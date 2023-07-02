import asyncio
import typing
from discord.app_commands import CommandTree
from constants import *
import discord
from card_image_logic import create_welcome_card
from io import BytesIO
from youtube_upload_detection import SearchForNewVideo
from discord.ext import tasks
import wavelink


class LCCommands(CommandTree):
    def __init__(self, client):
        super().__init__(client)
        node = wavelink.NodePool.get_node()
        cola_link = []
        self.track = []

        @self.command(name="ping")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("Pong!")

        @self.command(name="queue")
        async def queue(interaction: discord.Interaction):
            player = node.get_player(interaction.guild_id)

            track_list = []
            try:
                if player.queue.count != 0:
                    contador = 0
                    for _ in range(player.queue.count):
                        contador += 1
                        cola_str = player.queue.get()
                        track_list.append(f"{'-' * 35}\n{contador}. Nombre: {cola_str}\nLink: {cola_link[_]}\n{'-' * 35}")
                        player.queue.put(cola_str)
                else:
                    track_list.append("No songs in the queue.")
                track_list_str = "\n".join(track_list)
            except AttributeError:
                embed = discord.Embed(
                    title="Not connected to a voicechat."
                )
            else:
                embed = discord.Embed(
                    title="**Current Queue**",
                    description=track_list_str
                )
            await interaction.response.send_message(embed=embed)

        @self.command(name="bump")
        async def bump(interaction: discord.Interaction, song_id: int):
            player = node.get_player(interaction.guild_id)
            try:
                await player.set_volume(player.volume)
            except AttributeError:
                embed = discord.Embed(
                    title="Not in a voicechannel."
                )
                await interaction.response.send_message(embed=embed)

            cola_str = None

            if song_id < 1 or song_id > player.queue.count:
                embed = discord.Embed(
                    title="The song id you inputted is not within the range of the queue."
                )
                await interaction.response.send_message(embed=embed)
                return

            if player.queue.count == 0:
                embed = discord.Embed(
                    title="No songs in the queue."
                )
                await interaction.response.send_message(embed=embed)
                return

            contador = 0
            for _ in range(song_id):
                contador += 1
                if contador == song_id:
                    cola_str = player.queue.get()
                    break
                else:
                    cola_str = player.queue.get()
                    player.queue.put(cola_str)

            player.queue.put_at_front(cola_str)
            embed = discord.Embed(
                title="Bump",
                description=f'Bumped **"{cola_str.title}"** to the top of the queue.'
            )
            await interaction.response.send_message(embed=embed)

        @self.command(name="play")
        async def play(interaction: discord.Interaction, search: str):
            player = node.get_player(interaction.guild_id)
            try:
                player.autoplay = True
            except AttributeError:
                await connect_logic(interaction)
                player = node.get_player(interaction.guild_id)
                player.autoplay = True

            tracks = await wavelink.YouTubeTrack.search(search)

            if not tracks:
                embed = discord.Embed(
                    title="This track was not found"
                )
                await interaction.response.send_message(embed=embed)
                return

            self.track = tracks[0]

            if not player.is_playing():
                await player.play(self.track)
                embed = discord.Embed(
                    title="**Now playing**",
                    description=f"Track: {self.track}\nLink: {self.track.uri}"
                )
            else:
                player.queue.put(self.track)
                cola_link.append(self.track.uri)
                embed = discord.Embed(
                    title="**Added to queue**",
                    description=f"Track: {self.track}\nLink: {self.track.uri}"
                )
            await interaction.response.send_message(embed=embed)

        @self.command(name="nowplaying")
        async def nowplaying(interaction: discord.Interaction):
            try:
                embed = discord.Embed(
                    title="**Now playing**",
                    description=f"Track: {self.track}\nLink: {self.track.uri}"
                )
            except AttributeError:
                embed = discord.Embed(
                    title="**Now playing**",
                    description=f"There are no tracks playing right now."
                )
            await interaction.response.send_message(embed=embed)

        @self.command(name="skip")
        async def skip(interaction: discord.Interaction):
            player = node.get_player(interaction.guild_id)
            embed = discord.Embed(
                title="Skipping track..."
            )
            try:
                await player.stop()
                await interaction.response.send_message(embed=embed)
            except AttributeError:
                embed = discord.Embed(
                    title="Not connected to a voicechat."
                )
                await interaction.response.send_message(embed=embed)

        @self.command(name="stop")
        async def stop(interaction: discord.Interaction):
            player = node.get_player(interaction.guild.id)
            if not player.is_playing:
                await interaction.response.send_message("No track is currently playing")
                return
            for _ in range(player.queue.count):
                player.queue.pop()
            self.track = []
            await player.stop()
            await interaction.response.send_message("Playback stopped.")

        @self.command(name="connect")
        async def connect(interaction: discord.Interaction):
            try:
                channel = interaction.user.voice.channel
            except AttributeError:
                return await interaction.response.send_message("No voice channel to connect to.")

            await interaction.response.send_message(f"Connected to channel **{channel.name}**")
            vc: wavelink.Player = await channel.connect(cls=wavelink.Player)
            return vc

        @self.command(name="disconnect")
        async def connect(interaction: discord.Interaction):
            player = node.get_player(interaction.guild.id)

            for _ in range(player.queue.count):
                player.queue.pop()

            await player.stop()

            for x in client.voice_clients:
                await interaction.response.send_message("Disconnecting from the channel...")
                return await x.disconnect()

            return await interaction.response.send_message(
                "I am not connected to any voice channel on this server!",
                ephemeral=True
            )

        @self.command(name="volume")
        async def volume(interaction: discord.Interaction, volume_number: int):
            player = node.get_player(interaction.guild_id)
            try:
                await player.set_volume(volume_number)

            except AttributeError:
                await interaction.response.send_message(f"Please use /connect or /play first!")

            await interaction.response.send_message(f"Volume changed to **{player.volume}%**")

        @self.command(name="seek")
        async def seek(
                interaction: discord.Interaction,
                seconds: typing.Optional[int] = 0,
                minutes: typing.Optional[int] = 0,
                hours: typing.Optional[int] = 0
        ):
            player = node.get_player(interaction.guild_id)
            miliseconds = (hours * 60 * 60 * 1000) + (minutes * 60 * 1000) + (seconds * 1000)
            try:
                # Spaghetti code
                await player.seek(miliseconds)

                total_seconds = int(miliseconds / 1000)
                calculated_seconds = total_seconds % 60
                calculated_minutes = (total_seconds // 60) % 60
                calculated_hours = total_seconds // 3600
                calculated_hours = f"0{calculated_hours}" if calculated_hours < 10 else str(calculated_hours)
                calculated_minutes = f"0{calculated_minutes}" if calculated_minutes < 10 else str(calculated_minutes)
                calculated_seconds = f"0{calculated_seconds}" if calculated_seconds < 10 else str(calculated_seconds)

                embed = discord.Embed(
                    title="Seek",
                    description=f"Skipped to: {calculated_hours}:{calculated_minutes}:{calculated_seconds}."
                )
            except AttributeError:
                embed = discord.Embed(
                    title="Not playing anything."
                )
            await interaction.response.send_message(embed=embed)

        async def connect_logic(interaction):
            try:
                channel = interaction.user.voice.channel
            except AttributeError:
                return await interaction.response.send_message("No voice channel to connect to.")

            vc: wavelink.Player = await channel.connect(cls=wavelink.Player)
            return vc


class LCBot(discord.Client):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger

    async def on_ready(self):
        self.logger.info(f"Connected as {self.user.name}")
        try:
            self.logger.info("Starting lavalink...")
            await self.start_lavalink()
            node: wavelink.Node = wavelink.Node(uri="http://localhost:2333", password="youshallnotpass")
            await wavelink.NodePool.connect(client=self, nodes=[node])
            self.logger.info("Syncing commands...")
            tree = LCCommands(self)
            synced = await tree.sync()
            self.logger.info(f"Synced {len(synced)} command(s)")
            # await self.check_new_video.start()
        except Exception as e:
            self.logger.error(e)

    @staticmethod
    async def start_lavalink():
        with open("logs/lavalink_logs.log", "a") as log_file:
            process = await asyncio.create_subprocess_exec(
                "java", "-jar", "Lavalink.jar", cwd="lavalink",
                stdout=log_file, stderr=log_file
            )

    async def on_wavelink_node_ready(self, node):
        self.logger.info(f"Wavelink node ready. ID: '{node.id}'")

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
        option_list = {}
        if "options" in interaction.data:
            for option in interaction.data["options"]:
                option_list[option["name"]] = option["value"]
        option_str = ", ".join([f"{key}: {value}" for key, value in option_list.items()])
        self.logger.info(f"User: {interaction.user} executed: {interaction.data['name']} args: [{option_str}]")

    # TODO Fix check_new_video
    # @tasks.loop(seconds=30)
    # async def check_new_video(self):
    #     video = SearchForNewVideo()
    #     link, title = video.check_new_video()
    #     if link != "null" and title != "null":
    #         print("new video upload detected")
    #         channel = await self.fetch_channel(YOUTUBE_FEED_CHANNEL_ID)
    #         await channel.send(f"New video uploaded on the channel!\n{title}\n{link}")
    #     else:
    #         print("no new videos uploaded")
