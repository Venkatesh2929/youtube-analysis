import mysql.connector
from config import db_config

def create_tables():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    table_create_channel_stats = """
    CREATE TABLE IF NOT EXISTS channel_stats (
        custom_channel_url VARCHAR(255),
        channel_id VARCHAR(255),
        channel_name VARCHAR(255),
        view_Count INT,
        subscriber_Count INT,
        video_Count INT,
        playlist_id VARCHAR(255),
        date_Ran DATE,
        PRIMARY KEY (channel_id, date_Ran)
    );
    """

    table_create_video_stats = """
    CREATE TABLE IF NOT EXISTS video_details (
        VideoID VARCHAR(255),
        VideoTitle VARCHAR(255),
        PublishedDate DATETIME,
        ViewCount INT,
        LikeCount INT,
        FavoriteCount INT,
        CommentCount INT,
        ChannelName VARCHAR(255),
        ChannelID VARCHAR(255),
        PlaylistID VARCHAR(255),
        DateRan DATE,
        PRIMARY KEY (VideoID, DateRan)
    );
    """

    cursor.execute(table_create_channel_stats)
    cursor.execute(table_create_video_stats)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
