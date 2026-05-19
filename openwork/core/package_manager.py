import subprocess
import shutil
from abc import ABC, abstractmethod
from typing import List


class BasePackageManager(ABC):
	name = "base"

	@abstractmethod
	def is_installed(self, package_name: str) -> bool:
		raise NotImplementedError()

	@abstractmethod
	def update(self) -> bool:
		raise NotImplementedError()

	@abstractmethod
	def install(self, packages: List[str], on_line: Optional[Callable[[str], None]] = None,
				ask_password: Optional[Callable[[str], str]] = None) -> bool:
		raise NotImplementedError()

	@abstractmethod
	def install_local_package(self, file_path: str) -> bool:
		raise NotImplementedError()

	@abstractmethod
	def add_repository(self, repo_config: dict) -> bool:
		raise NotImplementedError()

	def validate_command(self, command: str) -> bool:
		return shutil.which(command) is not None


class AptPackageManager(BasePackageManager):
	name = "apt"

	def is_installed(self, package_name: str) -> bool:
		try:
			subprocess.check_call(["dpkg-query", "-W", "-f=${Status}", package_name],
								  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			return True
		except subprocess.CalledProcessError:
			return False

	def update(self, on_line: Optional[Callable[[str], None]] = None,
			   ask_password: Optional[Callable[[str], str]] = None) -> bool:
		return subprocess.call(["sudo", "apt-get", "update"]) == 0

	def install(self, packages: List[str], on_line: Optional[Callable[[str], None]] = None,
				ask_password: Optional[Callable[[str], str]] = None) -> bool:
		cmd = "sudo apt-get install -y " + " ".join(packages)
		# try to use Executor interactive if available to capture prompts
		try:
			from .executor import Executor
			ex = Executor()
			rc = ex.run_interactive(cmd, on_line=on_line, on_request_password=ask_password)
			return rc == 0
		except Exception:
			return subprocess.call(["sudo", "apt-get", "install", "-y"] + packages) == 0

	def install_local_package(self, file_path: str) -> bool:
		return subprocess.call(["sudo", "dpkg", "-i", file_path]) == 0

	def add_repository(self, repo_config: dict) -> bool:
		# Minimal implementation: expects repo_config with 'ppa' or 'deb' keys
		if 'ppa' in repo_config:
			return subprocess.call(["sudo", "add-apt-repository", "-y", repo_config['ppa']]) == 0
		if 'deb' in repo_config:
			try:
				with open('/etc/apt/sources.list.d/openwork.list', 'a') as f:
					f.write(repo_config['deb'] + "\n")
				return True
			except Exception:
				return False
		return False


class DnfPackageManager(BasePackageManager):
	name = "dnf"

	def is_installed(self, package_name: str) -> bool:
		try:
			subprocess.check_call(["rpm", "-q", package_name],
								  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			return True
		except subprocess.CalledProcessError:
			return False

	def update(self) -> bool:
		return subprocess.call(["sudo", "dnf", "makecache"]) == 0

	def install(self, packages: List[str], on_line: Optional[Callable[[str], None]] = None,
				ask_password: Optional[Callable[[str], str]] = None) -> bool:
		cmd = "sudo dnf install -y " + " ".join(packages)
		try:
			from .executor import Executor
			ex = Executor()
			rc = ex.run_interactive(cmd, on_line=on_line, on_request_password=ask_password)
			return rc == 0
		except Exception:
			return subprocess.call(["sudo", "dnf", "install", "-y"] + packages) == 0

	def install_local_package(self, file_path: str) -> bool:
		return subprocess.call(["sudo", "rpm", "-Uvh", file_path]) == 0

	def add_repository(self, repo_config: dict) -> bool:
		# Minimal: expect 'rpm' url to install repo package
		if 'rpm' in repo_config:
			return subprocess.call(["sudo", "dnf", "install", "-y", repo_config['rpm']]) == 0
		return False

