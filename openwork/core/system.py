import os
import platform
import shutil
import socket
from typing import Dict, Optional


def read_os_release() -> Dict[str, str]:
	data = {}
	try:
		with open('/etc/os-release', 'r') as f:
			for line in f:
				if '=' in line:
					k, v = line.rstrip().split('=', 1)
					data[k] = v.strip('"')
	except Exception:
		pass
	return data


def get_distribution() -> Dict[str, Optional[str]]:
	info = read_os_release()
	name = info.get('NAME') or platform.system()
	version = info.get('VERSION_ID') or platform.release()
	id_like = info.get('ID_LIKE', '')
	distro_id = info.get('ID', '').lower()
	family = 'unknown'
	if 'debian' in id_like or distro_id in ('debian', 'ubuntu', 'zorin'):
		family = 'debian'
	elif 'fedora' in id_like or distro_id in ('fedora', 'rhel', 'centos'):
		family = 'rhel'

	return {
		'name': name,
		'id': distro_id,
		'version': version,
		'family': family,
	}


def is_desktop_environment() -> bool:
	return bool(os.environ.get('XDG_SESSION_TYPE') or os.environ.get('WAYLAND_DISPLAY') or os.environ.get('DISPLAY'))


def detect_desktop_environment() -> str:
	desktop = os.environ.get('XDG_CURRENT_DESKTOP') or os.environ.get('DESKTOP_SESSION') or ''
	desktop = desktop.lower()
	if 'gnome' in desktop:
		return 'GNOME'
	if 'kde' in desktop or 'plasma' in desktop:
		return 'KDE'
	if desktop:
		return desktop.upper()
	return 'unknown'


def has_command(cmd: str) -> bool:
	return shutil.which(cmd) is not None


def internet_ok(host: str = '8.8.8.8', port: int = 53, timeout: float = 2.0) -> bool:
	try:
		sock = socket.create_connection((host, port), timeout)
		sock.close()
		return True
	except Exception:
		return False

