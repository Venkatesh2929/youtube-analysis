from flask import Flask, render_template, request, jsonify
import mysql.connector
from config import db_config
from youtube_data import fetch_channel_and_video_data
from database_operations import insert_channel_stats, insert_video_details
from datetime import datetime
import string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    try:
        custom_channel_urls = request.json['channels']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        for url in custom_channel_urls:
            channel_stats, video_details_all = fetch_channel_and_video_data(url)
            insert_channel_stats(channel_stats, cursor)
            insert_video_details(video_details_all, cursor)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/get_channels')
def get_channels():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT DISTINCT channel_name FROM channel_stats"
    cursor.execute(query)
    channels = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(channels)

@app.route('/get_dates/<channel>')
def get_dates(channel):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT DISTINCT date_Ran FROM channel_stats WHERE channel_name = %s"
    cursor.execute(query, (channel,))
    dates = cursor.fetchall()
    
    # Debugging: Print the fetched dates
    print("Fetched dates from database:", dates)
    
    # Convert dates to string format
    formatted_dates = [{'date_Ran': date['date_Ran'].strftime('%Y-%m-%d')} for date in dates]
    
    # Debugging: Print the formatted dates
    print("Formatted dates to strings:", formatted_dates)
    
    cursor.close()
    conn.close()
    
    return jsonify(formatted_dates)

@app.route('/get_data_range', methods=['POST'])
def get_data_range():
    data = request.json
    channel = data['channel']
    date_from = data['date_from']
    date_to = data['date_to']
    metric = data['metric']

    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if metric in ["view_Count", "subscriber_Count", "video_Count"]:
        query = """
        SELECT * FROM channel_stats 
        WHERE channel_name = %s AND date_Ran BETWEEN %s AND %s
        """
        cursor.execute(query, (channel, date_from, date_to))
        stats = cursor.fetchall()
    else:
        stats = []
        query1 = """
            SELECT VideoID, VideoTitle
            FROM video_details
            WHERE ChannelName = %s AND DateRan = (
                SELECT MAX(DateRan)
                FROM video_details
                WHERE ChannelName = %s
            )
            ORDER BY ViewCount DESC
            LIMIT 10
        """
        cursor.execute(query1, (channel, channel))
        top_videos = cursor.fetchall()

        letter_mapping = {video['VideoID']: letter for video, letter in zip(top_videos, string.ascii_uppercase)}

        query2 = """
            SELECT *
            FROM video_details
            WHERE VideoID = %s AND DateRan BETWEEN %s AND %s
        """
        for video in top_videos:
            video_id = video['VideoID']
            letter = letter_mapping[video_id]
            cursor.execute(query2, (video_id, date_from, date_to))
            details = cursor.fetchall()
            for detail in details:
                detail['Letter'] = letter
            stats.extend(details)

    print("Retrieved Stats:", stats)  # Debugging: Print the retrieved stats
    
    cursor.close()
    conn.close()

    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True)
