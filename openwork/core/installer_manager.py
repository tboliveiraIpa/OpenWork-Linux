import threading
import os
from typing import Callable, Optional
from .package_manager import AptPackageManager, DnfPackageManager
from .executor import Executor


class InstallerManager:
    def __init__(self, system_info: dict = None):
        self.executor = Executor()
        self.pm = None
        if system_info is None:
            try:
                from .system import get_distribution
                system_info = get_distribution()
            except Exception:
                system_info = {'family': 'debian'}

        family = system_info.get('family', 'debian')
        if family == 'rhel':
            self.pm = DnfPackageManager()
        else:
            self.pm = AptPackageManager()

    def install_module(self, module: dict, on_line: Optional[Callable[[str], None]] = None,
                       ask_password: Optional[Callable[[str], str]] = None) -> None:
        def _run():
            name = module.get('id') or module.get('name')
            if on_line:
                on_line(f"Starting install of {name}")

            inst = module.get('install', {}) or {}
            itype = inst.get('type')

            if itype in ('apt', 'deb'):
                packages = inst.get('packages') or []
                if packages:
                    if on_line:
                        on_line(f"Installing packages: {' '.join(packages)}")
                    ok = self.pm.install(packages, on_line=on_line, ask_password=ask_password)
                    if ok:
                        if on_line:
                            on_line(f"Installed packages: {' '.join(packages)}")
                    else:
                        if on_line:
                            on_line(f"Failed to install packages: {' '.join(packages)}")
                else:
                    # fallback to local script
                    script = os.path.join(module.get('_path', ''), 'install.sh')
                    if os.path.exists(script):
                        self.executor.run_interactive(script, cwd=module.get('_path'), on_line=on_line, on_request_password=ask_password)
                    else:
                        if on_line:
                            on_line('No install instructions found')
            elif itype == 'custom':
                script = os.path.join(module.get('_path', ''), 'install.sh')
                if os.path.exists(script):
                    self.executor.run_interactive(script, cwd=module.get('_path'), on_line=on_line, on_request_password=ask_password)
                else:
                    if on_line:
                        on_line('No custom installer found')
            else:
                # default: try script
                script = os.path.join(module.get('_path', ''), 'install.sh')
                if os.path.exists(script):
                    self.executor.run_interactive(script, cwd=module.get('_path'), on_line=on_line, on_request_password=ask_password)
                else:
                    if on_line:
                        on_line('Unsupported install type or no installer available')

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def validate_module(self, module: dict, on_line: Optional[Callable[[str], None]] = None,
                        ask_password: Optional[Callable[[str], str]] = None) -> None:
        def _run():
            name = module.get('id') or module.get('name')
            if on_line:
                on_line(f"Validating {name}")
            val = module.get('validate', {}) or {}
            vtype = val.get('type')
            if vtype == 'script':
                script = os.path.join(module.get('_path', ''), val.get('path', 'validate.sh'))
                if os.path.exists(script):
                    self.executor.run_interactive(script, cwd=module.get('_path'), on_line=on_line, on_request_password=ask_password)
                else:
                    if on_line:
                        on_line('Validate script not found')
            else:
                # run simple status checks
                checks = module.get('status_checks') or []
                for c in checks:
                    cmd = c.get('command') if isinstance(c, dict) else c
                    if on_line:
                        on_line(f"Checking: {cmd}")
                    rc = os.system(cmd)
                    if on_line:
                        on_line(f"Command exit: {rc}")

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def install_modules(self, modules_list: list, on_line: Optional[Callable[[str], None]] = None,
                        ask_password: Optional[Callable[[str], str]] = None) -> None:
        """Install a list of module dicts sequentially in a background thread."""
        def _run():
            for module in modules_list:
                name = module.get('id') or module.get('name')
                if on_line:
                    on_line(f"=== Installing module {name} ===")

                inst = module.get('install', {}) or {}
                itype = inst.get('type')

                if itype in ('apt', 'deb'):
                    packages = inst.get('packages') or []
                    if packages:
                        if on_line:
                            on_line(f"Installing packages: {' '.join(packages)}")
                        ok = self.pm.install(packages, on_line=on_line, ask_password=ask_password)
                        if ok:
                            if on_line:
                                on_line(f"Installed packages: {' '.join(packages)}")
                        else:
                            if on_line:
                                on_line(f"Failed to install packages: {' '.join(packages)}")
                    else:
                        script = os.path.join(module.get('_path', ''), 'install.sh')
                        if os.path.exists(script):
                            self.executor.run_interactive(script, cwd=module.get('_path'), on_line=on_line, on_request_password=ask_password)
                        else:
                            if on_line:
                                on_line('No install instructions found')
                else:
                    script = os.path.join(module.get('_path', ''), 'install.sh')
                    if os.path.exists(script):
                        self.executor.run_interactive(script, cwd=module.get('_path'), on_line=on_line, on_request_password=ask_password)
                    else:
                        if on_line:
                            on_line('Unsupported install type or no installer available')

                if on_line:
                    on_line(f"=== Finished {name} ===")

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def install_profile(self, profile: dict, modules_map: dict, on_line: Optional[Callable[[str], None]] = None,
                        ask_password: Optional[Callable[[str], str]] = None) -> None:
        """Install all modules referenced by a profile. `modules_map` is id->module dict."""
        module_ids = profile.get('modules') or []
        modules_to_install = []
        for mid in module_ids:
            m = modules_map.get(mid)
            if m:
                modules_to_install.append(m)
            else:
                if on_line:
                    on_line(f"Profile references unknown module: {mid}")

        if not modules_to_install:
            if on_line:
                on_line('No modules to install for profile')
            return

        self.install_modules(modules_to_install, on_line=on_line, ask_password=ask_password)
