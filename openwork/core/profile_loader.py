import os
import yaml
from typing import Dict, List


def load_profiles(profiles_dir: str = 'openwork/profiles') -> List[Dict]:
	results = []
	if not os.path.isdir(profiles_dir):
		return results
	for name in os.listdir(profiles_dir):
		if name.endswith('.yml') or name.endswith('.yaml'):
			path = os.path.join(profiles_dir, name)
			try:
				with open(path, 'r') as f:
					data = yaml.safe_load(f)
					data['_path'] = path
					results.append(data)
			except Exception:
				continue
	return results

