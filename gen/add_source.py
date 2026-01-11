import os
from pathlib import Path
import json
import ffmpeg
from exifread import process_file
from exifread.core.ifd_tag import IfdTag
from datetime import datetime
from PIL import Image
from pillow_heif import read_heif

TARGET_DIR = Path("C:\\Users\\elfia\\OneDrive\\Desktop\\🌸Japan Trip Dump - test")

BASE_DIR = Path(os.path.dirname(__file__)).parent
WEB_SOURCE_DIR = BASE_DIR / "web-source"

def main() -> None:
	pass

def add_file_to_source(file_path: Path, user: str = "default", extra_tags = []):
	print("processing " + str(file_path))
	# Make asset dir
	asset_dir = WEB_SOURCE_DIR / "assets"
	asset_dir.mkdir(exist_ok=True, parents=True)
	
	# Make specific user dir
	user_dir = asset_dir / user
	user_dir.mkdir(exist_ok=True, parents=True)
	
	# Prep data
	data = {
		"name": file_path.name,
		"dm": file_path.stat().st_mtime, # date_modifed
		"dc": file_path.stat().st_ctime, # date_created
		"user": user,
		"tags": extra_tags,
		"custom_data":{}
	}

	# Copy file over
	with open(file_path, "rb") as f:
		gps_data: dict = {}
		date_taken: datetime = None
		file_ext = file_path.suffix.lower()
		
		if file_ext in [".jpg", ".jpeg", ".png", ".heic"]:
			tags = process_file(f)
			_date_taken_string = tags.get("Image DateTime")
			if _date_taken_string is not None:
				date_taken = datetime.strptime(str(_date_taken_string), "%Y:%m:%d %H:%M:%S")

			lat: IfdTag = tags.get("GPS GPSLatitude", None)
			lon: IfdTag = tags.get("GPS GPSLongitude", None)
			alt: IfdTag = tags.get("GPS GPSAltitude", None)
			if lat is not None: gps_data["lat"] = [float(lat.values[0]), float(lat.values[1]), float(lat.values[2])]
			if lon is not None: gps_data["lon"] = [float(lon.values[0]), float(lon.values[1]), float(lon.values[2])]
			if alt is not None: gps_data["alt"] = float(alt.values[0])

		elif file_ext in [".mp4", ".mov", ".avi", ".mkv"]:
			vid = ffmpeg.probe(file_path)
			for stream in (vid["streams"] + [vid["format"]]):
				tags = stream.get("tags")
				if tags is not None:
					_ct_string: str = tags.get("creation_time")
					date_taken = datetime.fromisoformat(_ct_string)
		
		if gps_data: data["gps"] = gps_data
		if date_taken: data["dt"] = date_taken.timestamp() 
		
		if gps_data: print(" >GPS✅")
		else: print(" >GPS❌")
		if date_taken: print(" >DT✅")
		else: print(" >DT❌")
		
		f.seek(0)
		with open(user_dir / file_path.name, "wb") as g:
			g.write(f.read())
		with open(user_dir / (file_path.name + ".json"), "w", encoding='utf-8') as h:
			json.dump(data, h)

def create_index() -> None:
	asset_dir = WEB_SOURCE_DIR / "assets"
	index_data = {
		"asset": {}
	}
	for root, _dirs, filenames in os.walk(asset_dir):
		for file in filenames:
			filepath = Path(root, file)
			if filepath.suffix == ".json":
				rel_path = filepath.relative_to(asset_dir)
				index_data["asset"][str(rel_path)] = json.load(open(filepath))
	
	index_path = WEB_SOURCE_DIR / "index.json"
	with open(index_path, "w") as f:
		json.dump(index_data, f)

def create_thumbnails(size = (1, 1)):
	asset_dir = WEB_SOURCE_DIR / "assets"
	thumb_dir = WEB_SOURCE_DIR / "thumbs"
	
	thumb_dir.mkdir(exist_ok=True, parents=True)
	for root, dirs, filenames in os.walk(asset_dir):
		for file in filenames:
			original_filepath = Path(root, file)
			file_ext = original_filepath.suffix.lower()
			print(original_filepath)
			
			filepath = thumb_dir / Path(root, file).relative_to(asset_dir).with_suffix(".jpg")
			filepath.parent.mkdir(exist_ok=True, parents=True)

			if file_ext in [".jpg", ".jpeg", ".png"]:
				with Image.open(original_filepath) as img:
					img.thumbnail(size, Image.Resampling.LANCZOS)
					img.save(filepath, "JPEG")
			elif file_ext in [".heic"]:
				heif_file = read_heif(original_filepath)
				with Image.frombytes(
						heif_file.mode,
						heif_file.size,
						heif_file.data,
						"raw",
					) as img:
					img.thumbnail(size, Image.Resampling.LANCZOS)
					img.save(filepath, "JPEG")
			elif file_ext in [".mp4", ".mov", ".avi", ".mkv"]:
				(
					ffmpeg
					.input(original_filepath, ss=4)	# Seek to time first (faster)
					.filter('scale', size[0], -1)	# Scale to width, keep aspect ratio
					.output(str(filepath), vframes=1)	# Extract exactly 1 frame
					.overwrite_output()
					.run(capture_stdout=True, capture_stderr=True)
				)

def import_assets():
	for file in (TARGET_DIR / "👨‍💼Elfiyan" / "📷Camera").iterdir(): add_file_to_source(file, "elfi")
	
	for file in (TARGET_DIR / "👨‍🔧Patrick" / "📷Camera" / "Day 1").iterdir(): add_file_to_source(file, "pat", ["day_1"])
	for file in (TARGET_DIR / "👨‍🔧Patrick" / "📷Camera" / "Day 2").iterdir(): add_file_to_source(file, "pat", ["day_2"])
	for file in (TARGET_DIR / "👨‍🔧Patrick" / "📷Camera" / "Day 3").iterdir(): add_file_to_source(file, "pat", ["day_3"])
	for file in (TARGET_DIR / "👨‍🔧Patrick" / "📷Camera" / "Day 4").iterdir(): add_file_to_source(file, "pat", ["day_4"])
	for file in (TARGET_DIR / "👨‍🔧Patrick" / "📷Camera" / "Day 5").iterdir(): add_file_to_source(file, "pat", ["day_5"])
	for file in (TARGET_DIR / "👨‍🔧Patrick" / "📷Camera" / "Day 6").iterdir(): add_file_to_source(file, "pat", ["day_6"])
	for file in (TARGET_DIR / "👨‍🔧Patrick" / "📷Camera" / "Day 7").iterdir(): add_file_to_source(file, "pat", ["day_7"])
	for file in (TARGET_DIR / "👨‍🔧Patrick" / "📷Camera" / "Day 8").iterdir(): add_file_to_source(file, "pat", ["day_8"])
	
	for file in (TARGET_DIR / "👨‍🔬Wei Hao" / "📷Camera" ).iterdir(): add_file_to_source(file, "wh")
	

if __name__ == "__main__":
	# import_assets()
	# create_index()
	create_thumbnails()

