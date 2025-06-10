-- Enable the pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    content_type TEXT NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document chunks table
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding_vector vector(768), -- Gemini text-embedding-004 dimension
    model_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_processed ON documents(processed);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_chunk_index ON document_chunks(document_id, chunk_index);
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id);

-- Create vector similarity search index (this may take a while for large datasets)
CREATE INDEX IF NOT EXISTS embeddings_vector_idx ON embeddings USING ivfflat (embedding_vector vector_cosine_ops);

-- Function for similarity search
CREATE OR REPLACE FUNCTION similarity_search(
    query_embedding vector(768),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    chunk_id int,
    document_id int,
    chunk_text text,
    page_number int,
    similarity float,
    title text,
    filename text
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN query
    SELECT 
        dc.id as chunk_id,
        dc.document_id,
        dc.chunk_text,
        dc.page_number,
        (1 - (e.embedding_vector <=> query_embedding)) as similarity,
        d.title,
        d.filename
    FROM embeddings e
    JOIN document_chunks dc ON e.chunk_id = dc.id
    JOIN documents d ON dc.document_id = d.id
    WHERE (1 - (e.embedding_vector <=> query_embedding)) > match_threshold
    ORDER BY e.embedding_vector <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to get document statistics
CREATE OR REPLACE FUNCTION get_document_stats()
RETURNS TABLE (
    total_documents bigint,
    processed_documents bigint,
    total_chunks bigint,
    total_embeddings bigint
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN query
    SELECT 
        (SELECT COUNT(*) FROM documents) as total_documents,
        (SELECT COUNT(*) FROM documents WHERE processed = true) as processed_documents,
        (SELECT COUNT(*) FROM document_chunks) as total_chunks,
        (SELECT COUNT(*) FROM embeddings) as total_embeddings;
END;
$$;

-- Row Level Security (RLS) policies can be added here if needed
-- For this prototype, we'll keep it simple

-- Grant necessary permissions (adjust based on your Supabase setup)
-- These might not be necessary depending on your Supabase configuration
-- GRANT USAGE ON SCHEMA public TO anon, authenticated;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated; 