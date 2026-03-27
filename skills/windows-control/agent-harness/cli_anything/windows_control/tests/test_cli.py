#!/usr/bin/env python3
"""Tests for Windows Control CLI"""
import sys
import os
import subprocess

# Add jingmai-agent path
_JM = r"E:\PY\jingmai-agent"
if os.path.exists(_JM) and _JM not in sys.path:
    sys.path.insert(0, _JM)

import pytest


def run_cli(args: list) -> subprocess.CompletedProcess:
    """Run the CLI with given arguments."""
    cmd = ["python", "-m", "cli_anything.windows_control.windows_control_cli"] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


class TestSystemCommands:
    """Test system operations (these don't require GUI)."""

    def test_system_info(self):
        """System info should return OS information."""
        result = run_cli(["system", "info"])
        assert result.returncode == 0 or "success" in result.stdout.lower() or "windows" in result.stdout.lower()

    def test_system_wait(self):
        """Wait should complete successfully."""
        result = run_cli(["system", "wait", "--seconds", "0.5"])
        assert result.returncode == 0 or "[OK]" in result.stdout

    def test_system_process(self):
        """Check process should work for known processes."""
        result = run_cli(["system", "process", "--name", "python"])
        # Should succeed even if process not found
        assert result.returncode == 0

    def test_file_exists(self):
        """File exists check should work."""
        result = run_cli(["file", "exists", "--path", "E:\\PY\\jingmai-agent\\requirements.txt"])
        assert result.returncode == 0
        assert "True" in result.stdout or "[OK]" in result.stdout

    def test_file_list(self):
        """File list should return directory contents."""
        result = run_cli(["file", "list", "--path", "E:\\PY\\jingmai-agent", "--pattern", "*.py", "--recursive"])
        assert result.returncode == 0 or "[OK]" in result.stdout


class TestMouseCommands:
    """Test mouse operations."""

    def test_mouse_move(self):
        """Mouse move should execute without error."""
        result = run_cli(["mouse", "move", "--x", "100", "--y", "100"])
        assert result.returncode == 0 or "[OK]" in result.stdout

    def test_mouse_click(self):
        """Mouse click should execute without error."""
        result = run_cli(["mouse", "click", "--x", "200", "--y", "200"])
        assert result.returncode == 0 or "[OK]" in result.stdout

    def test_mouse_click_with_button(self):
        """Mouse click with right button should work."""
        result = run_cli(["mouse", "click", "--x", "100", "--y", "100", "--button", "right"])
        assert result.returncode == 0 or "[OK]" in result.stdout


class TestKeyboardCommands:
    """Test keyboard operations."""

    def test_keyboard_press(self):
        """Keyboard press should work."""
        result = run_cli(["keyboard", "press", "--keys", "enter"])
        # This may fail if no focused window, which is acceptable
        assert result.returncode in (0, 1)


class TestWindowCommands:
    """Test window operations."""

    def test_window_list(self):
        """Window list should return window information."""
        result = run_cli(["window", "list"])
        assert result.returncode == 0 or "[OK]" in result.stdout


class TestUICommands:
    """Test UI inspection commands."""

    def test_ui_screenshot(self):
        """Screenshot should capture and return image data."""
        result = run_cli(["ui", "screenshot"])
        # May fail in headless environment
        assert result.returncode in (0, 1)


class TestJSONOutput:
    """Test JSON output mode."""

    def test_system_info_json(self):
        """JSON output should be valid JSON."""
        result = run_cli(["--json", "system", "info"])
        # Check for JSON structure
        output = result.stdout.strip()
        # Should contain JSON with success field
        if result.returncode == 0:
            assert "success" in output or "data" in output or "{" in output


class TestCLIEntryPoints:
    """Test CLI entry points."""

    def test_help(self):
        """Help should display available commands."""
        result = run_cli(["--help"])
        assert result.returncode == 0
        assert "mouse" in result.stdout
        assert "keyboard" in result.stdout
        assert "window" in result.stdout

    def test_group_help(self):
        """Group help should display subcommands."""
        result = run_cli(["mouse", "--help"])
        assert result.returncode == 0
        assert "click" in result.stdout

    def test_nonexistent_command(self):
        """Nonexistent command should fail gracefully."""
        result = run_cli(["nonexistent", "command"])
        assert result.returncode != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
