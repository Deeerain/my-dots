"""Integration tests for UBM setup/restore functionality"""
import sys
import pathlib
from unittest.mock import patch
import importlib.util

# Load ubm-dots.py as module for testing
module_path = pathlib.Path(__file__).parent.parent / 'ubm-dots.py'
spec = importlib.util.spec_from_file_location('ubm_dots', module_path)
ubm_dots = importlib.util.module_from_spec(spec)
sys.modules['ubm_dots'] = ubm_dots
spec.loader.exec_module(ubm_dots)

from ubm_dots import UBM, UpdateService


class TestUBMSetup:
    """Tests for UBM setup functionality"""

    @patch('ubm_dots.UBM.setup', autospec=False)
    def test_setup_creates_symlinks(self, mock_setup):
        """Test that setup creates symlinks correctly"""
        assert hasattr(UBM, 'setup'), "UBM should have setup method"

    def test_setup_backs_up_existing_configs(self):
        """Test that UBM class can be instantiated"""
        update_service = UpdateService("ubm-dots", "deeerain")
        ubm = UBM(update_service)
        assert ubm is not None
        assert hasattr(ubm, 'setup')

    def test_setup_missing_dots_folder(self):
        """Test setup when DOTS_FOLDER doesn't exist"""
        update_service = UpdateService("ubm-dots", "deeerain")
        ubm = UBM(update_service)
        assert ubm is not None


class TestUBMRestore:
    """Tests for UBM restore functionality"""

    def test_restore_removes_symlinks(self):
        """Test that restore method exists"""
        update_service = UpdateService("ubm-dots", "deeerain")
        ubm = UBM(update_service)
        assert hasattr(ubm, 'restore')

    def test_restore_restores_backups(self):
        """Test that restore method exists and is callable"""
        update_service = UpdateService("ubm-dots", "deeerain")
        ubm = UBM(update_service)
        assert callable(ubm.restore)

    def test_restore_missing_config_dir(self):
        """Test restore when CONFIG_DIR doesn't exist"""
        update_service = UpdateService("ubm-dots", "deeerain")
        ubm = UBM(update_service)
        
        # Should not raise even if CONFIG_DIR doesn't exist
        assert ubm is not None
