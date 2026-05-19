
try:
	from PySide6 import QtWidgets, QtCore, QtGui
	from functools import partial
	import os
	import threading
	from typing import Optional


	class TerminalDialog(QtWidgets.QDialog):
		"""Modal dialog that displays command output in a terminal-like widget."""
		def __init__(self, title: str, parent=None):
			super().__init__(parent)
			self.setWindowTitle(title)
			self.resize(800, 500)
			self.setModal(True)

			layout = QtWidgets.QVBoxLayout(self)

			# Terminal-like output area
			self.output = QtWidgets.QTextEdit()
			self.output.setReadOnly(True)
			self.output.setStyleSheet("""
				QTextEdit {
					background-color: #1e1e1e;
					color: #00ff00;
					font-family: 'Courier New', monospace;
					font-size: 10pt;
					padding: 8px;
					border: 1px solid #333;
				}
			""")
			layout.addWidget(self.output)

			# Close button
			btn_close = QtWidgets.QPushButton('Fechar')
			btn_close.clicked.connect(self.accept)
			layout.addWidget(btn_close)

		def append_line(self, text: str):
			"""Append a line to the terminal output."""
			self.output.append(text)
			# auto-scroll to bottom
			scrollbar = self.output.verticalScrollBar()
			scrollbar.setValue(scrollbar.maximum())


	class MainWindow(QtWidgets.QMainWindow):
		def __init__(self, modules, profiles, logger, installer=None):
			super().__init__()
			self.setWindowTitle('OpenWork Linux')
			self.resize(920, 640)

			central = QtWidgets.QWidget()
			self.setCentralWidget(central)
			main_layout = QtWidgets.QVBoxLayout(central)

			self.logger = logger
			self.installer = installer
			self.modules = modules
			self.profiles = profiles
			self.modules_by_id = {m.get('id'): m for m in modules}

			# stacked pages
			self.stack = QtWidgets.QStackedWidget()

			# Landing page
			landing = QtWidgets.QWidget()
			landing_layout = QtWidgets.QVBoxLayout(landing)
			landing_layout.setAlignment(QtCore.Qt.AlignCenter)

			logo_label = QtWidgets.QLabel()
			logo_label.setAlignment(QtCore.Qt.AlignCenter)
			project_logo = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'openwork-logo.png'))
			if os.path.exists(project_logo):
				pix = QtGui.QPixmap(project_logo)
			else:
				svg_logo = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'openwork-logo.svg'))
				pix = QtGui.QPixmap(svg_logo) if os.path.exists(svg_logo) else QtGui.QPixmap()
			if not pix.isNull():
				logo_label.setPixmap(pix.scaledToHeight(280, QtCore.Qt.SmoothTransformation))
			else:
				logo_label.setText('OpenWork Linux')

			desc = QtWidgets.QLabel('OpenWork Linux — Preparação de Workstations para SAP + Microsoft')
			desc.setAlignment(QtCore.Qt.AlignCenter)
			desc.setWordWrap(True)

			btn_profile = QtWidgets.QPushButton('Instalar por Perfil')
			btn_modules = QtWidgets.QPushButton('Instalar por Módulos')
			btn_profile.setFixedHeight(52)
			btn_modules.setFixedHeight(52)

			landing_layout.addWidget(logo_label)
			landing_layout.addSpacing(8)
			landing_layout.addWidget(desc)
			landing_layout.addSpacing(12)
			landing_layout.addWidget(btn_profile)
			landing_layout.addWidget(btn_modules)

			self.stack.addWidget(landing)

			# Modules page
			modules_page = QtWidgets.QWidget()
			m_layout = QtWidgets.QHBoxLayout(modules_page)

			left = QtWidgets.QWidget()
			left_layout = QtWidgets.QVBoxLayout(left)
			left_layout.addWidget(QtWidgets.QLabel('Instalar Módulos'))
			scroll = QtWidgets.QScrollArea()
			scroll.setWidgetResizable(True)
			scroll_content = QtWidgets.QWidget()
			scroll_layout = QtWidgets.QVBoxLayout(scroll_content)

			self.module_buttons = []
			for m in modules:
				row = QtWidgets.QWidget()
				rl = QtWidgets.QHBoxLayout(row)
				lbl = QtWidgets.QLabel(m.get('name'))
				btn_cfg = QtWidgets.QPushButton('Config')
				btn_val = QtWidgets.QPushButton('Validar')
				btn_inst = QtWidgets.QPushButton('Instalar')
				rl.addWidget(lbl)
				rl.addStretch()
				rl.addWidget(btn_cfg)
				rl.addWidget(btn_val)
				rl.addWidget(btn_inst)
				scroll_layout.addWidget(row)
				self.module_buttons.append((m, btn_inst, btn_val, btn_cfg))

			scroll_layout.addStretch()
			scroll_content.setLayout(scroll_layout)
			scroll.setWidget(scroll_content)
			left_layout.addWidget(scroll)
			m_layout.addWidget(left, 1)

			# logs on right
			self.log_view = QtWidgets.QTextEdit()
			self.log_view.setReadOnly(True)
			m_layout.addWidget(self.log_view, 2)

			self.stack.addWidget(modules_page)

			# Profiles page
			profiles_page = QtWidgets.QWidget()
			p_layout = QtWidgets.QHBoxLayout(profiles_page)
			self.profile_list = QtWidgets.QListWidget()
			self.profile_modules_list = QtWidgets.QListWidget()
			left_p = QtWidgets.QVBoxLayout()
			left_p.addWidget(QtWidgets.QLabel('Perfis'))
			left_p.addWidget(self.profile_list)
			right_p = QtWidgets.QVBoxLayout()
			right_p.addWidget(QtWidgets.QLabel('Módulos do perfil'))
			right_p.addWidget(self.profile_modules_list)
			self.btn_install_profile = QtWidgets.QPushButton('Instalar Perfil')
			right_p.addWidget(self.btn_install_profile)
			p_layout.addLayout(left_p, 1)
			p_layout.addLayout(right_p, 2)

			self.stack.addWidget(profiles_page)

			# add stack and back button
			main_layout.addWidget(self.stack)
			self.btn_back = QtWidgets.QPushButton('Voltar')
			self.btn_back.setVisible(False)
			main_layout.addWidget(self.btn_back)

			# populate profiles
			for p in profiles:
				it = QtWidgets.QListWidgetItem(p.get('name', p.get('_path', 'unknown')))
				it.setData(QtCore.Qt.UserRole, p)
				self.profile_list.addItem(it)

			# wire signals
			btn_profile.clicked.connect(lambda: self._show_page(profiles_page))
			btn_modules.clicked.connect(lambda: self._show_page(modules_page))
			self.btn_back.clicked.connect(lambda: self._show_page(landing))
			self.profile_list.currentItemChanged.connect(self._on_profile_selected)
			self.btn_install_profile.clicked.connect(self._on_install_profile)

			for m, btn_inst, btn_val, btn_cfg in self.module_buttons:
				btn_inst.clicked.connect(partial(self._install_module, m))
				btn_val.clicked.connect(partial(self._validate_module, m))
				btn_cfg.clicked.connect(partial(self._open_config_dialog, m))

		def _show_page(self, widget):
			self.stack.setCurrentWidget(widget)
			self.btn_back.setVisible(widget is not self.stack.widget(0))

		def _install_module(self, module):
			if not self.installer:
				self.append_log('Installer não disponível')
				return

			name = module.get('name')
			term = TerminalDialog(f"Instalando: {name}", parent=self)
			term.append_line(f">>> Iniciando instalação: {name}")
			term.append_line("")

			self.installer.install_module(module, on_line=term.append_line, ask_password=self._ask_sudo_password)
			term.exec()

		def _validate_module(self, module):
			if not self.installer:
				self.append_log('Installer não disponível')
				return

			name = module.get('name')
			term = TerminalDialog(f"Validando: {name}", parent=self)
			term.append_line(f">>> Iniciando validação: {name}")
			term.append_line("")

			self.installer.validate_module(module, on_line=term.append_line, ask_password=self._ask_sudo_password)
			term.exec()

		def _on_profile_selected(self, current, previous):
			self.profile_modules_list.clear()
			if not current:
				return
			profile = current.data(QtCore.Qt.UserRole)
			for mid in profile.get('modules', []):
				m = self.modules_by_id.get(mid)
				if m:
					self.profile_modules_list.addItem(m.get('name'))
				else:
					self.profile_modules_list.addItem(f"{mid} (missing)")

		def _open_config_dialog(self, module):
			scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
			scripts = []
			if os.path.isdir(scripts_dir):
				for fn in os.listdir(scripts_dir):
					if fn.endswith('.sh') or fn.endswith('.py'):
						if module.get('id') in fn or any(k in fn for k in ['sap', 'forti', 'teams', 'brave', 'pwa', 'onedrive', 'outlook']):
							scripts.append(os.path.join(scripts_dir, fn))

			dlg = QtWidgets.QDialog(self)
			dlg.setWindowTitle(f"Configurações: {module.get('name')}")
			dlg.setModal(True)
			layout = QtWidgets.QVBoxLayout(dlg)
			listw = QtWidgets.QListWidget()
			for s in scripts:
				listw.addItem(os.path.basename(s))
			layout.addWidget(listw)
			btn_run = QtWidgets.QPushButton('Executar script selecionado')
			layout.addWidget(btn_run)
			btn_close = QtWidgets.QPushButton('Fechar')
			layout.addWidget(btn_close)

			def _run_selected():
				it = listw.currentItem()
				if not it:
					self.append_log('Nenhum script selecionado')
					return
				script_path = os.path.join(scripts_dir, it.text())
				self.append_log(f'Executando script de configuração: {it.text()}')
				if self.installer and hasattr(self.installer, 'executor'):
					self.installer.executor.run_interactive(script_path, cwd=scripts_dir, on_line=self.append_log, on_request_password=self._ask_sudo_password)
				else:
					import subprocess
					subprocess.Popen(['bash', script_path])

			btn_run.clicked.connect(_run_selected)
			btn_close.clicked.connect(dlg.accept)
			dlg.exec()

		def _on_install_profile(self):
			it = self.profile_list.currentItem()
			if not it or not self.installer:
				self.append_log('Nenhum perfil selecionado ou instalador ausente')
				return
			profile = it.data(QtCore.Qt.UserRole)

			name = profile.get('name', 'Perfil')
			term = TerminalDialog(f"Instalando Perfil: {name}", parent=self)
			term.append_line(f">>> Iniciando instalação do perfil: {name}")
			term.append_line("")

			self.installer.install_profile(profile, self.modules_by_id, on_line=term.append_line, ask_password=self._ask_sudo_password)
			term.exec()

		def _ask_sudo_password(self, prompt: str) -> Optional[str]:
			# If called from GUI thread, show dialog directly
			if QtCore.QThread.currentThread() == self.thread():
				pw, ok = QtWidgets.QInputDialog.getText(self, 'Senha sudo', prompt, QtWidgets.QLineEdit.Password)
				return pw if ok else None

			# Called from a background thread: schedule dialog on GUI thread and wait
			res = {'pw': None}
			evt = threading.Event()

			def run_dialog():
				pw, ok = QtWidgets.QInputDialog.getText(self, 'Senha sudo', prompt, QtWidgets.QLineEdit.Password)
				if ok:
					res['pw'] = pw
				evt.set()

			QtCore.QTimer.singleShot(0, run_dialog)
			evt.wait()
			return res.get('pw')

		def append_log(self, line: str):
			self.log_view.append(line)

except Exception:
	class MainWindow:
		def __init__(self, modules, profiles, logger, installer=None):
			raise RuntimeError('PySide6 not available')

