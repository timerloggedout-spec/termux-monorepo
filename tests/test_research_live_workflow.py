"""Static safety contracts; these are not production outcome observations."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow():
    return yaml.load((ROOT / '.github/workflows/continuous-evaluation.yml').read_text(), Loader=yaml.BaseLoader)


def test_live_mode_never_runs_the_legacy_broad_matrix():
    d = workflow()
    inputs = d['on']['workflow_dispatch']['inputs']
    assert inputs['live_mode']['default'] == 'catalog'
    assert inputs['live_mode']['options'] == ['catalog', 'preflight', 'pilot']
    assert inputs['task_pairs']['default'] == '2'
    assert "inputs.live_mode != 'preflight'" in d['jobs']['experiment']['if']
    assert "inputs.live_mode != 'pilot'" in d['jobs']['experiment']['if']
    live = d['jobs']['live-task-experiment']
    assert "github.event_name == 'workflow_dispatch'" in live['if']
    assert 'inputs.live_mode' in live['if']


def test_live_job_keeps_credentials_out_of_installs_and_artifacts():
    d = workflow()
    assert d['permissions'] == {'contents': 'read'}
    steps = d['jobs']['live-task-experiment']['steps']
    installs = [s for s in steps if 'pip install' in s.get('run', '')]
    assert installs and all('env' not in step for step in installs)
    run = next(s for s in steps if 'live_task_experiment' in s.get('run', ''))
    assert run['env']['OPENROUTER_API_KEY'] == '${{ secrets.OPENROUTER_API_KEY }}'
    assert '--pairs-per-context "$TASK_PAIRS"' in run['run']
    assert '--exclude-pr "$TARGET_NUMBER"' in run['run']
    upload = next(s for s in steps if s.get('uses', '').startswith('actions/upload-artifact@'))
    assert upload['with']['path'] == '/tmp/live-task-evidence'
    assert 'private' not in upload['with']['path']
    assert upload['if'] == 'always()'
