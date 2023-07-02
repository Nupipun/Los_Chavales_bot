from discord.app_commands import CommandTree
import discord
import wavelink
import typing
import discord_embeds as embeds


class LCMusicCommands(CommandTree):
    def __init__(self, client):
        super().__init__(client)
        node = wavelink.NodePool.get_node()
        cola_link = []
        self.track = []
        self.channel = None

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
                        track_list.append(f"{'-' * 35}\n{contador}. Nombre: {cola_str}\n"
                                          f"Link: {cola_link[_]}\n{'-' * 35}")
                        player.queue.put(cola_str)
                else:
                    track_list.append("No songs in the queue.")
                track_list_str = "\n".join(track_list)
            except AttributeError:
                embed = embeds.embed_not_in_voice_channel()
            else:
                embed = embeds.current_queue_embed(track_list_str)
            await interaction.response.send_message(embed=embed)

        @self.command(name="bump")
        async def bump(interaction: discord.Interaction, song_id: int):
            player = node.get_player(interaction.guild_id)
            try:
                await player.set_volume(player.volume)
            except AttributeError:
                await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())

            cola_str = None

            if song_id < 1 or song_id > player.queue.count:
                await interaction.response.send_message(embed=embeds.song_id_not_within_range_embed())
                return

            if player.queue.count == 0:
                await interaction.response.send_message(embed=embeds.no_songs_in_queue_embed())
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
            await interaction.response.send_message(embed=embeds.bumped_song_embed(cola_str))

        @self.command(name="play")
        async def play(interaction: discord.Interaction, search: str):
            if len(client.voice_clients) == 0:
                await connect_logic(interaction)
            player = node.get_player(interaction.guild_id)
            player.autoplay = True

            tracks = await wavelink.YouTubeTrack.search(search)

            if not tracks:
                await interaction.response.send_message(embed=embeds.track_not_found_embed())
                return

            self.track = tracks[0]
            if not player.is_playing():
                await player.play(self.track)
                embed = embeds.now_playing_embed(self.track)
            else:
                player.queue.put(self.track)
                cola_link.append(self.track.uri)
                embed = embeds.added_to_queue_embed(self.track)
            await interaction.response.send_message(embed=embed)

        @self.command(name="nowplaying")
        async def nowplaying(interaction: discord.Interaction):
            try:
                embed = embeds.now_playing_embed(self.track)
            except AttributeError:
                embed = embeds.tracks_not_playing_embed()
            await interaction.response.send_message(embed=embed)

        @self.command(name="skip")
        async def skip(interaction: discord.Interaction):
            player = node.get_player(interaction.guild_id)
            try:
                await player.stop()
                await interaction.response.send_message(embed=embeds.skipping_track_embed())
            except AttributeError:
                await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())

        @self.command(name="stop")
        async def stop(interaction: discord.Interaction):
            player = node.get_player(interaction.guild.id)
            if not player.is_playing:
                await interaction.response.send_message(embed=embeds.tracks_not_playing_embed())
                return
            for _ in range(player.queue.count):
                player.queue.pop()
            self.track = []
            await player.stop()
            await interaction.response.send_message(embed=embeds.playback_stopped_embed())

        @self.command(name="connect")
        async def connect(interaction: discord.Interaction):
            actual_channel = interaction.user.voice.channel
            try:
                if self.channel != actual_channel:
                    for x in client.voice_clients:
                        await x.disconnect()
                    self.channel = actual_channel
                    self.channel.connect()
                else:
                    return await interaction.response.send_message(embed=embeds.already_connected_to_voicechat_embed())
            except AttributeError:
                return await interaction.response.send_message(embed=embeds.voice_channel_not_found_embed())

            await interaction.response.send_message(embed=embeds.connected_to_voicechat_embed(self.channel.name))
            vc: wavelink.Player = await self.channel.connect(cls=wavelink.Player)
            return vc

        @self.command(name="disconnect")
        async def disconnect(interaction: discord.Interaction):
            player = node.get_player(interaction.guild.id)

            for _ in range(player.queue.count):
                player.queue.pop()

            await player.stop()

            for x in client.voice_clients:
                await interaction.response.send_message(
                    embed=embeds.disconnected_from_voicechat_embed())
                self.channel = None
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
                await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())

            else:
                await interaction.response.send_message(embed=embeds.volume_changed_embed(volume_number))

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

                embed = embeds.seek_embed(calculated_hours, calculated_minutes, calculated_seconds)
            except AttributeError:
                embed = embeds.tracks_not_playing_embed()
            await interaction.response.send_message(embed=embed)

        async def connect_logic(interaction):
            try:
                channel = interaction.user.voice.channel
            except AttributeError:
                return await interaction.response.send_message(embed=embeds.voice_channel_not_found_embed())

            vc: wavelink.Player = await channel.connect(cls=wavelink.Player)
            return vc

        @self.command(name="pause")
        async def pause(interaction: discord.Interaction):
            player = node.get_player(interaction.guild_id)
            try:
                await player.pause()
            except AttributeError:
                embed = embeds.tracks_not_playing_embed()
            else:
                embed = embeds.paused_playback_embed()
            finally:
                await interaction.response.send_message(embed=embed)

        @self.command(name="resume")
        async def resume(interaction: discord.Interaction):
            player = node.get_player(interaction.guild_id)
            try:
                await player.resume()
            except AttributeError:
                embed = embeds.tracks_not_playing_embed()
            else:
                embed = embeds.resumed_playback_embed()
            finally:
                await interaction.response.send_message(embed=embed)
