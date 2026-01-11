import os
from pathlib import Path

BASE_DIR = Path(os.path.dirname(__file__)).parent
WEB_SOURCE_DIR = BASE_DIR / "web-source"

for root, dirs, files in os.walk(WEB_SOURCE_DIR):
	for file in files:
		filepath = Path(root, file)
		percentage_limit = (float(filepath.stat().st_size) / 1000000)
		if percentage_limit >= 0.99:
			print(percentage_limit)
			print(filepath)