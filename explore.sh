#!/bin/bash
echo "=== Directory trees (maxdepth 3) ==="
for d in ~/deepseek-cli ~/deepcli ~/deepcli-tui ~/deepseek_harvest_work ~/termux-multi-agent; do
  [ -d "$d" ] && find "$d" -maxdepth 3 -not -path '*/node_modules/*' -not -path '*/.cache/*' -not -path '*/.git/*' | sort
done

echo "=== Key package/config files ==="
for f in \
  ~/deepseek-cli/package.json \
  ~/deepcli/package.json \
  ~/deepcli-tui/package.json \
  ~/deepseek_harvest_work/package.json \
  ~/termux-multi-agent/package.json \
  ~/deepseek-cli/Cargo.toml \
  ~/deepcli/Cargo.toml \
  ~/deepcli-tui/Cargo.toml \
  ~/termux-multi-agent/Cargo.toml \
  ~/deepseek-cli/pyproject.toml \
  ~/deepcli/pyproject.toml \
  ~/deepcli-tui/pyproject.toml \
  ~/termux-multi-agent/pyproject.toml
do
  [ -f "$f" ] && printf '\n--- %s ---\n' "$f" && cat "$f"
done

echo "=== Session/conversation references ==="
grep -rn "session\|conversation" \
  ~/deepseek-cli/ ~/deepcli/ ~/deepcli-tui/ ~/deepseek_harvest_work/ ~/termux-multi-agent/ \
  --include="*.py" --include="*.js" --include="*.ts" --include="*.rs" --include="*.sh" --include="*.json" \
  2>/dev/null | head -60

echo "=== Token / cookies / API key references ==="
grep -rn "token\|cookies\|api_key\|API_KEY\|authorization" \
  ~/deepseek-cli/ ~/deepcli/ ~/deepcli-tui/ ~/deepseek_harvest_work/ ~/termux-multi-agent/ \
  --include="*.py" --include="*.js" --include="*.ts" --include="*.rs" --include="*.sh" --include="*.json" \
  2>/dev/null | head -60

echo "=== Export / download / storage references ==="
grep -rn "export\|download\|storage\|Downloads" \
  ~/deepseek-cli/ ~/deepcli/ ~/deepcli-tui/ ~/deepseek_harvest_work/ ~/termux-multi-agent/ \
  --include="*.py" --include="*.js" --include="*.ts" --include="*.rs" --include="*.sh" --include="*.json" \
  2>/dev/null | head -60

echo "=== deepseek_harmonizer.sh ==="
[ -f ~/deepseek_harmonizer.sh ] && cat ~/deepseek_harmonizer.sh

echo "=== Recent file: termux-multi-agent (top-level listing) ==="
if [ -d ~/termux-multi-agent ]; then
  ls -la ~/termux-multi-agent/
  find ~/termux-multi-agent -maxdepth 2 -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | sort
fi
