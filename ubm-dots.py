#!/bin/python3
"""
UBM (User Base Manager) - A tool for managing dotfiles and system services.
"""

import typer
import urllib.request
import json
import subprocess
import shutil
import sys
import os
import logging
import tomllib
from http.client import HTTPResponse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Iterator
from dataclasses import dataclass
import unittest
from unittest.mock import Mock, patch

# Constants
REPO_OWNER = "deeerain"
REPO_NAME = "ubm-dots"
VERSION = "0.0.8"  # Update this when releasing new versions (sync with PKGBUILD)
INSTALL_FOLDER = Path("/usr/share/ubm-dots")
DOTS_FOLDER = INSTALL_FOLDER / 'dots'
HOME_DIR = Path.home()
CONFIG_DIR = HOME_DIR / '.config'
CONFIG_FILE = HOME_DIR / '.config/ubm/config.toml'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = typer.Typer()


@dataclass
class RepoConfig:
    """Repository configuration."""
    owner: str = REPO_OWNER
    name: str = REPO_NAME


class Config:
    """Configuration manager for UBM."""
    
    def __init__(self, config_path: Path = CONFIG_FILE):
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'rb') as f:
                    return tomllib.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
                return self._default_config()
        return self._default_config()
    
    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            'services': ['hyprland', 'waybar'],
            'repo': {'owner': REPO_OWNER, 'name': REPO_NAME},
            'update': {'check_on_startup': True, 'auto_update': False},
            'backup': {'enabled': True, 'max_backups': 5}
        }
    
    @property
    def services(self) -> List[str]:
        """Get list of managed services."""
        return self._config.get('services', ['hyprland', 'waybar'])
    
    @property
    def repo(self) -> RepoConfig:
        """Get repository configuration."""
        repo = self._config.get('repo', {})
        return RepoConfig(
            owner=repo.get('owner', REPO_OWNER),
            name=repo.get('name', REPO_NAME)
        )
    
    @property
    def update_check_on_startup(self) -> bool:
        """Check for updates on startup."""
        return self._config.get('update', {}).get('check_on_startup', True)
    
    @property
    def auto_update(self) -> bool:
        """Automatically update when available."""
        return self._config.get('update', {}).get('auto_update', False)
    
    @property
    def backup_enabled(self) -> bool:
        """Enable backup functionality."""
        return self._config.get('backup', {}).get('enabled', True)
    
    @property
    def max_backups(self) -> int:
        """Maximum number of backups to keep."""
        return self._config.get('backup', {}).get('max_backups', 5)


class ServiceBase:
    """Base class for system services."""
    
    def stop(self):
        """Stop the service."""
        raise NotImplementedError()
    
    def start(self):
        """Start the service."""
        raise NotImplementedError()
    
    def restart(self):
        """Restart the service."""
        self.stop()
        self.start()
    
    def _cmd(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Execute a system command."""
        try:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)
            logger.debug(f"Command succeeded: {' '.join(cmd)}")
            return result
        except subprocess.CalledProcessError as e:
            logger.warning(f"Command failed: {' '.join(cmd)} - {e.stderr}")
            if check:
                raise
            return e
        except FileNotFoundError as e:
            logger.error(f"Command not found: {' '.join(cmd)}")
            raise


class HyprlandService(ServiceBase):
    """Service manager for Hyprland."""
    
    def restart(self):
        """Reload Hyprland configuration."""
        self._cmd(['hyprctl', 'reload'])


class WaybarService(ServiceBase):
    """Service manager for Waybar."""
    
    def stop(self):
        """Stop Waybar."""
        self._cmd(['killall', 'waybar'], check=False)
    
    def start(self):
        """Start Waybar."""
        self._cmd(['hyprctl', 'dispatch', 'exec', 'waybar'])


class UBMService:
    """Container for multiple services."""
    
    def __init__(self, services: Optional[Dict[str, ServiceBase]] = None):
        self.services = services or {}
    
    def add_service(self, name: str, service: ServiceBase):
        """Add a service to the container."""
        self.services.setdefault(name, service)
    
    def get_service(self, name: str) -> Optional[ServiceBase]:
        """Get a service by name."""
        return self.services.get(name)
    
    def get_service_names(self) -> List[str]:
        """Get list of all service names."""
        return list(self.services.keys())
    
    def restart(self):
        """Restart all services."""
        for service in self.services.values():
            try:
                service.restart()
                logger.info(f"Restarted service: {service.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to restart {service.__class__.__name__}: {e}")
    
    def start(self):
        """Start all services."""
        for service in self.services.values():
            try:
                service.start()
                logger.info(f"Started service: {service.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to start {service.__class__.__name__}: {e}")
    
    def stop(self):
        """Stop all services."""
        for service in self.services.values():
            try:
                service.stop()
                logger.info(f"Stopped service: {service.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to stop {service.__class__.__name__}: {e}")


class Utils:
    """Utility functions."""
    
    @staticmethod
    def get_current_version(repo_name: str) -> str:
        """Get current version from VERSION constant."""
        version = VERSION
        if version.startswith("v"):
            version = version[1:]
        return version
    
    @staticmethod
    def is_newest_version(ver1: str, ver2: str) -> bool:
        """Compare two version strings."""
        ver1_parts = list(map(int, ver1.replace("-", ".").split(".")))
        ver2_parts = list(map(int, ver2.replace("-", ".").split(".")))
        
        while len(ver1_parts) < 3:
            ver1_parts.append(0)
        while len(ver2_parts) < 3:
            ver2_parts.append(0)
        
        for i in range(3):
            if ver1_parts[i] > ver2_parts[i]:
                return True
            elif ver1_parts[i] < ver2_parts[i]:
                return False
        
        return False
    
    @staticmethod
    def setup_zst(filepath: Path, dry_run: bool = False) -> None:
        """Install a .zst package file."""
        if os.geteuid() != 0:
            raise PermissionError("This operation requires root privileges")
        
        if dry_run:
            typer.echo(f"Would install: {filepath}")
            return
        
        try:
            subprocess.run(["pacman", "-U", str(filepath)], check=True)
            logger.info(f"Successfully installed: {filepath}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install package: {e}")
            raise
    
    @staticmethod
    def cleanup_old_backups(backup_dir: Path, max_backups: int) -> None:
        """Clean up old backup files."""
        backups = sorted(backup_dir.glob("*.back"), key=lambda p: p.stat().st_mtime)
        while len(backups) > max_backups:
            oldest = backups.pop(0)
            oldest.unlink()
            logger.info(f"Removed old backup: {oldest}")


class UpdateService:
    """Service for checking and applying updates."""
    
    def __init__(self, repo_owner: str, repo_name: str) -> None:
        self.repo = repo_name
        self.owner = repo_owner
        self.assets: List[Dict] = []
        self.latest_version: Optional[str] = None
    
    @property
    def api_url(self) -> str:
        """Get GitHub API URL for the repository."""
        return f'https://api.github.com/repos/{self.owner}/{self.repo}'
    
    def check_updates(self) -> bool:
        """Check if updates are available."""
        try:
            self.get_latest_repo_info()
            current_version = Utils.get_current_version(self.repo)
            
            if current_version is None or self.latest_version is None:
                return False
            
            logger.debug(f"Current version: {current_version}")
            logger.debug(f"Latest version: {self.latest_version}")
            
            has_update = Utils.is_newest_version(self.latest_version, current_version)
            logger.info(f"Update available: {has_update}")
            return has_update
        except Exception as e:
            logger.error(f"Error checking updates: {e}", exc_info=True)
            return False
    
    def get_latest_repo_info(self) -> None:
        """Fetch latest release information from GitHub."""
        url = f'{self.api_url}/releases/latest'
        data = self._request(url)
        
        self.assets = data.get('assets', [])
        latest_version = data.get('tag_name', '')
        
        if latest_version.startswith("v"):
            latest_version = latest_version[1:]
        
        self.latest_version = latest_version
    
    def find_zst_file(self) -> Optional[Dict]:
        """Find the .zst asset in the release."""
        for asset in self.assets:
            filename = asset.get("name", "")
            if filename.endswith(".zst"):
                return asset
        return None
    
    def download_asset(self, asset: Dict, folder: str = '/tmp/') -> Optional[str]:
        """Download an asset with progress bar."""
        name, url = self._get_asset_download_info(asset)
        download_path = Path(folder, name)
        return self._download(url, download_path)
    
    def _download(self, url: str, filename: Path) -> Optional[str]:
        """Download a file with progress bar."""
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                with open(filename, 'wb') as f:
                    with typer.progressbar(
                        length=total_size,
                        label=f"Downloading {filename.name}"
                    ) as progress:
                        while True:
                            chunk = response.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress.update(len(chunk))
                
                logger.info(f"Downloaded: {filename}")
                return str(filename)
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None
    
    def _get_asset_download_info(self, asset: Dict) -> Tuple[str, str]:
        """Extract download information from asset."""
        return (asset.get('name', ''), asset.get('browser_download_url', ''))
    
    def _request(self, url: str) -> Any:
        """Make an HTTP request and parse JSON response."""
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise


class UBM:
    """Main UBM class for managing dotfiles and services."""
    
    def __init__(self, update_service: UpdateService, config: Config):
        self.update_service = update_service
        self.config = config
        self.services = UBMService()
        self.modules: Iterator[Path] = DOTS_FOLDER.iterdir() if DOTS_FOLDER.exists() else iter([])
        self._setup_services()
    
    def _setup_services(self):
        """Initialize services based on configuration."""
        for service_name in self.config.services:
            if service_name == 'hyprland':
                self.services.add_service('hyprland', HyprlandService())
            elif service_name == 'waybar':
                self.services.add_service('waybar', WaybarService())
    
    def add_service(self, name: str, service: ServiceBase):
        """Add a custom service."""
        self.services.add_service(name, service)
    
    def restart_services(self, services: Optional[List[str]] = None):
        """Restart specified services or all if none specified."""
        if not services:
            self.services.restart()
            return
        
        for service_name in services:
            service = self.services.get_service(service_name)
            if service:
                service.restart()
                logger.info(f"Restarted service: {service_name}")
            else:
                logger.warning(f"Service not found: {service_name}")
    
    def get_service_names(self) -> List[str]:
        """Get list of all service names."""
        return self.services.get_service_names()
    
    def update(self, dry_run: bool = False):
        """Update UBM to the latest version."""
        try:
            self.update_service.get_latest_repo_info()
            zst_asset = self.update_service.find_zst_file()
            
            if not zst_asset:
                typer.echo("Error: No .zst file found in release", err=True)
                return
            
            zst_file = self.update_service.download_asset(zst_asset)
            if not zst_file:
                typer.echo("Error: Failed to download update", err=True)
                return
            
            Utils.setup_zst(Path(zst_file), dry_run=dry_run)
            typer.echo(f"Successfully updated to version {self.update_service.latest_version}")
        except PermissionError as e:
            typer.echo(f"Error: {e}", err=True)
        except Exception as e:
            logger.error(f"Update failed: {e}", exc_info=True)
            typer.echo(f"Error: Update failed - {e}", err=True)
    
    def check_updates(self) -> bool:
        """Check if updates are available."""
        return self.update_service.check_updates()
    
    def setup(self, force: bool = False):
        """Setup dotfiles by symlinking to configuration directory."""
        if not DOTS_FOLDER.exists():
            typer.echo(f"Error: DOTS_FOLDER not found at {DOTS_FOLDER}", err=True)
            return
        
        for module in DOTS_FOLDER.iterdir():
            if not module.is_dir():
                continue
                
            module_name = module.name
            home_module = CONFIG_DIR / module_name
            
            if home_module.exists():
                if home_module.is_symlink() and not force:
                    typer.echo(f"Skipping {module_name} - already linked")
                    continue
                
                if not force:
                    if not typer.confirm(f"{home_module} exists. Backup and replace?"):
                        continue
                
                backup_path = Path(f'{home_module}.back')
                
                # Clean up old backup if exists
                if backup_path.exists():
                    if self.config.backup_enabled:
                        backup_path.unlink()
                    else:
                        shutil.rmtree(backup_path, ignore_errors=True)
                
                # Move existing to backup
                shutil.move(str(home_module), str(backup_path))
                logger.info(f"Backed up {home_module} to {backup_path}")
            
            # Create symlink
            home_module.symlink_to(module)
            logger.info(f"Created symlink: {home_module} -> {module}")
        
        # Clean up old backups
        if self.config.backup_enabled:
            Utils.cleanup_old_backups(CONFIG_DIR, self.config.max_backups)
        
        self.restart_services()
        typer.echo("Setup completed successfully")
    
    def restore(self) -> None:
        """Restore original configuration from backups."""
        if not CONFIG_DIR.exists():
            typer.echo(f"Error: CONFIG_DIR not found at {CONFIG_DIR}", err=True)
            return
        
        # Get set of modules we manage
        modules_set = {str(p) for p in DOTS_FOLDER.iterdir() if p.is_dir()}
        
        # Remove symlinks we created
        removed_count = 0
        for module in CONFIG_DIR.iterdir():
            if not module.is_symlink():
                continue
            
            try:
                target = module.readlink()
                if str(target) in modules_set:
                    module.unlink()
                    removed_count += 1
                    logger.info(f"Removed symlink: {module}")
            except (ValueError, OSError, RuntimeError) as e:
                logger.warning(f"Failed to process {module}: {e}")
                continue
        
        # Restore from backups
        restored_count = 0
        for module in CONFIG_DIR.glob("*.back"):
            original_name = module.name.removesuffix('.back')
            original_path = CONFIG_DIR / original_name
            
            if original_path.exists():
                typer.echo(f"Warning: {original_path} already exists, skipping restore")
                continue
                
            shutil.move(str(module), str(original_path))
            restored_count += 1
            logger.info(f"Restored: {original_path}")
        
        self.restart_services()
        typer.echo(f"Restored {restored_count} configurations, removed {removed_count} symlinks")
    
    def status(self) -> None:
        """Show status of managed dotfiles."""
        typer.echo("UBM Status:")
        typer.echo(f"Version: {VERSION}")
        typer.echo(f"Install folder: {INSTALL_FOLDER}")
        typer.echo(f"Dots folder: {DOTS_FOLDER}")
        typer.echo(f"Config folder: {CONFIG_DIR}")
        typer.echo(f"Managed services: {', '.join(self.get_service_names())}")
        
        # Check symlinks
        typer.echo("\nDotfiles status:")
        for module in DOTS_FOLDER.iterdir():
            if not module.is_dir():
                continue
                
            module_name = module.name
            home_module = CONFIG_DIR / module_name
            
            if home_module.is_symlink():
                try:
                    target = home_module.readlink()
                    if str(target) == str(module):
                        typer.echo(f"  ✓ {module_name} -> linked correctly")
                    else:
                        typer.echo(f"  ⚠ {module_name} -> linked to {target} (expected {module})")
                except:
                    typer.echo(f"  ✗ {module_name} -> broken symlink")
            elif home_module.exists():
                typer.echo(f"  ✗ {module_name} -> exists but not symlink")
            else:
                typer.echo(f"  ✗ {module_name} -> not linked")


# Initialize components
config = Config()
update_service = UpdateService(config.repo.owner, config.repo.name)
ubm = UBM(update_service, config)


# COMMANDS


@app.command("update")
def update(
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be updated"),
    force: bool = typer.Option(False, "--force", help="Force update even if not needed")
):
    """
    Update UBM to the latest version.
    
    Checks GitHub for new releases and installs them if available.
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    if dry_run:
        typer.echo("Dry run mode - no changes will be made")
        if ubm.check_updates():
            typer.echo(f"Would update from {VERSION} to {update_service.latest_version}")
        else:
            typer.echo(f"Already at latest version {VERSION}")
        return
    
    if not force and not ubm.check_updates():
        typer.echo(f'Already at latest version {VERSION}')
        return
    
    typer.echo(f"Updating from {VERSION} to {update_service.latest_version}...")
    ubm.update(dry_run=dry_run)


@app.command("reload")
def reload(
    services: List[str] = typer.Option(
        None, "--services", "-s", help="Services to reload (default: all)"
    ),
    all_services: bool = typer.Option(False, "--all", "-a", help="Reload all services")
):
    """
    Reload system services.
    
    If no services specified, reloads all managed services.
    """
    if all_services or not services:
        ubm.restart_services()
        typer.echo("All services reloaded")
    else:
        ubm.restart_services(services)
        typer.echo(f"Services reloaded: {', '.join(services)}")


@app.command("install")
def install_command(
    force: bool = typer.Option(False, "--force", "-f", help="Force reinstall even if exists"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode")
):
    """
    Install dotfiles by creating symlinks.
    
    This will backup existing configurations and create symlinks to the managed dotfiles.
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    typer.echo("Installing dotfiles...")
    ubm.setup(force=force)


@app.command('restore')
def restore_command(
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode")
):
    """
    Restore original configuration from backups.
    
    This removes symlinks and restores backed up configurations.
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not typer.confirm("This will restore original configurations. Continue?"):
        typer.echo("Restore cancelled")
        return
    
    ubm.restore()


@app.command("status")
def status_command():
    """Show current status of UBM and managed dotfiles."""
    ubm.status()


@app.command("config")
def show_config():
    """Show current configuration."""
    typer.echo("Current UBM Configuration:")
    typer.echo(f"Config file: {CONFIG_FILE}")
    typer.echo(f"Managed services: {', '.join(config.services)}")
    typer.echo(f"Repository: {config.repo.owner}/{config.repo.name}")
    typer.echo(f"Check updates on startup: {config.update_check_on_startup}")
    typer.echo(f"Auto update: {config.auto_update}")
    typer.echo(f"Backup enabled: {config.backup_enabled}")
    typer.echo(f"Max backups: {config.max_backups}")


if __name__ == "__main__":
    # Check for updates on startup if configured
    if config.update_check_on_startup and not config.auto_update:
        if ubm.check_updates():
            typer.echo(f"Update available: {VERSION} -> {update_service.latest_version}")
            typer.echo("Run 'ubm update' to install")
    
    app()