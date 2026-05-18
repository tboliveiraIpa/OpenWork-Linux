import os
from datetime import datetime
from typing import Callable, List


class Logger:
	def __init__(self, log_dir=None):
		self.subscribers: List[Callable[[str], None]] = []
		if log_dir is None:
			log_dir = os.path.expanduser('~/.local/state/openwork-linux/logs')
		self.log_dir = log_dir
		os.makedirs(self.log_dir, exist_ok=True)
		self.log_path = os.path.join(self.log_dir, datetime.now().strftime('%Y%m%d-%H%M%S') + '.log')

	def subscribe(self, cb: Callable[[str], None]):
		self.subscribers.append(cb)

	def info(self, msg: str):
		line = f"[INFO] {datetime.now().isoformat()} - {msg}"
		with open(self.log_path, 'a') as f:
			f.write(line + '\n')
		for s in self.subscribers:
			try:
				s(line)
			except Exception:
				pass

	def error(self, msg: str):
		line = f"[ERROR] {datetime.now().isoformat()} - {msg}"
		with open(self.log_path, 'a') as f:
			f.write(line + '\n')
		for s in self.subscribers:
			try:
				s(line)
			except Exception:
				pass

