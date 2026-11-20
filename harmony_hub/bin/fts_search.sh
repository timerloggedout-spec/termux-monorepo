#!/bin/bash
# synthegration search bridge -> FTS5
# Usage: fts_search.sh "term"
DB=~/termux-multi-agent/local_repo.db
TERM="${1:?}"
sqlite3 "$DB" "SELECT snippet(messages_fts, 0, '<b>', '</b>', '…', 40) FROM messages_fts WHERE content MATCH '$TERM' LIMIT 10;"
