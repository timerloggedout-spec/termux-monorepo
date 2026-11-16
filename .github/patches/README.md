# iOS-Termux Contribution Patches

This directory contains patch files for contributing to external repositories.

## Available Patches

### ios-termux-contribution.patch
- **Target:** credkellar/iOS-Termux
- **Changes:** 
  - Add 22 new command translations (43 total, was 21)
  - Add 4 new path translations (9 total, was 5)
  - Add 30 new comprehensive tests (73 total, was 43)
- **Status:** Ready for submission
- **PR Title:** "Enhance translations: add 22 new command pairs and 4 new path mappings"

## How to Use

### Option 1: Use the Workflow (Recommended)

Trigger the workflow from termux-monorepo:

```bash
# From termux-monorepo directory
gh workflow run ios-termux-contribute.yml \
  --field target_repo="credkellar/iOS-Termux" \
  --field base_branch="main" \
  --field pr_title="Enhance translations: add 22 new command pairs and 4 new path mappings"
```

Or via GitHub UI:
1. Go to: https://github.com/timerloggedout-spec/termux-monorepo/actions
2. Select "iOS-Termux Contribute" workflow
3. Click "Run workflow"
4. Use default values or customize
5. Click "Run workflow"

### Option 2: Manual Application

```bash
# Clone the target repo
git clone https://github.com/credkellar/iOS-Termux.git
cd iOS-Termux

# Create a branch
git checkout -b contribution-enhancements

# Apply the patch
git apply .github/patches/ios-termux-contribution.patch

# Commit
git add -A
git commit -m "Enhance translations: add 22 new command pairs and 4 new path mappings"

# Push to your fork and create PR
git push origin contribution-enhancements
# Then create PR via GitHub UI
```

## Patch Details

### Command Translations Added (22 new):
- Package management: `pkg upgrade`, `apt upgrade`, `pkg remove`, `pkg search`, `dpkg -l`, `apt search`
- File operations: `xdg-open`
- Clipboard: `termux-clipboard-set {text}`
- TTS: `termux-tts-stop`
- Downloads: `termux-download`, `termux-download --timeout`
- Android-specific: `termux-vibrate`, `termux-notification`, `termux-camera-photo`, `termux-sensor`

### Path Translations Added (4 new):
- `~/storage/external-1` ↔ `On My iPhone`
- `/sdcard` ↔ `On My iPhone`
- `/storage/emulated/0` ↔ `On My iPhone`
- `/storage/emulated/0/Download` ↔ `On My iPhone/Download`

### Tests Added (30 new):
- All new translations tested
- Injection protection verified
- Bidirectional consistency checked
- Edge cases covered

## Verification

Before submitting, verify:
- ✅ All 73 tests pass (`python3 -m pytest tests/ -v`)
- ✅ All 48 checks pass (`python3 main.py`)
- ✅ No breaking changes
- ✅ 100% backward compatible

## Related Files

- **Workflow:** `.github/workflows/ios-termux-contribute.yml`
- **Integration Lane:** `_1-Projects/ios-termux/`
- **Integration Plan:** `/workspace/pr-submission/INTEGRATION-PLAN.md`

## Support

For questions or issues:
- **Upstream:** https://github.com/credkellar/iOS-Termux
- **This Repo:** https://github.com/timerloggedout-spec/termux-monorepo
- **Task ID:** f599f5e8-9209-470a-970a-78932a08db07
