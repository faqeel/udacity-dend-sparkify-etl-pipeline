import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE staging_events (
    event_id INT IDENTITY(0,1),
    artist_name VARCHAR(255),
    auth VARCHAR(50),
    user_first_name VARCHAR(255),
    user_gender  VARCHAR(1),
    item_in_session	INTEGER,
    user_last_name VARCHAR(255),
    song_length	DOUBLE PRECISION, 
    user_level VARCHAR(50),
    location VARCHAR(255),	
    method VARCHAR(25),
    page VARCHAR(35),	
    registration VARCHAR(50),	
    session_id	BIGINT,
    song_title VARCHAR(255),
    status INTEGER, 
    ts BIGINT,
    user_agent TEXT,	
    user_id VARCHAR(100),
    PRIMARY KEY (event_id)
)
""")

staging_songs_table_create = ("""
CREATE TABLE staging_songs (
    num_songs INTEGER,
    artist_id VARCHAR(100),
    artist_latitude DOUBLE PRECISION,
    artist_longitude DOUBLE PRECISION,
    artist_location VARCHAR(255),
    artist_name VARCHAR(255),
    song_id VARCHAR(100),
    title VARCHAR(255),
    duration DOUBLE PRECISION,
    year INTEGER,
    PRIMARY KEY (song_id)
)
""")

songplay_table_create = ("""
CREATE TABLE songplays (
    songplay_id INT IDENTITY(0,1),
    start_time TIMESTAMP,
    user_id VARCHAR(100),
    level VARCHAR(50),
    song_id VARCHAR(100),
    artist_id VARCHAR(100),
    session_id BIGINT,
    location VARCHAR(255),
    user_agent TEXT,
    PRIMARY KEY (songplay_id)
)
""")

user_table_create = ("""
CREATE TABLE users (
    user_id VARCHAR(100),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    gender VARCHAR(1),
    level VARCHAR(50),
    PRIMARY KEY (user_id)
)
""")

song_table_create = ("""
CREATE TABLE songs (
    song_id VARCHAR(100),
    title VARCHAR(255),
    artist_id VARCHAR(100),
    year INTEGER,
    duration DOUBLE PRECISION,
    PRIMARY KEY (song_id)
)
""")

artist_table_create = ("""
CREATE TABLE artists (
    artist_id VARCHAR(100),
    name VARCHAR(255),
    location VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    PRIMARY KEY (artist_id)
)
""")

time_table_create = ("""
CREATE TABLE time (
    start_time TIMESTAMP,
    hour INTEGER,
    day INTEGER,
    week INTEGER,
    month INTEGER,
    year INTEGER,
    weekday VARCHAR(20),
    PRIMARY KEY (start_time)
)
""")

# STAGING TABLES

staging_events_copy = ("""
COPY staging_events FROM {}
IAM_ROLE {}
FORMAT AS JSON {}
REGION 'us-west-2';
""").format(config['S3']['LOG_DATA'], config['IAM_ROLE']['ARN'], config['S3']['LOG_JSONPATH'])

staging_songs_copy = ("""
COPY staging_songs FROM {}
IAM_ROLE {}
FORMAT AS JSON 'auto'
REGION 'us-west-2';
""").format(config['S3']['SONG_DATA'], config['IAM_ROLE']['ARN'])

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT DISTINCT
    TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second' AS start_time,
    se.user_id,
    se.user_level,
    ss.song_id,
    ss.artist_id,
    se.session_id,
    se.location,
    se.user_agent
FROM staging_events se
JOIN staging_songs ss ON se.song_title = ss.title AND se.artist_name = ss.artist_name
WHERE se.page = 'NextSong'
""")

user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
SELECT DISTINCT 
    user_id,
    user_first_name,
    user_last_name,
    user_gender,
    user_level
FROM staging_events
WHERE user_id IS NOT NULL
ON CONFLICT (user_id) DO UPDATE SET level = EXCLUDED.level
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT DISTINCT 
    song_id,
    title,
    artist_id,
    year,
    duration
FROM staging_songs
WHERE song_id IS NOT NULL
ON CONFLICT (song_id) DO NOTHING
""")

artist_table_insert = ("""
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT 
    artist_id,
    artist_name,
    artist_location,
    artist_latitude,
    artist_longitude
FROM staging_songs
WHERE artist_id IS NOT NULL
ON CONFLICT (artist_id) DO UPDATE SET
    name = EXCLUDED.name,
    location = EXCLUDED.location,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude
""")

time_table_insert = ("""
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
SELECT DISTINCT 
    start_time,
    EXTRACT(hour FROM start_time),
    EXTRACT(day FROM start_time),
    EXTRACT(week FROM start_time),
    EXTRACT(month FROM start_time),
    EXTRACT(year FROM start_time),
    EXTRACT(weekday FROM start_time)
FROM songplays
ON CONFLICT (start_time) DO NOTHING
FROM songplays
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
