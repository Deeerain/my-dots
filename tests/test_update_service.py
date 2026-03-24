"""Unit tests for UpdateService class"""
import pytest
from unittest.mock import patch, MagicMock
import json
import sys
import pathlib
import importlib.util

# Load ubm-dots.py as module for testing
module_path = pathlib.Path(__file__).parent.parent / 'ubm-dots.py'
spec = importlib.util.spec_from_file_location('ubm_dots', module_path)
ubm_dots = importlib.util.module_from_spec(spec)
sys.modules['ubm_dots'] = ubm_dots
spec.loader.exec_module(ubm_dots)

from ubm_dots import UpdateService, Utils


class TestUpdateService:
    """Tests for UpdateService"""

    def test_api_url_construction(self):
        """Test GitHub API URL construction"""
        service = UpdateService("ubm-dots", "deeerain")
        expected_url = "https://api.github.com/repos/deeerain/ubm-dots"
        assert service.api_url == expected_url

    @patch('urllib.request.urlopen')
    def test_get_latest_repo_info_success(self, mock_urlopen):
        """Test successful repo info retrieval"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "tag_name": "v0.0.5",
            "assets": [
                {"name": "ubm-dots-0.0.5-3-any.pkg.tar.zst", "browser_download_url": "http://example.com/file.zst"}
            ]
        }).encode('utf-8')
        mock_urlopen.return_value = mock_response

        service = UpdateService("ubm-dots", "deeerain")
        service.get_latest_repo_info()

        assert service.latest_version == "0.0.5"
        assert len(service.assets) == 1

    @patch('urllib.request.urlopen')
    def test_get_latest_repo_info_with_v_prefix(self, mock_urlopen):
        """Test version parsing with 'v' prefix"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "tag_name": "v1.2.3-rc1",
            "assets": []
        }).encode('utf-8')
        mock_urlopen.return_value = mock_response

        service = UpdateService("ubm-dots", "deeerain")
        service.get_latest_repo_info()

        assert service.latest_version == "1.2.3-rc1"

    def test_find_zst_file_found(self):
        """Test finding ZST file in assets"""
        service = UpdateService("ubm-dots", "deeerain")
        service.assets = [
            {"name": "ubm-dots-0.0.5-3-any.pkg.tar.zst", "browser_download_url": "http://example.com/file.zst"},
            {"name": "source.tar.gz", "browser_download_url": "http://example.com/source.tar.gz"}
        ]

        zst_file = service.find_zst_file()
        assert zst_file is not None
        assert zst_file["name"] == "ubm-dots-0.0.5-3-any.pkg.tar.zst"

    def test_find_zst_file_not_found(self):
        """Test when ZST file is not in assets"""
        service = UpdateService("ubm-dots", "deeerain")
        service.assets = [
            {"name": "source.tar.gz", "browser_download_url": "http://example.com/source.tar.gz"},
            {"name": "README.md", "browser_download_url": "http://example.com/README.md"}
        ]

        zst_file = service.find_zst_file()
        assert zst_file is None

    def test_find_zst_file_empty_assets(self):
        """Test when assets list is empty"""
        service = UpdateService("ubm-dots", "deeerain")
        service.assets = []

        zst_file = service.find_zst_file()
        assert zst_file is None

    def test_get_asset_download_info(self):
        """Test extracting download info from asset"""
        service = UpdateService("ubm-dots", "deeerain")
        asset = {
            "name": "ubm-dots-0.0.5-3-any.pkg.tar.zst",
            "browser_download_url": "https://github.com/deeerain/ubm-dots/releases/download/v0.0.5-3/ubm-dots-0.0.5-3-any.pkg.tar.zst"
        }

        name, url = service._get_asset_download_info(asset)
        assert name == "ubm-dots-0.0.5-3-any.pkg.tar.zst"
        assert url == "https://github.com/deeerain/ubm-dots/releases/download/v0.0.5-3/ubm-dots-0.0.5-3-any.pkg.tar.zst"

    @patch.object(UpdateService, 'get_latest_repo_info')
    @patch('ubm_dots.Utils.get_current_version')
    def test_check_updates_up_to_date(self, mock_get_version, mock_get_info):
        """Test checking for updates when already up to date"""
        mock_get_version.return_value = "0.0.5"
        
        service = UpdateService("ubm-dots", "deeerain")
        service.latest_version = "0.0.5"

        result = service.check_updates()
        # 0.0.5 == 0.0.5, no update needed
        assert result is False

    @patch.object(UpdateService, 'get_latest_repo_info')
    @patch('ubm_dots.Utils.get_current_version')
    def test_check_updates_get_version_failed(self, mock_get_version, mock_get_info):
        """Test checking for updates when getting version fails"""
        mock_get_version.return_value = None
        
        service = UpdateService("ubm-dots", "deeerain")
        service.latest_version = "0.0.5"

        result = service.check_updates()
        assert result is False

    @patch.object(UpdateService, 'get_latest_repo_info')
    @patch('ubm_dots.Utils.get_current_version')
    def test_check_updates_exception_handling(self, mock_get_version, mock_get_info):
        """Test exception handling in check_updates"""
        mock_get_info.side_effect = Exception("Network error")
        
        service = UpdateService("ubm-dots", "deeerain")
        
        result = service.check_updates()
        assert result is False
