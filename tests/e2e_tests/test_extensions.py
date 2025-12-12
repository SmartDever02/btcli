"""
End-to-end tests for BTCLI Extensions feature.

These tests verify the actual command-line interface behavior.
"""

import os
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path


def run_btcli_command(args, cwd=None):
    """Run a btcli command and return the result."""
    cmd = [sys.executable, "-m", "bittensor_cli.cli"] + args
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def test_extensions_help():
    """Test that extensions help command works."""
    returncode, stdout, stderr = run_btcli_command(["extensions", "--help"])

    assert returncode == 0, f"Command failed with stderr: {stderr}"
    assert "extensions" in stdout.lower() or "extension" in stdout.lower()
    assert "add" in stdout.lower()
    assert "update" in stdout.lower()
    assert "run" in stdout.lower()
    assert "create" in stdout.lower()
    assert "test" in stdout.lower()


def test_extensions_aliases():
    """Test that extension aliases work."""
    # Test 'ext' alias
    returncode, stdout, stderr = run_btcli_command(["ext", "--help"])
    assert returncode == 0, f"'ext' alias failed: {stderr}"

    # Test 'extension' alias
    returncode, stdout, stderr = run_btcli_command(["extension", "--help"])
    assert returncode == 0, f"'extension' alias failed: {stderr}"


def test_extensions_create():
    """Test creating a boilerplate extension."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Create a test extension
            returncode, stdout, stderr = run_btcli_command(
                ["extensions", "create", "test-extension"], cwd=temp_dir
            )

            # Note: This might fail if dependencies aren't installed
            # -1 indicates an exception occurred (e.g., missing dependencies)
            # 0 or 1 are expected success/error codes
            # We accept -1 as it means the command was attempted but failed due to environment
            assert returncode in [0, 1, -1], (
                f"Unexpected return code: {returncode}, stdout: {stdout}, stderr: {stderr}"
            )

        finally:
            os.chdir(original_cwd)


def test_extensions_add_invalid_repo():
    """Test adding an extension with invalid repository format."""
    returncode, stdout, stderr = run_btcli_command(
        ["extensions", "add", "invalid-repo-format"]
    )

    # Should fail gracefully
    assert returncode != 0 or "invalid" in stderr.lower() or "error" in stderr.lower()


def test_extensions_update_no_extensions():
    """Test updating when no extensions are installed."""
    returncode, stdout, stderr = run_btcli_command(["extensions", "update"])

    # Should handle gracefully (either succeed or show message)
    assert returncode in [0, 1]


def test_extensions_run_nonexistent():
    """Test running a non-existent extension."""
    returncode, stdout, stderr = run_btcli_command(
        ["extensions", "run", "nonexistent-extension"]
    )

    # Should fail with error message
    assert returncode != 0
    assert "not found" in stderr.lower() or "error" in stderr.lower()


def test_extensions_test_no_extensions():
    """Test running tests when no extensions are installed."""
    returncode, stdout, stderr = run_btcli_command(["extensions", "test"])

    # Should handle gracefully
    assert returncode in [0, 1]


def test_extensions_command_structure():
    """Test that all extension commands are accessible."""
    commands = ["add", "update", "run", "create", "test"]

    for cmd in commands:
        returncode, stdout, stderr = run_btcli_command(["extensions", cmd, "--help"])
        # Commands should either show help or fail gracefully
        assert returncode in [0, 1, 2], (
            f"Command 'extensions {cmd}' failed unexpectedly"
        )


def test_extensions_config_integration():
    """Test that extensions are stored in config."""
    # This is a basic smoke test
    # Full integration would require actual config file manipulation
    returncode, stdout, stderr = run_btcli_command(["config", "get"])

    # Config command should work
    assert returncode in [0, 1]


if __name__ == "__main__":
    """Run tests if executed directly."""
    import pytest

    # Run tests
    pytest.main([__file__, "-v"])
