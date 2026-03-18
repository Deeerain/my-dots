#!/bin/python3
import typer
import urllib.request
import json
import subprocess
from http.client import HTTPResponse
import pathlib
from typing import List, Dict, Any

REPO_OWNER = "deeerain"
REPO_NAME = "ubm-dots"
INSTALL_FOLDER = pathlib.Path("/usr/share/ubm-dots")
DOTS_FOLDER = INSTALL_FOLDER / 'dots'
HOME_DIR = pathlib.Path.home()
CONFIG_DIR = HOME_DIR / '.config'

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
        url = f'{self.api_url}/releases/latest'
        data = self._request(url)

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

        print(result)

        if len(result) > 0:
            return result[0]
        return None

    def _get_asset_download_info(self, asset: Dict) -> (str, str):
        return (asset.get('name'), asset.get('browser_download_url'))

    def _request(self, url: str, *, method: str = 'get') -> Any:
        resp: HTTPResponse = urllib.request.urlopen(url)
        try:
            return json.loads(resp.read().decode('utf-8'))
        finally:
            resp.close()


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
        self.modules = DOTS_FOLDER.iterdir()

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
        update_service.get_latest_repo_info()
        zst_asset = update_service.find_zst_file()

        if not zst_asset:
            print("Zst file not found")
            return

        zst_file = update_service.download_asset(zst_asset)
        Utils.setup_zst(zst_file)

    def check_updates(self) -> bool:
        return self.update_service.check_updates()

    def setup(self):
        for module in DOTS_FOLDER.iterdir():
            module_name = module.name
            home_module = CONFIG_DIR / module_name

            if home_module.exists():
                home_module.move(f'{home_module}.back')

            home_module.symlink_to(module)

        self.restart_services()

    def restore(self) -> None:
        for module in CONFIG_DIR.iterdir():
            if not module.is_symlink():
                continue
            if not module.readlink() in self.modules:
                continue
            module.unlink()

        for module in CONFIG_DIR.iterdir():
            if not module.name.endswith('.back'):
                continue

            module.move(CONFIG_DIR / module.name.removesuffix('.back'))

        self.restart_services()


update_service = UpdateService(REPO_NAME, REPO_OWNER)
ubm = UBM(update_service)
ubm.add_service('hyprland', HyprlandService())
ubm.add_service('waybar', WaybarService())


# COMMANDS


@app.command("update")
def update(debug: bool = typer.Option(False, '--debug')):
    if debug:
        ubm.update()
        return

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


@app.command("install")
def install_command(debug: bool = typer.Option(False, "--debug")):
    ubm.setup()


@app.command('restore')
def restore_command():
    ubm.restore()


if __name__ == "__main__":
    app()
