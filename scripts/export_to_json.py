import json
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=8081,
    database="movies_db",
    user="postgres",
    password="ShShvr@17776W"
)

cursor = conn.cursor()

cursor.execute("SELECT * FROM movies;")
rows = cursor.fetchall()

columns = [desc[0] for desc in cursor.description]

data = []
for row in rows:
    record = dict(zip(columns, row))
    data.append(record)

with open("movies.json", "w", encoding="utf-8") as f:
    json.dump(data, f, default=str, indent=2)

cursor.close()
conn.close()

print("Exported all records to movies.json")
