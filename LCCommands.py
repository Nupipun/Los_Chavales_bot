from discord.app_commands import CommandTree
from LCMusicCommands import LCMusicCommands
from LCDuroCommands import LCDuroCommands
from discord.app_commands import checks
from youtube_upload_detection import SearchForNewVideo
from googleapiclient.errors import HttpError
import constants as const
import discord_embeds as embeds
import discord
import typing


class LCCommands(LCDuroCommands, LCMusicCommands, CommandTree):
    def __init__(self, client):
        super().__init__(client)

        @self.command(name="ping")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("Pong!")

        @self.command(name="help")
        async def help(interaction: discord.Interaction):
            await interaction.response.send_message(embed=embeds.help_embed())

        # ADMINISTRATOR COMMANDS
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
            self.logger.warning(error)

        @checks.has_permissions(administrator=True)
        @self.command(name="vidcheck")
        async def vidcheck(self):
            video = SearchForNewVideo()
            try:
                link, title = video.check_new_video()
            except HttpError as e:
                self.logger.error(e)
                return
            if link != "null" and title != "null":
                self.logger.info("New video upload detected.")
                channel = await self.fetch_channel(const.YOUTUBE_FEED_CHANNEL_ID)
                await channel.send(f"New video uploaded on the channel!\n{title}\n{link}")
            else:
                self.logger.debug("No new video upload detected.")

        @vidcheck.error
        async def vidcheck_error(self, error, interaction: discord.Interaction):
            await interaction.response.send_message(error, ephemeral=True)
            self.logger.error(error)
