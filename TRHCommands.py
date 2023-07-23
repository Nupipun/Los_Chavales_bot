from discord.app_commands import CommandTree
from TRHMusicCommands import LCMusicCommands
# from TRHDuroCommands import LCDuroCommands
from discord.app_commands import checks
from youtube_upload_detection import SearchForNewVideo
from googleapiclient.errors import HttpError
import constants as const
import discord_embeds as embeds
import discord
import typing
from io import BytesIO
from card_image_logic import create_welcome_card


class LCCommands(LCMusicCommands, CommandTree):
    def __init__(self, client):
        super().__init__(client)

        @self.command(name="ping")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("Pong!")

        @self.command(name="help")
        async def help(interaction: discord.Interaction, option: typing.Optional[str] = "general"):
            await interaction.response.send_message(embed=embeds.help_embed(option), ephemeral=True)

        @checks.has_permissions(administrator=True)
        @self.command(name="createwelcomecard")
        async def createwelcomecard(interaction: discord.Interaction, user: discord.User):
            channel = await client.fetch_channel(const.WELCOME_CHANNEL_ID)
            user_id = interaction.user.id

            user = await client.fetch_user(user_id)
            avatar_data = BytesIO(await user.display_avatar.read())

            card = create_welcome_card(user, avatar_data)

            file = discord.File(card, filename="welcome_card.png")
            msg = (
                f"Hello {interaction.user.mention} welcome to {const.SERVER_NAME}\n"
                f"\nHola {interaction.user.mention} bienvenido a {const.SERVER_NAME}!"
                )

            await channel.send(msg, file=file)

        # ADMINISTRATOR COMMANDS
        @checks.has_permissions(administrator=True)
        @self.command(name="announce")
        async def announce(interaction: discord.Interaction,
                           channel: discord.TextChannel,
                           message: str,
                           everyone: typing.Optional[bool] = False):

            allowed_mentions = discord.AllowedMentions(everyone=everyone)
            await channel.send("@everyone" if everyone else "", embed=embeds.announcement_embed(message, everyone),
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
