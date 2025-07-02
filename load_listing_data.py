from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
cursor.execute("CREATE EXTENSION IF NOT EXISTS azure_ai;")
conn.commit()

cursor.execute(f"SELECT azure_ai.set_setting('azure_openai.endpoint', '{os.getenv('AZURE_OPENAI_ENDPOINT')}');")
cursor.execute(f"SELECT azure_ai.set_setting('azure_openai.subscription_key', '{os.getenv('AZURE_OPENAI_KEY')}');")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS all_listing_data AS
        (SELECT DISTINCT a.id, a.name, a.longitude, a.latitude, h.nearby_homicide_count, s.nearby_subway_count, a.room_type, a.price, a.neighbourhood 
        FROM nyc_listings_bnb a
        JOIN homicide_listings h ON h.name = a.name
        JOIN subway_listings s ON s.name = h.name)""")
conn.commit()
cursor.execute("ALTER TABLE all_listing_data ADD COLUMN IF NOT EXISTS description TEXT")
cursor.execute("ALTER TABLE all_listing_data ADD COLUMN IF NOT EXISTS embedding VECTOR(1536)")
conn.commit()

cursor.execute(f"""
    UPDATE all_listing_data AS a
    SET description = CONCAT('The listing id is ', a.id, '. The listing name is ', a.name, '. The listing longitude is ', a.longitude, '. The listing latitude is ', a.latitude, '. The listings nearby homicide count is ', a.nearby_homicide_count, '. The listing nearby subway count is ', a.nearby_subway_count, '. The listing room type is ', a.room_type, '. The listing price is ', a.price, '. The listing neighborhood is ', a.neighbourhood)
    WHERE description IS NULL;""")
conn.commit()

cursor.execute(f"""
            UPDATE all_listing_data
            SET embedding = azure_openai.create_embeddings('{os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")}', description, max_attempts => 5, retry_delay_ms => 500)
            WHERE embedding IS NULL""")
conn.commit()