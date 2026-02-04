import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permissions
SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

TOKEN_FILE = "token.pickle"
CLIENT_SECRET_FILE = "client_secret.json"


def authenticate():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE, SCOPES
        )
        creds = flow.run_local_server(port=0)



        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


def get_comments(youtube, video_id):
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=10,
        textFormat="plainText"
    )
    response = request.execute()

    comments = []

    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comment_id = item["snippet"]["topLevelComment"]["id"]
        comments.append((comment_id, comment))

    return comments


def reply_to_comment(youtube, comment_id, text):
    youtube.comments().insert(
        part="snippet",
        body={
            "snippet": {
                "parentId": comment_id,
                "textOriginal": text
            }
        }
    ).execute()


if __name__ == "__main__":
    VIDEO_ID = "9iTUv_jj-Zk"

    youtube = authenticate()
    comments = get_comments(youtube, VIDEO_ID)

    print("Found comments:")
    for cid, text in comments:
        print("-", text)

        reply = f"Thanks for your comment: '{text}'"
        reply_to_comment(youtube, cid, reply)
        print("Replied.")
