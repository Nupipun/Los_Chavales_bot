from discord import Embed


def help_embed():
    return Embed(
        title="**Avaliable commands**",
        description="**/ping** - _Pong!_\n"
                    "**/help** - _Shows this message._\n"
                    "**/queue** - _Shows the current queue._\n"
                    "**/bump** - _Bumps a song to the top of the queue._\n"
                    "**/play** - _Plays a song._\n"
                    "**/skip** - _Skips the current song._\n"
                    "**/stop** - _Stops playback._\n"
                    "**/connect** - _Connects to a voicechat._\n"
                    "**/disconnect** - _Disconnects from a voicechat._\n"
                    "**/nowplaying** - _Shows the current song playing._\n"
                    "**/pause** - _Pauses playback._\n"
                    "**/resume** - _Resumes playback._\n"
                    "**/volume** - _Changes the volume._\n"
    )


def announcement_embed(message, is_everyone: bool = False):
    return Embed(
        title="Announcement",
        description=f"{message}",
    )


def not_connected_to_voicechat_embed():
    return Embed(
        title="Not connected to a voicechat."
    )


def current_queue_embed(track_list_str):
    return Embed(
        title="**Current Queue**",
        description=track_list_str
    )


def song_id_not_within_range_embed():
    return Embed(
        title="The song id you inputted is not within the range of the queue."
    )


def no_songs_in_queue_embed():
    return Embed(
        title="There are no songs in the queue."
    )


def bumped_song_embed(cola_str):
    return Embed(
        title="Bump",
        description=f'Bumped **"{cola_str.title}"** to the top of the queue.'
    )


def track_not_found_embed():
    return Embed(
        title="Track not found."
    )


def now_playing_embed(track):
    return Embed(
        title="**Now playing**",
        description=f"Track: {track}\nLink: {track.uri}"
    )


def added_to_queue_embed(track):
    return Embed(
        title="**Added to queue**",
        description=f"Track: {track}\nLink: {track.uri}"
    )


def tracks_not_playing_embed():
    return Embed(
        title="There are no tracks playing right now."
    )


def skipping_track_embed():
    return Embed(
        title="Skipping track."
    )


def playback_stopped_embed():
    return Embed(
        title="Playback stopped."
    )


def already_connected_to_voicechat_embed():
    return Embed(
        title="Already connected to a voicechat."
    )


def voicechannel_not_found_embed():
    return Embed(
        title="Voice channel not found."
    )


def connected_to_voicechat_embed(channel_name):
    return Embed(
        title=f"Connected to channel **{channel_name}**."
    )


def disconnected_from_voicechat_embed():
    return Embed(
        title="Disconnected from voicechat."
    )


def volume_changed_embed(volume):
    return Embed(
        title="Volume changed.",
        description=f"Volume changed to **{volume}**."
    )


def seek_embed(hours, minutes, seconds):
    return Embed(
        title="Seek changed.",
        description=f"Seeked to **{hours}:{minutes}:{seconds}**."
    )


def paused_playback_embed():
    return Embed(
        title="Playback paused."
    )


def resumed_playback_embed():
    return Embed(
        title="Playback resumed."
    )
