"""Publication controls must filter data before any static upload."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow():
    return yaml.load((ROOT / '.github/workflows/help-wanted-dashboard-deploy.yml').read_text(), Loader=yaml.BaseLoader)


def test_pages_mirror_uploads_filtered_composite_and_replaces_stale_assets():
    job = workflow()['jobs']['user-site']
    steps = job['steps']
    prepare = next(s for s in steps if s.get('name') == 'Prepare Tribute subtree')
    command = prepare['run']
    assert 'scripts/quota_publication.py' in command
    assert '--config ops/quota/public-visibility.json' in command
    assert '--output _tribute/data/quota-public.json' in command
    assert '--observe-github' in command
    assert 'set -euo pipefail' in command
    assert command.index('cp -a apps/help-wanted-dashboard/.') < command.index('scripts/quota_publication.py')
    assert '_tribute/data/quota.json' in command and '_tribute/data/provider-quota-coverage.json' in command
    assert '_tribute/quota.txt' in command and 'rm -f' in command
    mirror = next(s for s in steps if s.get('name') == 'Mirror Tribute to /help-wanted/')
    assert steps.index(prepare) < steps.index(mirror)
    assert mirror['with']['keep_files'] == 'false'
    assert mirror['with']['destination_dir'] == 'help-wanted'


def test_owner_config_and_sources_trigger_existing_publication_without_new_schedule():
    triggers = workflow()['on']
    assert 'schedule' not in triggers
    paths = triggers['push']['paths']
    assert 'ops/quota/**' in paths
    assert 'scripts/quota_publication.py' in paths
    assert 'scripts/github_quota_manager.py' in paths


def test_optional_vercel_path_filters_before_deploy_and_removes_raw_copies():
    steps = workflow()['jobs']['vercel']['steps']
    filt = next(s for s in steps if s.get('name') == 'Apply quota visibility before optional Vercel publication')
    deploy = next(s for s in steps if s.get('name') == 'Deploy to Vercel (production)')
    assert steps.index(filt) < steps.index(deploy)
    assert '--output apps/help-wanted-dashboard/data/quota-public.json' in filt['run']
    assert 'rm -f apps/help-wanted-dashboard/data/quota.json' in filt['run']
