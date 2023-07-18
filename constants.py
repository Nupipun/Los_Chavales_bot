import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
WELCOME_CHANNEL_ID = 1119197039553675295
YOUTUBE_CHANNEL_ID = "UCvH7CJqcP5mW411eAE8KqZQ"
YOUTUBE_FEED_CHANNEL_ID = 1121936232247742556
WAVELINK_URI = os.getenv("WAVELINK_URI")
WAVELINK_PASS = os.getenv("WAVELINK_PASS")
SERVER_NAME = "The Rhythm Hub"
DURO_IMG_PATH = os.path.join("images", "duro_images")
GATO_IMG_PATH = os.path.join("images", "gato_images")
BORZOI_IMG_PATH = os.path.join("images", "borzoi_images")
LMAO_IMG_PATH = os.path.join("images", "lmao_images")
