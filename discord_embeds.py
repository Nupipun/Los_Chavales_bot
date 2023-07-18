from discord import Embed
from wavelink import YouTubeTrack, YouTubePlaylist


def help_embed(choice):
    if choice == "general":
        description = ("**GENERAL COMMANDS**\n"
                       "**/ping** - _Pong!_\n"
                       "**/help** - _Shows this message._\n\n")
    elif choice == "music":
        description = ("**MUSIC COMMANDS**\n"
                       "**/queue** - _Shows the current queue._\n"
                       "**/bump** - _Bumps a song to the top of the queue (currently unsupported)_\n"
                       "**/play** - _Plays a song. (spotify playlist currently unsupported)_\n"
                       "**/skip** - _Skips the current song._\n"
                       "**/stop** - _Stops playback._\n"
                       "**/connect** - _Connects to a voicechat._\n"
                       "**/disconnect** - _Disconnects from a voicechat._\n"
                       "**/nowplaying** - _Shows the current song playing._\n"
                       "**/pause** - _Pauses playback._\n"
                       "**/resume** - _Resumes playback._\n"
                       "**/volume** - _Changes the volume._\n")
    elif choice == "durobot":
        # description = ("**DUROBOT COMMANDS**\n"
        #                "**/durosave** - _Saves a new image in the duro database._\n"
        #                "**/duro** - _Sends a random image from the duro database._\n"
        #                "**/gatosave** - _Saves a new image in the gato database._\n"
        #                "**/gato** - _Sends a random image from the gato database._\n"
        #                "**/borzoisave** - _Saves a new image in the borzoi database._\n"
        #                "**/borzoi** - _Sends a random image from the borzoi database._\n"
        #                "**/lmaosave** - _Saves a new image in the lmao database._\n"
        #                "**/lmao** - _Sends a random image from the lmao database._\n"
        #                )
        description = (
            "**DUROBOT COMMANDS**\n"
            "Durobot integration is currently disabled.\n"
        )
    else:
        description = "**Choose a valid option (general, music, admin, durobot).**"

    return Embed(title="**Avaliable commands**", description=description)


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


def now_playing_embed(track, queue):
    if isinstance(track, YouTubeTrack):
        description = f"Track: {track.title}\nLink: {track.uri}"
    elif isinstance(track, YouTubePlaylist):
        description = f"Track: {track.tracks[-queue - 1].title}\nLink: {track.tracks[-queue - 1].uri}"
    embed = Embed(title="Now playing", description=description)
    return embed


def added_to_queue_embed(track):
    return Embed(
        title="**Added to queue**",
        description=f"Track: {track}\nLink: {track.uri}"
    )


def not_enough_tracks_in_queue_embed():
    return Embed(
        title="There are not enough tracks in the queue."
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
