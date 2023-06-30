from discord.app_commands import CommandTree
from constants import *
import discord
from card_image_logic import create_welcome_card
from io import BytesIO
from youtube_upload_detection import SearchForNewVideo
from discord.ext import tasks
import wavelink
import subprocess
import time
from threading import Thread
import os

class LCCommands(CommandTree):
    def __init__(self, client):
        super().__init__(client)
        node = wavelink.NodePool.get_node()

        # TODO Crear comando /queue
        # TODO Crear comando /skip

        @self.command(name="ping")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("Pong!")

        # TODO Crear queue
        @self.command(name="play")
        async def play(interaction: discord.Interaction, search: str):
            player = node.get_player(interaction.guild_id)
            print(player)
            print(node.players)

            tracks = await wavelink.YouTubeTrack.search(search)
            if not tracks:
                await interaction.response.send_message("this track was not found")
                return

            track = tracks[0]
            try:
                await player.play(track)
            except AttributeError:
                await interaction.response.send_message("Please use /connect first!")
            # TODO mejorar esto
            embed = discord.Embed(
                title="**Now playing**",
                description=f"Track: {track}\nLink: {track.uri}"
            )
            await interaction.response.send_message(embed=embed)

        @self.command(name="stop")
        async def stop(interaction: discord.Interaction):
            player = node.get_player(interaction.guild.id)
            if not player.is_playing:
                await interaction.response.send_message("No track is currently playing")
                return

            await player.stop()
            await interaction.response.send_message("Playback stopped.")

        @self.command(name="connect")
        async def connect(interaction: discord.Interaction):
            try:
                channel = interaction.user.voice.channel
            except AttributeError:
                return await interaction.response.send_message("No voice channel to connect to.")

            vc: wavelink.Player = await channel.connect(cls=wavelink.Player)
            await interaction.response.send_message(f"Joined voice channel {channel.name}")
            return vc

        @self.command(name="disconnect")
        async def connect(interaction: discord.Interaction):
            for x in client.voice_clients:
                await interaction.response.send_message("Disconnecting from the channel...")
                return await x.disconnect()

            return await interaction.response.send_message(
                "I am not connected to any voice channel on this server!",
                ephemeral=True
            )


class LCBot(discord.Client):
    async def on_ready(self):
        print(f"{self.user.name} is working.")
        try:
            print("Syncing commands...")
            print("Starting wavelink...")
            t1 = Thread(self.start_lavalink())
            t1.start()
            time.sleep(4)
            node: wavelink.Node = wavelink.Node(uri="http://localhost:2333", password="youshallnotpass")
            await wavelink.NodePool.connect(client=self, nodes=[node])
            print(node.players)
            tree = LCCommands(self)
            synced = await tree.sync()
            print(f"Synced {len(synced)} command(s)")


            # await self.check_new_video.start()
        except Exception as e:
            print(e)

    @staticmethod
    def start_lavalink():
        os.chdir("lavalink")
        subprocess.Popen("java -jar Lavalink.jar")

    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"wavelink node ready. id: {node.id}")

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

    # @tasks.loop(minutes=5, reconnect=True)
    # async def check_new_video(self):
    #     video = SearchForNewVideo()
    #     link, title = video.check_new_video()
    #     if link != "null" and title != "null":
    #         print("new video upload detected")
    #         channel = await self.fetch_channel(YOUTUBE_FEED_CHANNEL_ID)
    #         await channel.send(f"New video uploaded on the channel!\n{title}\n{link}")
    #     else:
    #         print("no new videos uploaded")
