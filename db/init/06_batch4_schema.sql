-- 06_batch4_schema.sql   (GeoRAG+ Batch 4)
-- Location in repo: db/init/06_batch4_schema.sql
-- Idempotent. Extends regulation_chunks (created in Batch 1) for RAG.

ALTER TABLE regulation_chunks ADD COLUMN IF NOT EXISTS doc_code   VARCHAR(30);   -- KPBR | KMBR | PADDY_ACT ...
ALTER TABLE regulation_chunks ADD COLUMN IF NOT EXISTS doc_title  TEXT;
ALTER TABLE regulation_chunks ADD COLUMN IF NOT EXISTS page_start INT;
ALTER TABLE regulation_chunks ADD COLUMN IF NOT EXISTS chunk_index INT;
ALTER TABLE regulation_chunks ADD COLUMN IF NOT EXISTS applies_to VARCHAR(30);   -- panchayat | municipality | all

-- Keyword search column (legal text has exact rule numbers and terms,
-- so we combine this with vector search = hybrid retrieval)
ALTER TABLE regulation_chunks ADD COLUMN IF NOT EXISTS content_tsv tsvector
  GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(clause_ref, '') || ' ' || coalesce(content, ''))
  ) STORED;

CREATE INDEX IF NOT EXISTS reg_tsv_idx ON regulation_chunks USING GIN (content_tsv);
CREATE INDEX IF NOT EXISTS reg_doc_idx ON regulation_chunks (doc_code);
-- The HNSW vector index (reg_embed_idx) already exists from 02_schema.sql