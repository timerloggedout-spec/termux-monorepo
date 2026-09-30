#!/data/data/com.termux/files/usr/bin/bash
# commit-msg: Conventional Commits + DO Framework enforcement
_msg_file="$1"
_subj=$(head -1 "$_msg_file")

case "$_subj" in
  Revert*|Merge*|fixup*|squash*|Initial*) exit 0 ;;
esac

if ! printf '%s' "$_subj" | grep -qE '^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert)(\([^)]+\))?!?: .+'; then
  echo "commit-msg: enforce Conventional Commits - type(scope)!: subject"
  echo "  got: $_subj"
  exit 1
fi

if printf '%s' "$_subj" | grep -Eqi "\b(don't|do not|never|avoid|cannot|won't|no more)\b"; then
  echo "commit-msg: rewrite as affirmative directive (docs/STANDARDS/DO-FRAMEWORK.md section 2)"
  exit 1
fi

exit 0
