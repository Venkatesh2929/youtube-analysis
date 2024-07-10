import mysql.connector
from config import db_config

def insert_channel_stats(channel_stats, cursor):
    insert_channel_stats_query = """
    INSERT INTO channel_stats (custom_channel_url, channel_id, channel_name, view_Count, subscriber_Count, video_Count, playlist_id, date_Ran)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
    view_Count = VALUES(view_Count), 
    subscriber_Count = VALUES(subscriber_Count),
    video_Count = VALUES(video_Count)
    """
    for stats in channel_stats:
        cursor.execute(insert_channel_stats_query, (
            stats['custom_channel_url'],
            stats['channel_id'],
            stats['channel_name'],
            stats['view_Count'],
            stats['subscriber_Count'],
            stats['video_Count'],
            stats['playlist_id'],
            stats['date_Ran']
        ))

def insert_video_details(video_details_all, cursor):
    insert_video_details_query = """
    INSERT INTO video_details (VideoID, VideoTitle, PublishedDate, ViewCount, LikeCount, FavoriteCount, CommentCount, ChannelName, ChannelID, PlaylistID, DateRan)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
    ViewCount = VALUES(ViewCount), 
    LikeCount = VALUES(LikeCount),
    FavoriteCount = VALUES(FavoriteCount),
    CommentCount = VALUES(CommentCount)
    """
    for video in video_details_all:
        cursor.execute(insert_video_details_query, (
            video['VideoID'],
            video['VideoTitle'],
            video['PublishedDate'],
            video['ViewCount'],
            video['LikeCount'],
            video['FavoriteCount'],
            video['CommentCount'],
            video['ChannelName'],
            video['ChannelID'],
            video['PlaylistID'],
            video['DateRan']
        ))
