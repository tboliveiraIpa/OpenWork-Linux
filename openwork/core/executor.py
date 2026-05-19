import subprocess
import threading
from typing import Callable, Optional


class Executor:
	def __init__(self):
		pass
	def run(self, command: str, cwd: Optional[str] = None, on_line: Optional[Callable[[str], None]] = None) -> int:
		"""Run a command and stream stdout/stderr lines to `on_line`.
		Blocks until completion and returns the exit code."""
		proc = subprocess.Popen(command, shell=True, executable='/bin/bash', cwd=cwd,
								stdin=subprocess.DEVNULL,
								stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
								bufsize=1, universal_newlines=True)

		def reader():
			assert proc.stdout is not None
			try:
				for line in proc.stdout:
					if on_line:
						on_line(line.rstrip())
			except Exception:
				pass

		t = threading.Thread(target=reader, daemon=True)
		t.start()
		proc.wait()
		t.join(timeout=2.0)
		return proc.returncode

	def run_interactive(self, command: str, cwd: Optional[str] = None,
						on_line: Optional[Callable[[str], None]] = None,
						on_request_password: Optional[Callable[[str], str]] = None):
		"""Run a command with stdin open. Streams output to `on_line`.

		If the subprocess prints a password prompt (contains 'password'), and
		`on_request_password` is provided, it will be called with the prompt
		text and should return the password string (without newline). The
		password will be written to the process stdin followed by a newline.
		Returns the process exit code.
		"""
		import os
		# Ensure apt doesn't use pager and shows progress
		env = os.environ.copy()
		env['DEBIAN_FRONTEND'] = 'noninteractive'
		env['APT_LISTCHANGES_FRONTEND'] = 'text'
		
		proc = subprocess.Popen(command, shell=True, executable='/bin/bash', cwd=cwd,
								stdin=subprocess.PIPE,
								stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
								bufsize=1, universal_newlines=True, env=env)

		def reader():
			assert proc.stdout is not None
			try:
				for line in proc.stdout:
					text = line.rstrip()
					if on_line:
						on_line(text)
					# detect sudo-like password prompts
					low = text.lower()
					if ('password' in low or 'senha' in low) and on_request_password:
						try:
							pw = on_request_password(text)
							if pw is not None and proc.stdin:
								proc.stdin.write(pw + "\n")
								proc.stdin.flush()
						except Exception:
							# ignore prompt failures
							pass
			except Exception:
				pass

		t = threading.Thread(target=reader, daemon=True)
		t.start()
		proc.wait()
		# Wait for reader thread to finish flushing buffered output
		t.join(timeout=2.0)
		# close stdin
		try:
			if proc.stdin:
				proc.stdin.close()
		except Exception:
			pass
		return proc.returncode

