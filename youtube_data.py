from googleapiclient.discovery import build
import requests
from datetime import datetime
from config import apiKey

yt = build('youtube', 'v3', developerKey=apiKey)

def fetch_channel_and_video_data(custom_url):
    data_retrieved_today = {}
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={custom_url}&key={apiKey}'
    response = requests.get(url)
    data = response.json()
    
    if 'items' in data and len(data['items']) > 0:
        data_retrieved_today['channel_id'] = data['items'][0]['snippet']['channelId']
    else:
        data_retrieved_today['channel_id'] = None
    
    channel_id = data_retrieved_today['channel_id']
    if channel_id is None:
        print(f"Channel does not exist for URL: {custom_url}")
        return [], []
    
    request = yt.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()
    
    channel_stats = []
    for item in response['items']:
        channel_data = {
            'custom_channel_url': custom_url,
            'channel_id': item['id'],
            'channel_name': item['snippet']['title'],
            'view_Count': int(item['statistics']['viewCount']),
            'subscriber_Count': int(item['statistics']['subscriberCount']),
            'video_Count': int(item['statistics']['videoCount']),
            'playlist_id': item['contentDetails']['relatedPlaylists']['uploads'],
            'date_Ran': datetime.now().date()
        }
        channel_stats.append(channel_data)
    
    playlist_id = channel_data['playlist_id']
    
    video_ids = []
    request = yt.playlistItems().list(
        part="contentDetails",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    video_ids.extend([item['contentDetails']['videoId'] for item in response['items']])
    next_page_token = response.get('nextPageToken')
    while next_page_token:
        request = yt.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        video_ids.extend([item['contentDetails']['videoId'] for item in response['items']])
        next_page_token = response.get('nextPageToken')
    
    video_details_all = []
    for i in range(0, len(video_ids), 50):
        request = yt.videos().list(
            part="snippet,statistics",
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute()
        for video in response['items']:
            published_date = video['snippet']['publishedAt']
            published_date = datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%SZ')
            video_details = dict(
                VideoID=video['id'],
                VideoTitle=video['snippet']['title'],
                PublishedDate=published_date,
                ViewCount=int(video['statistics'].get('viewCount', 0)),
                LikeCount=int(video['statistics'].get('likeCount', 0)),
                FavoriteCount=int(video['statistics'].get('favoriteCount', 0)),
                CommentCount=int(video['statistics'].get('commentCount', 0)),
                ChannelName=channel_data['channel_name'],
                ChannelID=channel_data['channel_id'],
                PlaylistID=channel_data['playlist_id'],
                DateRan=datetime.now().date()
            )
            video_details_all.append(video_details)
    
    return channel_stats, video_details_all
