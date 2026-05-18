import os
import yaml
from .system import get_distribution, is_desktop_environment, detect_desktop_environment, has_command, internet_ok


def run_checks() -> dict:
	distro = get_distribution()
	checks = {
		'distribution': distro,
		'is_desktop': is_desktop_environment(),
		'desktop_env': detect_desktop_environment(),
		'python3': has_command('python3') or has_command('python'),
		'python_version': None,
		'pip3': has_command('pip3') or has_command('pip'),
		'venv_module': True,
		'git': has_command('git'),
		'vscode': has_command('code') or has_command('code-oss'),
		'gtk_available': False,
		'pyside6': False,
		'appimage_tool': has_command('appimagetool'),
		'dpkg': has_command('dpkg'),
		'rpm': has_command('rpm'),
		'apt': has_command('apt-get') or has_command('apt'),
		'dnf': has_command('dnf'),
		'sudo': has_command('sudo'),
		'internet': internet_ok(),
	}

	# python version
	try:
		import sys
		checks['python_version'] = sys.version.split('\n')[0]
	except Exception:
		checks['python_version'] = None

	# venv availability
	try:
		import venv  # type: ignore
		checks['venv_module'] = True
	except Exception:
		checks['venv_module'] = False

	# GUI libs
	try:
		import gi  # type: ignore
		checks['gtk_available'] = True
	except Exception:
		checks['gtk_available'] = False

	try:
		import PySide6  # type: ignore
		checks['pyside6'] = True
	except Exception:
		checks['pyside6'] = False

	return checks


def write_report(checks: dict, path: str = 'openwork/reports/readiness.yml') -> None:
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, 'w') as f:
		yaml.safe_dump(checks, f)

