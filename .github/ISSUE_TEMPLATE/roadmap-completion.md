---
name: Roadmap Completion
about: Track completion of a roadmap exercise for repository qualifications
labels: roadmap, completion, enhancement
title: "[ROADMAP] [EXERCISE]: Completion"
---

## 🎯 Roadmap Exercise Completion

**This issue tracks completion of a roadmap exercise for `termux-monorepo` repository qualifications.**

### 📋 Exercise Details

- **Roadmap:** `[e.g., mlops, ai-engineer, nvidia]`
- **Exercise:** `[e.g., implement-ml-pipeline, cuda-basics]`
- **Priority:** `[high/medium/low]` (based on tier)
- **Tags:** `[comma-separated, e.g., ml, ai, pipeline, gpu]`
- **Phase:** `[PHASE 2, PHASE 3, etc.]`

### 📊 Completion Status

- [ ] ✅ Exercise code completed
- [ ] ✅ Tests written and passing (min coverage: varies by exercise)
- [ ] ✅ Documentation created (min words: varies by exercise)
- [ ] ✅ Portfolio repository linked (if applicable)
- [ ] ✅ Evidence verified by GitHub Actions
- [ ] ✅ Badge awarded
- [ ] ✅ README.md updated

### 📁 Evidence Links

- **Code:** `[path to code file(s)]`
- **Tests:** `[path to test file(s)]`
- **Documentation:** `[path to documentation]`
- **Portfolio Repo:** `[URL to portfolio repository]`
- **Evidence File:** `[path to evidence.json]`

### 🔍 Verification

**Verification Criteria:**
```yaml
# Example for MLOps - Implement ML Pipeline
code:
  required: true
  min_size: 500 bytes
  patterns: ["def train", "def evaluate", "def predict"]
test:
  required: true
  min_coverage: 80%
documentation:
  required: true
  min_words: 500
  sections: ["Overview", "Pipeline Stages", "Usage", "Deployment"]
portfolio:
  required: true
  required_files: ["README.md", "LICENSE", "requirements.txt", "Dockerfile"]
```

**Verification Command:**
```bash
python roadmap-completions/scripts/verify-completion.py --roadmap mlops --exercise implement-ml-pipeline
```

### 📝 Notes

[Additional notes about the completion, challenges faced, solutions implemented, etc.]

---

## 🤖 Automation

The `roadmap-completion.yml` workflow validates the submitted evidence and posts a result on this issue.

**Triggers:**
- Issue opened, edited, reopened, or labeled after `roadmap:{roadmap}` and `exercise:{exercise}` labels are present
- Push of the matching `evidence.json` under `roadmap-completions/roadmaps/{roadmap}/exercises/{exercise}/`

The verifier checks configured evidence paths, code size/extensions/patterns, submitted test-result metadata, documentation word counts/sections, and required local portfolio files. It records verification status in the workflow run and comments on the matching issue. The verifier validates submitted test metadata and evidence files; exercise test commands run in their owning project workflow.

Badge generation, README publication, and issue closure follow as explicit publication steps after evidence verification.

---

## 📚 References

- [Repository Roadmap Completion Framework](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/REPO-ROADMAP-COMPLETION-FRAMEWORK.md)
- [Priorities Configuration](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/roadmap-completions/config/priorities.json)
- [Verification Rules](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/roadmap-completions/config/verification-rules.yaml)

---

## 🎯 Next Steps

1. Complete the exercise code
2. Write tests (if required)
3. Create documentation (if required)
4. Link portfolio repository (if required)
5. Create evidence.json file
6. Push changes to trigger verification
7. Badge will be awarded automatically

---

**Label this issue with:** `roadmap:{roadmap}`, `exercise:{exercise}`, `priority:{priority}`
