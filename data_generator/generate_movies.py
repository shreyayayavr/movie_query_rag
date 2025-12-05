from faker import Faker
import random
import psycopg2

fake = Faker()

conn = psycopg2.connect(
    host="localhost",
    port=8081,
    database="movies_db",
    user="postgres",
    password="ShShvr@17776W"
)

cursor = conn.cursor()

insert_query = """
INSERT INTO movies (title, director, release_date, money_made)
VALUES (%s, %s, %s, %s)
"""

for i in range(10000):
    title = fake.sentence(nb_words=3).replace(".", "")
    director = fake.name()
    release_date = fake.date_between(start_date='-20y', end_date='today')
    money_made = random.randint(1_000_000, 500_000_000)

    cursor.execute(insert_query, (title, director, release_date, money_made))

    if i % 1000 == 0:
        conn.commit()
        print(f"Inserted {i} records")

conn.commit()
cursor.close()
conn.close()

print("10,000 records inserted successfully!")
