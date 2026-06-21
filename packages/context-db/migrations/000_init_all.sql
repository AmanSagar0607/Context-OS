-- Combined migration: runs on first DB start
\i /docker-entrypoint-initdb.d/001_core.sql
\i /docker-entrypoint-initdb.d/002_memory.sql
\i /docker-entrypoint-initdb.d/003_knowledge.sql
\i /docker-entrypoint-initdb.d/004_subscriptions.sql
