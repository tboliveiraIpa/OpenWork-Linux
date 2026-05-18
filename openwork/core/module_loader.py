import os
import yaml
from typing import Dict, List


def load_modules(modules_dir: str = 'openwork/modules') -> List[Dict]:
	results = []
	if not os.path.isdir(modules_dir):
		return results
	for name in os.listdir(modules_dir):
		path = os.path.join(modules_dir, name)
		if os.path.isdir(path):
			manifest = os.path.join(path, 'manifest.yml')
			if os.path.exists(manifest):
				try:
					with open(manifest, 'r') as f:
						data = yaml.safe_load(f)
						data['_path'] = path
						results.append(data)
				except Exception:
					continue
	return results

