import mysql.connector
from config import db_config
from datetime import datetime
import json
import string

# Hardcoded test values
channel = 'PCS Global'
date_from = '2024-06-28'
date_to = '2024-07-03'
metric = 'video_view_Count'  # Make sure this matches the actual field name in your database

# Convert dates to the correct format
date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
date_to = datetime.strptime(date_to, '%Y-%m-%d').date()

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)

# Initialize stats list to hold the final result
stats = []

if metric in ["view_Count", "subscriber_Count", "video_Count"]:
    query = """
    SELECT * FROM channel_stats 
    WHERE channel_name = %s AND date_Ran BETWEEN %s AND %s
    """
    cursor.execute(query, (channel, date_from, date_to))
    stats = cursor.fetchall()
else:
    # Step 1: Retrieve the top 10 most viewed videos as of the latest date
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

    print(top_videos)
    
    # Step 2: Assign a letter to each video
    letter_mapping = {video['VideoID']: letter for video, letter in zip(top_videos, string.ascii_uppercase)}

    # Step 3: For each video, retrieve the details within the date range and add the assigned letter
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

cursor.close()
conn.close()

# Save the data to a JSON file similar to what jsonify would return
with open('output.json', 'w') as f:
    json.dump(stats, f, indent=4, default=str)

print("Output written to output.json")
