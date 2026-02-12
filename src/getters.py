import json
import tomllib
from pathlib import Path

class configGetter:
    def __init__(self):
        with open("config.toml", "rb") as f:
            self.config = tomllib.load(f)
        self.project_root = Path(__file__).resolve().parent.parent
        
    def get_film_path(self):
        relative_parts = Path(self.config["mediaFilePaths"]["filmFilePath"])
        video_path = self.project_root / "inputMedia" / relative_parts
        assert video_path.exists(), f"❌ Movie not found at {video_path}"
        return str(video_path)
    def get_test_path(self):
        video_path = self.project_root / "inputMedia" / "test.mkv"
        assert video_path.exists(), f"❌ Movie not found at {video_path}"
        return str(video_path)
config = configGetter()
