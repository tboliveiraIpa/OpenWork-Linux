import sys
from .core.dependency_checker import run_checks, write_report
from .core.module_loader import load_modules
from .core.profile_loader import load_profiles
from .core.logger import Logger


def run_app():
	logger = Logger()
	logger.info('Starting OpenWork Linux')

	checks = run_checks()
	write_report(checks)
	logger.info('Wrote readiness report to openwork/reports/readiness.yml')

	modules = load_modules()
	profiles = load_profiles()
	from .core.installer_manager import InstallerManager
	installer = InstallerManager()
	# Try to launch GUI if available
	try:
		from .ui.main_window import MainWindow
		from PySide6 import QtWidgets

		app = QtWidgets.QApplication(sys.argv)
		win = MainWindow(modules, profiles, logger, installer=installer)
		# subscribe logger to GUI
		try:
			logger.subscribe(win.append_log)
		except Exception:
			pass
		win.show()
		sys.exit(app.exec())
	except Exception as e:
		logger.error(f'GUI not available: {e}')
		print('OpenWork readiness report written. GUI not available or failed to start.')
		print(f'GUI error: {e}')


if __name__ == '__main__':
	run_app()

