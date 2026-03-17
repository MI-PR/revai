import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# 1. SETUP
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret.json"

def get_authenticated_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes)
            # Use a fixed port if you want to whitelist it in Google Cloud
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return googleapiclient.discovery.build(api_service_name, api_version, credentials=creds)

# ... (The rest of the get_comments and reply_to_comment functions remain the same)

# 1. SETUP SCOPES AND API INFO
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret.json"



def get_comments(youtube, video_id):
    """
    Lists the top-level comments for a specific video.
    """
    try:
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=20,  # Max is 100
            textFormat="plainText"
        )
        response = request.execute()

        comments_data = []
        for item in response.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]
            comment_id = top_comment["id"]
            author = top_comment["snippet"]["authorDisplayName"]
            text = top_comment["snippet"]["textDisplay"]
            
            comments_data.append({
                "id": comment_id,
                "author": author,
                "text": text
            })
            
        return comments_data

    except googleapiclient.errors.HttpError as e:
        print(f"Error fetching comments: {e}")
        return []

def reply_to_comment(youtube, parent_id, reply_text):
    """
    Replies to a specific comment using its ID (parent_id).
    """
    try:
        request = youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": parent_id,
                    "textOriginal": reply_text
                }
            }
        )
        response = request.execute()
        print(f"Successfully replied to {parent_id}!")
        return response

    except googleapiclient.errors.HttpError as e:
        print(f"Error posting reply: {e}")
        return None

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Authenticate (Browser will open to login)
    youtube_service = get_authenticated_service()

    # 2. Define the video you want to check
    VIDEO_ID = "9iTUv_jj-Zk"  # Replace with a real Video ID

    # 3. Get Comments
    print(f"Fetching comments for video: {VIDEO_ID}...")
    comments = get_comments(youtube_service, VIDEO_ID)

    for i, comment in enumerate(comments):
        print(f"[{i}] {comment['author']}: {comment['text']}")

    # 4. Interactive Reply (Optional)
    if comments:
        choice = input("\nEnter the index number of the comment to reply to (or 'q' to quit): ")
        if choice.isdigit() and int(choice) < len(comments):
            target_comment = comments[int(choice)]
            reply_msg = input(f"Enter your reply to {target_comment['author']}: ")
            
            reply_to_comment(youtube_service, target_comment['id'], reply_msg)
        else:
            print("Exiting without replying.")
