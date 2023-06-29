from discord.app_commands import CommandTree
from constants import *
import discord
from card_image_logic import create_welcome_card
from io import BytesIO
from youtube_upload_detection import SearchForNewVideo
from discord.ext import tasks


class LCCommands(CommandTree):
    def __init__(self, client):
        super().__init__(client)

        @self.command(name="ping")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("Pong!")


class LCBot(discord.Client):
    async def on_ready(self):
        print(f"{self.user.name} is working.")
        try:
            print("Syncing commands...")
            tree = LCCommands(self)
            await self.check_new_video.start()
            synced = await tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    async def on_member_join(self, member: discord.Member):
        channel = await self.fetch_channel(WELCOME_CHANNEL_ID)
        user_id = member.id

        user = await self.fetch_user(user_id)
        avatar_data = BytesIO(await user.display_avatar.read())

        card = create_welcome_card(user, avatar_data)

        file = discord.File(card, filename="welcome_card.png")
        msg = f"Hello {member} welcome to Los Chavales!\n\nHola {member} bienvenido a Los Chavales!"

        await channel.send(msg, file=file)

    async def on_interaction(self, interaction: discord.Interaction):
        print(f"el usuario {interaction.user} ha ejecutado {interaction.data['name']}")

    @tasks.loop(seconds=30, reconnect=True)
    async def check_new_video(self):
        video = SearchForNewVideo()
        link, title = video.check_new_video()
        if link != "null" and title != "null":
            print("new video upload detected")
            channel = await self.fetch_channel(YOUTUBE_FEED_CHANNEL_ID)
            await channel.send(f"New video uploaded on the channel!\n{title}\n{link}")
        else:
            print("no new videos uploaded")
