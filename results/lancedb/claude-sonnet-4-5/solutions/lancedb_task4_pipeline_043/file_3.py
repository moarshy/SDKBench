# Ingest documents
   docs = [{"text": "Your document text"}]
   ingest_documents(docs)
   
   # Search
   results = search("your query", k=5)
   
   # Full pipeline
   result = run_pipeline("your query")