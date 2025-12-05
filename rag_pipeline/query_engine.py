import os
import psycopg2
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from dotenv import load_dotenv
import re

load_dotenv()
BASE_DIR = r"C:\Users\Shreya\PycharmProjects\movie_query_rag"
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to Chroma (RAG)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("movies")

# Connect to PostgreSQL (SQL)
pg_conn = psycopg2.connect(
    host="localhost",
    database="movies_db",
    user="postgres",
    password="ShShvr@17776W",
    port="8081"
)
pg_cursor = pg_conn.cursor()

# Connect to Groq (LLM for NL → SQL)
client_llm = Groq(api_key=os.getenv("GROQ_API_KEY"))

#NL to SQL

def nl_to_sql(user_query: str):
    prompt = f"""
You are a PostgreSQL SQL generator.

Table:
movies(id, title, director, release_date, money_made)

MANDATORY RULES:
- ALWAYS select: title, director, release_date, money_made
- NEVER select only one column
- Output ONLY SQL
- No explanations
- Use EXTRACT(YEAR FROM release_date) for year filters
- Use ORDER BY money_made DESC for ranking
- Use LIMIT if user asks for top N

User Question:
{user_query}

SQL:
"""

    response = client_llm.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    # ✅ Safety fallback: force full select if LLM messes up
    if "select" in sql.lower() and "money_made" not in sql.lower():
        sql = sql.replace(
            sql.split("from")[0],
            "SELECT title, director, release_date, money_made "
        )

    return sql

def run_sql_query_llm(user_query: str):
    sql = nl_to_sql(user_query)

    print("\nGenerated SQL:\n", sql)

    #blocked queries
    forbidden = ["drop", "delete", "truncate", "update", "insert"]
    if any(word in sql.lower() for word in forbidden):
        return "Unsafe SQL blocked."

    try:
        pg_cursor.execute(sql)
        results = pg_cursor.fetchall()
    except Exception as e:
        return f"SQL Execution Error: {e}"

    if not results:
        return "No results found."

    formatted = []
    for row in results:
        title = row[0]
        director = row[1] if len(row) > 1 else "N/A"
        release_date = row[2] if len(row) > 2 else "N/A"
        money = row[3] if len(row) > 3 else "N/A"

        formatted.append(
            f"""
    Title: {title}
    Director: {director}
    Release Date: {release_date}
    Money Made (USD): {money}
    """
        )

    return "\n\n---\n\n".join(formatted)

#RAG for semantic search
def run_rag_query(query: str):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    docs = results["documents"][0]
    return "\n\n---\n\n".join(docs)

#hybrid router
def detect_query_type_llm(user_query: str):
    prompt = f"""
You are a classifier.

Decide whether the user query needs:
- SQL (exact filtering, dates, numbers, top N)
OR
- RAG (semantic similarity, vague search)

Reply with ONLY ONE WORD:
SQL or RAG

User Query:
{user_query}

Answer:
"""

    response = client_llm.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    decision = response.choices[0].message.content.strip().upper()
    return decision

def hybrid_query_router(query: str):
    q = query.lower()

    numeric_patterns = [
        r"less than",
        r"more than",
        r"greater than",
        r"below",
        r"above",
        r"\b\d+\b",   # any number present
    ]
    if any(re.search(p, q) for p in numeric_patterns):
        print("\nForced Routing to **SQL Engine (Numeric Rule Override)**...")
        return run_sql_query_llm(query)

    # Otherwise let LLM decide
    decision = detect_query_type_llm(query)

    print(f"\nLLM Routing Decision: {decision}")

    if decision == "SQL":
        print("Routing to **LLM-Powered SQL Engine**...")
        return run_sql_query_llm(query)
    else:
        print("Routing to **RAG Engine (Semantic Search)**...")
        return run_rag_query(query)

#user loop

if __name__ == "__main__":
    while True:
        user_query = input("\nAsk a movie question (or type exit): ")

        if user_query.lower() == "exit":
            break

        answer = hybrid_query_router(user_query)
        print("\nAnswer:")
        print(answer)
