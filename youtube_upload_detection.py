from googleapiclient.discovery import build
import json
from constants import *


class SearchForNewVideo:
    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        self.json_file = "latest_video_id.json"
        self.latest_video_id = self.load_latest_video_id()

    def check_new_video(self):
        search_response = self.youtube.search().list(
            channelId=YOUTUBE_CHANNEL_ID,
            part="id,snippet",
            order="date",
            type="video"
        ).execute()

        latest_video_id = search_response["items"][0]["id"]["videoId"]
        video_title = search_response["items"][0]["snippet"]["title"]
        video_link = f"https://www.youtube.com/watch?v={latest_video_id}"

        if latest_video_id != self.latest_video_id:
            self.latest_video_id = latest_video_id
            self.save_latest_video_id()
        else:
            video_title = "null"
            video_link = "null"
        return video_link, video_title

    def load_latest_video_id(self):
        try:
            with open(self.json_file, "r") as json_file:
                data = json.load(json_file)
                return data["latest_video_id"]
        except FileNotFoundError:
            return ""

    def save_latest_video_id(self):
        data = {"latest_video_id": self.latest_video_id}
        with open(self.json_file, "w") as json_file:
            json.dump(data, json_file)


if __name__ == "__main__":
    video = SearchForNewVideo()
    link, title = video.check_new_video()
    if link != "null" and title != "null":
        print(link)
        print(title)
    else:
        print("no new videos uploaded")
