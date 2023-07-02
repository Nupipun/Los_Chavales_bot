from googleapiclient.discovery import build
import constants as c
import shelve
import os


class SearchForNewVideo:
    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey=c.YOUTUBE_API_KEY)

    def check_new_video(self):
        search_response = self.youtube.search().list(
            channelId=c.YOUTUBE_CHANNEL_ID,
            part="id,snippet",
            order="date",
            type="video"
        ).execute()

        self.latest_video_id = self.load_latest_video_id()
        latest_video_id = search_response["items"][0]["id"]["videoId"]
        video_title = search_response["items"][0]["snippet"]["title"]
        video_link = fr"https://www.youtube.com/watch?v={latest_video_id}"

        if latest_video_id != self.latest_video_id:
            self.latest_video_id = latest_video_id
            self.save_latest_video_id()
        else:
            video_title = "null"
            video_link = "null"
        return video_link, video_title

    def load_latest_video_id(self):
        try:
            with shelve.open("shelve/latest_video_id") as data:
                return data["latest_video_id"]
        except FileNotFoundError:
            return ""

    def save_latest_video_id(self):
        try:
            with shelve.open("shelve/latest_video_id") as data:
                data["latest_video_id"] = self.latest_video_id
        except FileNotFoundError:
            os.mkdir("shelve")
            self.save_latest_video_id()


if __name__ == "__main__":
    video = SearchForNewVideo()
    link, title = video.check_new_video()
    if link != "null" and title != "null":
        print(link)
        print(title)
    else:
        print("no new videos uploaded")
