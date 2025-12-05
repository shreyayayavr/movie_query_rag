# movie_query_rag


##  Features

- Natural language querying over PostgreSQL
- LLM-based dynamic NL → SQL generation
- Semantic search using embeddings + ChromaDB
- Hybrid SQL + RAG query routing




-  **PostgreSQL (SQL)** for structured, numeric, and date-based queries  
-  **Chroma Vector DB (RAG)** for semantic, meaning-based search  

##   Data Flow

1. Movie data is stored in **PostgreSQL**  
2. Data is exported as **JSON**  
3. JSON data is embedded using **SentenceTransformers**  
4. Embeddings are stored in **ChromaDB**  
5. Queries are routed to:
   - SQL → for exact filters, ranking, and numeric conditions  
   - RAG → for semantic similarity and vague discovery 