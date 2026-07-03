-- Run this once in the Supabase SQL editor (Project -> SQL Editor -> New query).
-- Sets up the table that holds embedded chunks of the Smooth knowledge base.

create extension if not exists vector;

create table if not exists smooth_chunks (
    id bigint generated always as identity primary key,
    section text not null,
    content text not null,
    embedding vector(768)
);

-- Similarity search function used by the backend.
create or replace function match_smooth_chunks (
    query_embedding vector(768),
    match_count int default 12
)
returns table (
    id bigint,
    section text,
    content text,
    similarity float
)
language sql stable
as $$
    select
        id,
        section,
        content,
        1 - (smooth_chunks.embedding <=> query_embedding) as similarity
    from smooth_chunks
    order by smooth_chunks.embedding <=> query_embedding
    limit match_count;
$$;
