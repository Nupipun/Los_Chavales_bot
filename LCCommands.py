from discord.app_commands import CommandTree
from LCMusicCommands import LCMusicCommands
import discord


class LCCommands(LCMusicCommands, CommandTree):
    def __init__(self, client):
        super().__init__(client)

        @self.command(name="ping")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("Pong!")
