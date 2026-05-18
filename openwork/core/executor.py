import subprocess
import threading
from typing import Callable, Optional


class Executor:
	def __init__(self):
		pass

	def run(self, command: str, cwd: Optional[str] = None, on_line: Optional[Callable[[str], None]] = None) -> int:
		proc = subprocess.Popen(command, shell=True, cwd=cwd,
								stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
								bufsize=1, universal_newlines=True)

		def reader():
			assert proc.stdout is not None
			for line in proc.stdout:
				if on_line:
					on_line(line.rstrip())

		t = threading.Thread(target=reader, daemon=True)
		t.start()
		proc.wait()
		t.join(timeout=0.1)
		return proc.returncode

