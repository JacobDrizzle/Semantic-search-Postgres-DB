import psycopg2
from dotenv import load_dotenv
import os
import requests

load_dotenv()

db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

hf_token = os.getenv('HFTOKEN')
embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

conn = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
cursor = conn.cursor()

# FUNCTION TO GENERATE EMBEDDINGS

def generate_embedding(text: str) -> list[float]:
    
   response = requests.post(
       embedding_url,
       headers={"Authorization": f"Bearer {hf_token}"},
       json={"inputs": text})
    
   if response.status_code != 200:
       raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")
   return response.json()

# END OF FUNCTION TO GENERATE EMBEDDINGS


sql_query = "SELECT movie_id, title, release_year, genre, description FROM movies;"
cursor.execute(sql_query)

# Fetch all movies
movies = cursor.fetchall()

# Function to create embedings for each 'description' in the Movies DB
for movie in movies:
    movie_id, title, release_year, genre, description = movie
    embedding = generate_embedding(description)

    # Insert movie data and embeddings into the new table
    cursor.execute("""
        INSERT INTO Movie_Embeddings(movie_id, title, release_year, genre, description, embeddings)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (movie_id) DO UPDATE SET 
        title = EXCLUDED.title,
        release_year = EXCLUDED.release_year, 
        genre = EXCLUDED.genre, 
        description = EXCLUDED.description, 
        embeddings = EXCLUDED.embeddings;
    """, (movie_id, title, release_year, genre, description, embedding))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()