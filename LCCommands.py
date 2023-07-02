from discord.app_commands import CommandTree
from LCMusicCommands import LCMusicCommands
from discord.app_commands import checks
import discord_embeds as embeds
import discord
import typing


class LCCommands(LCMusicCommands, CommandTree):
    def __init__(self, client):
        super().__init__(client)

        @self.command(name="ping")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("Pong!")

        @self.command(name="help")
        async def help(interaction: discord.Interaction):
            await interaction.response.send_message(embed=embeds.help_embed())

        @checks.has_permissions(administrator=True)
        @self.command(name="announce")
        async def announce(interaction: discord.Interaction,
                           channel: discord.TextChannel,
                           message: str,
                           is_everyone: typing.Optional[bool] = False):
            if is_everyone:
                everyone_msg = "@everyone\n\n"
            else:
                everyone_msg = ""

            allowed_mentions = discord.AllowedMentions(everyone=is_everyone)
            await channel.send(everyone_msg, embed=embeds.announcement_embed(message, is_everyone),
                               allowed_mentions=allowed_mentions)
            await interaction.response.send_message("Announcement sent.", ephemeral=True)

        # Error handling
        @announce.error
        async def announce_error(interaction: discord.Interaction, error):
            await interaction.response.send_message(error, ephemeral=True)
