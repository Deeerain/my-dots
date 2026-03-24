"""Unit tests for Utils class"""
import pytest
from unittest.mock import patch, MagicMock
import subprocess
import sys
import pathlib
import importlib.util

# Load ubm-dots.py as module for testing
module_path = pathlib.Path(__file__).parent.parent / 'ubm-dots.py'
spec = importlib.util.spec_from_file_location('ubm_dots', module_path)
ubm_dots = importlib.util.module_from_spec(spec)
sys.modules['ubm_dots'] = ubm_dots
spec.loader.exec_module(ubm_dots)

from ubm_dots import Utils


class TestIsNewestVersion:
    """Tests for version comparison logic"""

    def test_major_version_newer(self):
        """Test that newer major version is recognized"""
        assert Utils.is_newest_version("2.0.0", "1.9.9") is True

    def test_major_version_older(self):
        """Test that older major version is recognized"""
        assert Utils.is_newest_version("1.9.9", "2.0.0") is False

    def test_minor_version_newer(self):
        """Test that newer minor version is recognized"""
        assert Utils.is_newest_version("1.2.0", "1.1.9") is True

    def test_minor_version_older(self):
        """Test that older minor version is recognized"""
        assert Utils.is_newest_version("1.1.9", "1.2.0") is False

    def test_patch_version_newer(self):
        """Test that newer patch version is recognized"""
        assert Utils.is_newest_version("1.0.2", "1.0.1") is True

    def test_patch_version_older(self):
        """Test that older patch version is recognized"""
        assert Utils.is_newest_version("1.0.1", "1.0.2") is False

    def test_equal_versions(self):
        """Test that equal versions return False"""
        assert Utils.is_newest_version("1.0.0", "1.0.0") is False

    def test_versions_with_dash(self):
        """Test versions with dash separator"""
        assert Utils.is_newest_version("1-0-5", "1-0-4") is True

    def test_mixed_separators(self):
        """Test versions with mixed separators"""
        assert Utils.is_newest_version("1.0-5", "1.0-4") is True

    def test_short_version_strings(self):
        """Test versions shorter than 3 parts"""
        assert Utils.is_newest_version("1.2", "1.1") is True
        assert Utils.is_newest_version("2", "1") is True

    def test_version_with_leading_zero(self):
        """Test versions with leading zeros"""
        assert Utils.is_newest_version("01.02.03", "01.02.02") is True


class TestGetCurrentVersion:
    """Tests for getting installed version"""

    @patch('subprocess.run')
    def test_get_version_success(self, mock_run):
        """Test successful version retrieval"""
        mock_result = MagicMock()
        mock_result.stdout = b"ubm-dots 0.0.5\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        version = Utils.get_current_version("ubm-dots")
        assert version == "0.0.5"

    @patch('subprocess.run')
    def test_get_version_with_v_prefix(self, mock_run):
        """Test version retrieval with 'v' prefix"""
        mock_result = MagicMock()
        mock_result.stdout = b"ubm-dots v1.2.3\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        version = Utils.get_current_version("ubm-dots")
        assert version == "1.2.3"

    @patch('subprocess.run')
    def test_get_version_command_failed(self, mock_run):
        """Test version retrieval when pacman fails"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pacman')

        version = Utils.get_current_version("ubm-dots")
        assert version is None

    @patch('subprocess.run')
    def test_get_version_parse_error(self, mock_run):
        """Test version retrieval with malformed output"""
        mock_result = MagicMock()
        mock_result.stdout = b"malformed"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        version = Utils.get_current_version("ubm-dots")
        assert version is None


class TestSetupZst:
    """Tests for ZST package installation"""

    @patch('subprocess.run')
    def test_setup_zst_success(self, mock_run):
        """Test successful ZST installation"""
        mock_run.return_value = MagicMock(returncode=0)
        
        filepath = pathlib.Path("/tmp/ubm-dots.zst")
        # Should not raise
        try:
            Utils.setup_zst(filepath)
        except subprocess.CalledProcessError:
            pytest.fail("setup_zst raised CalledProcessError unexpectedly")

    @patch('subprocess.run')
    def test_setup_zst_failure(self, mock_run):
        """Test ZST installation failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pacman')
        
        filepath = pathlib.Path("/tmp/ubm-dots.zst")
        with pytest.raises(subprocess.CalledProcessError):
            Utils.setup_zst(filepath)

    @patch('subprocess.run')
    def test_setup_zst_path_conversion(self, mock_run):
        """Test that path is properly converted to string"""
        mock_run.return_value = MagicMock(returncode=0)
        
        filepath = pathlib.Path("/tmp/ubm-dots.zst")
        Utils.setup_zst(filepath)
        
        # Verify the path was passed as string
        args = mock_run.call_args[0][0]
        assert str(filepath) in args
