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

query_embedding = generate_embedding("Team of explorers.")
query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

cursor.execute("""
    SELECT title
    FROM Movie_Embeddings
    ORDER BY embeddings <-> %s::vector  -- Cast the string to vector
    LIMIT 10;
""", (query_embedding_str,)) 

results = cursor.fetchall()

for result in results:
    print(result[0])  # Assuming that 'title' is the first column in the SELECT statement

# Close the cursor and connection
cursor.close()
conn.close()