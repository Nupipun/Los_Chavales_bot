from discord.app_commands import CommandTree
import discord
import wavelink
import typing
import discord_embeds as embeds
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import constants as const


class LCMusicCommands(CommandTree):
    def __init__(self, client):
        super().__init__(client)
        node = wavelink.NodePool.get_node()

        cola_link = []
        self.track = []
        self.channel = None

        # TODO Add clear parameter to clear the queue.
        # TODO Fix the queue command when it reaches 4096 characters.
        @self.command(name="queue")
        async def queue(interaction: discord.Interaction):
            player = node.get_player(interaction.guild_id)
            if len(client.voice_clients) == 0:
                return await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())
            track_list = []
            if player.queue.count != 0:
                contador = 0
                for _ in range(player.queue.count):
                    contador += 1
                    cola_str = player.queue.get()
                    track_list.append(f"`{contador}.` **[{cola_str}]({cola_link[_]})**")
                    player.queue.put(cola_str)
            else:
                track_list.append("No songs in the queue.")
            track_list_str = "\n".join(track_list)
            embed = embeds.current_queue_embed(track_list_str)
            await interaction.response.send_message(embed=embed)

        # TODO Fix bump messing up with the queue.
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

        # TODO Add spotify playlist support.
        @self.command(name="play")
        async def play(interaction: discord.Interaction, search: str):
            if len(client.voice_clients) == 0:
                await connect_logic(interaction)
            player = node.get_player(interaction.guild_id)
            player.autoplay = True

            if is_spotify_link(search):
                spotify_track_id = get_spotify_track_id(search, "track")

                if spotify_track_id is None:
                    return await interaction.response.send_message(embed=embeds.track_not_found_embed())
                track_name, artist_names = get_track_name_from_spotify(spotify_track_id, "track")
                list_of_artists = ", ".join(artist_names)
                search = f"{list_of_artists} {track_name}"

            if "&list=" in search:
                playlist_id = search.split("&list=")[1]
                self.track = await wavelink.YouTubePlaylist.search(playlist_id)

                if not self.track:
                    return await interaction.response.send_message(embed=embeds.track_not_found_embed())
                add_all_tracks_to_queue(player, "playlist")
            else:
                tracks = await wavelink.YouTubeTrack.search(search)

                if not tracks:
                    return await interaction.response.send_message(embed=embeds.track_not_found_embed())
                self.track = tracks[0]
                add_all_tracks_to_queue(player, "track")
                embed = embeds.added_to_queue_embed(self.track)

            if not player.is_playing():
                await player.play(player.queue.get())
                embed = embeds.now_playing_embed(self.track, player.queue.count)
            await interaction.response.send_message(embed=embed)

        def add_all_tracks_to_queue(player, query_type, tracks=None):
            if query_type == "track":
                player.queue.put(self.track)
                cola_link.append(self.track.uri)
            elif query_type == "playlist":
                for track in self.track.tracks:
                    player.queue.put(track)
                    cola_link.append(track.uri)

        def get_spotify_track_id(url: str, query: str) -> typing.Optional[str]:
            """Returns the track ID from a Spotify track URL."""
            if query == "track":
                match = re.search(r"track\/(\w+)", url)
            elif query == "playlist":
                match = re.search(r"playlist\/(\w+)", url)
            if match:
                return match.group(1)
            return None

        def is_spotify_link(url: str) -> bool:
            """Returns True if the URL is a Spotify URL."""
            return url.startswith("https://open.spotify.com/")

        def get_track_name_from_spotify(id: str, query_type: str) -> typing.Optional[str]:
            """Returns the track name and artist name from a Spotify track ID."""
            client_credentials_manager = SpotifyClientCredentials(client_id=const.SPOTIFY_CLIENT_ID,
                                                                  client_secret=const.SPOTIFY_CLIENT_SECRET)
            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            if query_type == "track":
                track = sp.track(id)
                track_name = track["name"]
                artist_names = [artist["name"] for artist in track["artists"]]

                return track_name, artist_names

        @self.command(name="nowplaying")
        async def nowplaying(interaction: discord.Interaction):
            player = node.get_player(interaction.guild_id)
            if len(client.voice_clients) == 0:
                return await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())
            elif not player.is_playing or player is None:
                return await interaction.response.send_message(embed=embeds.tracks_not_playing_embed())

            embed = embeds.now_playing_embed(self.track, player.queue.count)
            await interaction.response.send_message(embed=embed)

        @self.command(name="skip")
        async def skip(interaction: discord.Interaction, count: typing.Optional[int] = 0):
            """Skips the current track. If a number is specified, skips that many tracks."""
            player = node.get_player(interaction.guild_id)
            if len(client.voice_clients) == 0:
                return await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())

            elif not player.is_playing or player is None:
                return await interaction.response.send_message(embed=embeds.tracks_not_playing_embed())

            elif count >= player.queue.count:
                return await interaction.response.send_message(embed=embeds.not_enough_tracks_in_queue_embed())

            elif count != 0:
                for _ in range(count):
                    player.queue.get()
                    await player.stop()
                return await interaction.response.send_message(embed=embeds.skipping_track_embed())

            else:
                await player.stop()
                return await interaction.response.send_message(embed=embeds.skipping_track_embed())

        @self.command(name="stop")
        async def stop(interaction: discord.Interaction):
            player = node.get_player(interaction.guild.id)
            if len(client.voice_clients) == 0:
                return await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())
            elif not player.is_playing or player is None:
                return await interaction.response.send_message(embed=embeds.tracks_not_playing_embed())
            for _ in range(player.queue.count):
                print(player.queue.count)
                player.queue.pop()
            self.track = []
            await player.stop()
            await interaction.response.send_message(embed=embeds.playback_stopped_embed())

        @self.command(name="connect")
        async def connect(interaction: discord.Interaction):
            actual_channel = interaction.user.voice.channel
            if actual_channel is None:
                return await interaction.response.send_message(embed=embeds.voicechannel_not_found_embed())

            if self.channel != actual_channel:
                for x in client.voice_clients:
                    await x.disconnect()
                self.channel = actual_channel
                self.channel.connect()
            else:
                return await interaction.response.send_message(embed=embeds.already_connected_to_voicechat_embed())
            await interaction.response.send_message(embed=embeds.connected_to_voicechat_embed(self.channel.name))
            vc: wavelink.Player = await self.channel.connect(cls=wavelink.Player)
            return vc

        @self.command(name="disconnect")
        async def disconnect(interaction: discord.Interaction):
            player = node.get_player(interaction.guild.id)
            if len(client.voice_clients) == 0:
                return await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())

            for _ in range(player.queue.count):
                player.queue.pop()

            await player.stop()

            for x in client.voice_clients:
                await interaction.response.send_message(
                    embed=embeds.disconnected_from_voicechat_embed())
                self.channel = None
                return await x.disconnect()

        @self.command(name="volume")
        async def volume(interaction: discord.Interaction, volume_number: int):
            player = node.get_player(interaction.guild_id)
            if len(client.voice_clients) == 0:
                return await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())

            await player.set_volume(volume_number)
            await interaction.response.send_message(embed=embeds.volume_changed_embed(volume_number))

        @self.command(name="seek")
        async def seek(
                interaction: discord.Interaction,
                seconds: typing.Optional[int] = 0,
                minutes: typing.Optional[int] = 0,
                hours: typing.Optional[int] = 0
        ):
            player = node.get_player(interaction.guild_id)
            if len(client.voice_clients) == 0:
                return await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())
            if not player.is_playing or player is None:
                return await interaction.response.send_message(embed=embeds.tracks_not_playing_embed())

            miliseconds = (hours * 60 * 60 * 1000) + (minutes * 60 * 1000) + (seconds * 1000)
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
            await interaction.response.send_message(embed=embed)

        async def connect_logic(interaction):
            channel = interaction.user.voice.channel
            if channel is None:
                return await interaction.response.send_message(embed=embeds.voice_channel_not_found_embed())

            vc: wavelink.Player = await channel.connect(cls=wavelink.Player)
            return vc

        @self.command(name="pause")
        async def pause(interaction: discord.Interaction):
            player = node.get_player(interaction.guild_id)
            if len(client.voice_clients) == 0:
                return await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())
            elif not player.is_playing or player is None:
                return await interaction.response.send_message(embed=embeds.tracks_not_playing_embed())
            await player.pause()
            await interaction.response.send_message(embed=embeds.paused_playback_embed())

        @self.command(name="resume")
        async def resume(interaction: discord.Interaction):
            player = node.get_player(interaction.guild_id)
            if len(client.voice_clients) == 0:
                return await interaction.response.send_message(embed=embeds.not_connected_to_voicechat_embed())
            elif not player.is_playing or player is None:
                return await interaction.response.send_message(embed=embeds.tracks_not_playing_embed())
            await player.resume()
            await interaction.response.send_message(embed=embeds.resumed_playback_embed())
