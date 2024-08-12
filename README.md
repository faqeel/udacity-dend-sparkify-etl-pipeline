# Sparkify ETL Pipeline

This project implements an ETL (Extract, Transform, Load) pipeline for Sparkify, a music streaming startup. The pipeline extracts data from S3, stages it in Redshift, and transforms it into a set of dimensional tables. This allows the analytics team to continue finding insights into what songs their users are listening to.

## How to Run

1. Configure AWS resources:
    - Set up a Redshift cluster
    - Create an IAM role with read access to S3
2. Update the `dwh.cfg` file with your Redshift cluster details and IAM role ARN.
3. Run the create_tables script to set up the database schema:

```sh
python create_tables.py
```

4. Run the ETL pipeline to process the data:

```sh
python etl.py
```

## Files in the Repository

- `create_tables.py`: Script to drop existing tables and create new tables.
- `etl.py`: Script to load data from S3 into staging tables on Redshift and then process that data into analytics tables.
- `sql_queries.py`: Contains all SQL queries used in the ETL process.

## Database Schema

### Fact Table

1. **songplays** - records in event data associated with song plays

### Dimension Tables

2. **users** - users in the app
3. **songs** - songs in music database
4. **artists** - artists in music database
5. **time** - timestamps of records in songplays broken down into specific units

## ETL Pipeline

1. Load data from S3 to staging tables on Redshift.
2. Transform data from staging tables to analytics tables on Redshift.

## Example Queries

Here are a few example queries to get started with analyzing the data:

1. Find the top 10 most played songs:

```sql
SELECT s.title, COUNT(*) as play_count
FROM songplays sp
JOIN songs s ON sp.song_id = s.song_id
GROUP BY s.title
ORDER BY play_count DESC
LIMIT 10;
```

2. Get the number of users by level:

```sql
SELECT level, COUNT(*) as user_count
FROM users
GROUP BY level;
```

3. Find the most active hours of the day:

```sql
SELECT t.hour, COUNT(*) as play_count
FROM songplays sp
JOIN time t ON sp.start_time = t.start_time
GROUP BY t.hour
ORDER BY play_count DESC;
```

These queries can help the analytics team start understanding user behavior and popular content on the Sparkify platform.