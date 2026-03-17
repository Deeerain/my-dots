#!/bin/python3
import shutil
import typer
import urllib.request
import json
import subprocess
import os
import pathlib
from typing import List, Optional, Dict, Any
from enum import Enum

REPO_OWNER = "deeerain"
REPO_NAME = "ubm-dots"
INSTALL_FOLDER = pathlib.Path("/usr/share/ubm-dots")
DOTFILES_DIR_NAME = "dots"

app = typer.Typer()


class ServiceBase:
    def stop(self):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def restart(self):
        self.stop()
        self.start()

    def _cmd(self, cmd):
        try:
            subprocess.run(cmd)
        except subprocess.CalledProcessError as e:
            pass


class Utils:
    @staticmethod
    def get_current_version(repo_name: str):
        '''Get installed verison'''
        result = subprocess.run(
            f"pacman -Q {REPO_NAME}".split(), capture_output=True)
        version = result.stdout.decode("utf-8").split()[1]

        if version.startswith("v"):
            version = version[1:]

        return version

    @staticmethod
    def is_newest_version(ver1: str, ver2: str) -> bool:
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
    def setup_zst(filepath: pathlib.Path):
        subprocess.run(f"sudo pacman -U {filepath}".split())


class UpdateService:
    def __init__(self, repo_name: str, repo_owner: str) -> None:
        self.repo = repo_name
        self.owner = repo_owner
        self.assets: List[Dict] = {}
        self.latest_version: str = None

    @property
    def api_url(self) -> str:
        return f'https://api.github.com/repos/{self.owner}/{self.repo}'

    def check_updates(self) -> True:
        pass

    def get_latest_repo_info(self) -> None:
        data = self._request(f'{self.api_url}/releases/latest')

        self.assets = data.get('assets')

        latest_version = data.get('tag_name')

        if latest_version.startswith("v"):
            latest_version = latest_version[1:]

            self.latest_version = latest_version

    def find_zst_file(self) -> Dict | None:
        for asset in self.assets:
            filename = asset.get("name")

            if not filename:
                continue

            if filename.endswith(".zst"):
                return asset

    def download_asset(self, asset: Dict, folder: str = '/tmp/') -> str | None:
        name, url = self._get_asset_download_info(asset)
        download_path = pathlib.Path(folder, name)
        return self._download(url, download_path)

    def _download(self, url: str, filename: str) -> str | None:
        result = urllib.request.urlretrieve(url, filename)

        if len(result) > 0:
            return result[1]
        return None

    def _get_asset_download_info(self, asset: Dict) -> (str, str):
        return (asset.get('name'), asset.get('browser_download_url'))

    def _request(self, url: str, *, method: str = 'get') -> Any:
        req = urllib.request.Request(url, method=method)

        with urllib.request.urlopen(req) as resp:
            return Dict(json.loads(resp.read().decode('utf-8')))


class HyprlandService(ServiceBase):
    def restart(self):
        self._cmd(['hyprctl', 'reload'])


class WaybarService(ServiceBase):
    def stop(self):
        self._cmd(['killall', 'waybar'])

    def start(self):
        self._cmd(['hyprctl', 'dispatch', 'exec', 'waybar'])


class UBMService(ServiceBase):
    def __init__(self, services: Dict[str, ServiceBase] = {}):
        self.services = services

    def add_service(self, name: str, service: ServiceBase):
        self.services.setdefault(name, service)

    def get_service(self, name: str) -> ServiceBase | None:
        return self.services.get(name)

    def restart(self):
        for service in self.services.values():
            service.restart()

    def start(self):
        for service in self.services.values():
            try:
                service.restart()
            except NotImplementedError:
                pass

    def stop(self):
        for service in self.services.values():
            try:
                service.stop()
            except NotImplementedError:
                pass


class UBM:
    def __init__(self, update_service: UpdateService):
        self.update_service = update_service
        self.services = UBMService()

    def add_service(self, name: str, service: ServiceBase):
        self.services.add_service(name, service)

    def restart_services(self, services: List[str] = []):
        if not any(services):
            self.services.restart()
            return

        for service_name in services:
            self.services.get_service(service_name).restart()

    def get_service_names(self) -> List[str]:
        return self.services.services.keys()

    def update(self):
        zst_file = update_service.download_asset()
        Utils.setup_zst(zst_file)

    def check_updates(self) -> bool:
        return self.update_service.check_updates()


update_service = UpdateService(REPO_NAME, REPO_OWNER)
ubm = UBM(update_service)
ubm.add_service('hyprland', HyprlandService())
ubm.add_service('waybar', WaybarService())


# COMMANDS


@app.command("update")
def update():
    if not ubm.check_updates():
        typer.echo('Latest version')
        return

    ubm.update()


@app.command("reload")
def reload(
    services: List[str] = typer.Option(
        [*ubm.get_service_names()], "--services", "-s"),
):
    ubm.restart_services(services)


def backup(*args: pathlib.Path):
    for dest in args:
        backup = dest.with_suffix(f"{dest.suffix}.backup")
        shutil.move(str(dest), str(backup))
        print(f"Backup : {backup}")


def install(install_dir: pathlib.Path, config_dir_name: str):
    if (
        not install_dir.exists()
        and not pathlib.Path(install_dir, config_dir_name).exists()
    ):
        return

    home_config_dir = pathlib.Path.home() / ".config"
    config_modules = [_ for _ in (install_dir / config_dir_name).iterdir()]

    for config_module in config_modules:
        home_config_module = home_config_dir / config_module.name

        if not config_module.is_dir():
            if home_config_module.exists() and not home_config_module.is_symlink():
                backup(home_config_module)
                home_config_module.symlink_to(config_module)

        if home_config_module.exists() and not home_config_module.is_symlink():
            backup(home_config_module)

        if home_config_module.is_symlink():
            home_config_module.unlink()

        try:
            home_config_module.symlink_to(config_module)
            print(f"Symlink: {home_config_module} -> {config_module}")
        except Exception as e:
            print(e)


@app.command("install")
def install_command(debug: bool = typer.Option(False, "--debug")):
    install_dir = INSTALL_FOLDER if not debug else pathlib.Path("./")
    install(install_dir, DOTFILES_DIR_NAME)


if __name__ == "__main__":
    app()
