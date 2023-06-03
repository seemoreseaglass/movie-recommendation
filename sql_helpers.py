import pymysql
from google.cloud.sql.connector import Connector

# Function to return the database connection
def getconn() -> pymysql.connections.Connection:
    with Connector() as connector:
        conn: pymysql.connections.Connection = connector.connect(
            "movie-recommendation-386906:asia-northeast1:movie-recommendation",
            "pymysql",
            user="root",
            password="123",
            db="imdb",
            local_infile=True
        )
        return conn