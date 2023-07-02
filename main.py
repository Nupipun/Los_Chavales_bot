import discord
from LCBot import LCBot
import logging
from logging.handlers import RotatingFileHandler
import colorlog
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)

TOKEN = os.getenv("TOKEN")

file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s: %(message)s")

console_formatter = colorlog.ColoredFormatter(
    "%(asctime)s %(log_color)s%(levelname)s - %(name)s: %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red"
    },
    reset=True,
    style="%"
)
try:
    file_handler = RotatingFileHandler(filename="logs/logs.log", encoding="utf-8", mode="a",
                                       maxBytes=20 * 1024 * 1024, backupCount=5)
except FileNotFoundError:
    os.mkdir("logs")
    file_handler = RotatingFileHandler(filename="logs/logs.log", encoding="utf-8", mode="a",
                                       maxBytes=20 * 1024 * 1024, backupCount=5)
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

intents = discord.Intents.all()

client = LCBot(logger, intents=intents)
client.run(TOKEN, log_handler=None)
