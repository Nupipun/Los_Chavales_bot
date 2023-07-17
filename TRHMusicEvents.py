import discord
import asyncio


class LCMusicEvents(discord.Client):
    @staticmethod
    async def start_lavalink():
        with open("logs/lavalink_logs.log", "a") as log_file:
            await asyncio.create_subprocess_exec(
                "java", "-jar", "Lavalink.jar", cwd="lavalink",
                stdout=log_file, stderr=log_file
            )

    async def on_wavelink_node_ready(self, node):
        self.logger.info(f"Wavelink node ready. ID: '{node.id}'")
