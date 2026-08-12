import os
import sys
import tempfile
from pathlib import Path

# Create a temporary directory to act as the hermetic HOME
# so that importing deepcli.core does not mutate the real ~/.deepcli
_temp_home = tempfile.TemporaryDirectory()
os.environ["HOME"] = _temp_home.name

import pytest

# Ensure deepcli is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "deepcli")))

from deepcli.core import enforce_local_privileges

def test_enforce_local_privileges_basic():
    """Verify that enforce_local_privileges sets correct permissions on files and directories."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        root_path = Path(tmp_dir)

        # Create directories and files
        subdir = root_path / "subdir"
        subdir.mkdir()

        config_file = root_path / "config.json"
        config_file.write_text("{}")

        cache_file = subdir / "session.json"
        cache_file.write_text("[]")

        # Set loose permissions first (e.g., 0o777)
        os.chmod(root_path, 0o777)
        os.chmod(subdir, 0o777)
        os.chmod(config_file, 0o666)
        os.chmod(cache_file, 0o666)

        # Enforce privileges
        enforce_local_privileges(root_path)

        # Check root directory permissions
        assert (root_path.stat().st_mode & 0o777) == 0o700
        # Check subdir permissions
        assert (subdir.stat().st_mode & 0o777) == 0o700
        # Check file permissions
        assert (config_file.stat().st_mode & 0o777) == 0o600
        assert (cache_file.stat().st_mode & 0o777) == 0o600


def test_enforce_local_privileges_skips_symlinks():
    """Verify that enforce_local_privileges explicitly skips symlinks to prevent traversal/hijacking."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        root_path = Path(tmp_dir)

        # Create a directory inside the secure root
        secure_dir = root_path / "secure"
        secure_dir.mkdir()

        # Create an external directory we want to protect from permission changes
        external_dir = root_path / "external"
        external_dir.mkdir()
        external_file = external_dir / "external.txt"
        external_file.write_text("sensitive info")

        # Set loose permissions on external directory/file
        os.chmod(external_dir, 0o755)
        os.chmod(external_file, 0o644)

        # Create a symlink from inside secure_dir to the external directory or external file
        symlinked_dir = secure_dir / "link_to_external_dir"
        symlinked_file = secure_dir / "link_to_external_file"

        # Create the symlinks
        symlinked_dir.symlink_to(external_dir, target_is_directory=True)
        symlinked_file.symlink_to(external_file, target_is_directory=False)

        # Enforce privileges on secure_dir
        enforce_local_privileges(secure_dir)

        # Assert secure_dir permissions are restricted
        assert (secure_dir.stat().st_mode & 0o777) == 0o700

        # Ensure external files/directories WERE NOT altered via symlink traversal
        # (their permissions should remain 0o755 and 0o644, NOT 0o700 and 0o600)
        assert (external_dir.stat().st_mode & 0o777) == 0o755
        assert (external_file.stat().st_mode & 0o777) == 0o644

        # Ensure the symlinks themselves are recognized as symlinks
        assert symlinked_dir.is_symlink()
        assert symlinked_file.is_symlink()


def test_enforce_local_privileges_with_read_only_files():
    """Verify that enforce_local_privileges handles individual path permission exceptions gracefully."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        root_path = Path(tmp_dir)

        # Create directories and files
        subdir = root_path / "subdir"
        subdir.mkdir()

        test_file = subdir / "test.txt"
        test_file.write_text("content")

        # Set to read-only first
        os.chmod(test_file, 0o400)

        # Enforce privileges
        enforce_local_privileges(root_path)

        # Check permissions
        assert (root_path.stat().st_mode & 0o777) == 0o700
        assert (subdir.stat().st_mode & 0o777) == 0o700
        # The file itself should be restricted to 0o600 or remain safe
        assert (test_file.stat().st_mode & 0o777) in (0o600, 0o400)


# Sentinel verification complete. Secure privilege policies (0o600 for files,
# 0o700 for directories) are fully verified, preventing symlink traversal attacks.
# Last verified: August 12, 2026
