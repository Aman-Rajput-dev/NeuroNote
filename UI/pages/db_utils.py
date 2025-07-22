import psycopg2
from psycopg2.extras import execute_values
import os

# Ideally load these from environment variables
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def insert_note_to_db(prompt, response, source_str, img_list):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO study_notes (prompt, response, source, img_list)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (prompt, response, source_str, img_list))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("Database insertion error:", e)
        return False

def fetch_all_notes():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        fetch_query = """
            SELECT prompt, response, source, img_list, timestamp
            FROM study_notes
            ORDER BY timestamp DESC
        """
        cursor.execute(fetch_query)
        notes = cursor.fetchall()
        cursor.close()
        conn.close()
        return notes  # List of tuples
    except Exception as e:
        print("Database fetch error:", e)
        return []
    
def fetch_filtered_notes(start_date=None, end_date=None, keyword=None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = """
            SELECT prompt, response, source, img_list, timestamp
            FROM study_notes
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND timestamp >= %s"
            params.append(start_date)

        if end_date:
            query += " AND timestamp <= %s"
            params.append(end_date)

        if keyword:
            query += " AND (LOWER(prompt) LIKE %s OR LOWER(response) LIKE %s)"
            kw = f"%{keyword.lower()}%"
            params.extend([kw, kw])

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        notes = cursor.fetchall()
        cursor.close()
        conn.close()
        return notes
    except Exception as e:
        print("Database fetch error:", e)
        return []

