#!/usr/bin/env bash
P=/home/vscode/.pg0/installation/18.1.0/bin/psql
export PGPASSWORD=hindsight
Q(){ $P -h /tmp -U hindsight -d hindsight -tAc "$1"; }

echo "--- 5 newest facts (primary) ---"
Q "SELECT to_char(created_at,'HH24:MI:SS') || '  ' || fact_type || '  ' || substring(text,1,120)
   FROM memory_units WHERE bank_id='termux-monorepo::primary' ORDER BY created_at DESC LIMIT 5;"
echo
echo "--- top 6 by proof_count (the formed observations) ---"
Q "SELECT 'proof=' || proof_count || '  ' || fact_type || '  ' || substring(text,1,120)
   FROM memory_units WHERE bank_id='termux-monorepo::primary' ORDER BY proof_count DESC LIMIT 6;"
echo
echo "--- observation_history, 5 newest (jsonb cast) ---"
Q "SELECT to_char(changed_at,'HH24:MI:SS') || '  ' || substring(content::text,1,120)
   FROM observation_history ORDER BY changed_at DESC LIMIT 5;" 2>&1
echo
echo "--- observation_history row count + bank split ---"
Q "SELECT bank_id || '  n=' || count(*) FROM observation_history GROUP BY bank_id ORDER BY count(*) DESC LIMIT 8;" 2>&1
echo
echo "--- memory_links, links by from_unit bank ---"
Q "SELECT m.bank_id || '  links=' || count(*) FROM memory_links l
   JOIN memory_units m ON m.id = l.from_unit_id GROUP BY m.bank_id ORDER BY count(*) DESC LIMIT 8;" 2>&1
echo
echo "--- entities top 10 ---"
Q "SELECT '  ' || canonical_name || '  n=' || count(*) FROM entities GROUP BY canonical_name ORDER BY count(*) DESC LIMIT 10;" 2>&1
echo
echo "--- entities per bank ---"
Q "SELECT bank_id || '  n=' || count(*) FROM entities GROUP BY bank_id ORDER BY count(*) DESC LIMIT 8;" 2>&1
