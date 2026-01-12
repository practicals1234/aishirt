# # #utils/gdrive_helper.py

# import os
# import io
# import streamlit as st
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.oauth2.credentials import Credentials

# SCOPES = ["https://www.googleapis.com/auth/drive"]

# TOKEN_FILE = "token.json"
# CLIENT_SECRET_FILE = "client_secret.json"


# def get_drive_service():
#     """Authenticate user via OAuth and return Drive service."""

#     creds = None

#     if os.path.exists(TOKEN_FILE):
#         creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

#     if not creds or not creds.valid:
#         flow = InstalledAppFlow.from_client_secrets_file(
#             CLIENT_SECRET_FILE, SCOPES
#         )
#         creds = flow.run_local_server(port=0)
#         with open(TOKEN_FILE, "w") as token:
#             token.write(creds.to_json())

#     return build("drive", "v3", credentials=creds)


# def upload_to_drive(file_content, file_name, folder_id):
#     service = get_drive_service()

#     file_metadata = {
#         "name": file_name,
#         "parents": [folder_id]
#     }

#     media = MediaIoBaseUpload(
#         io.BytesIO(file_content),
#         mimetype="application/pdf"
#     )

#     file = service.files().create(
#         body=file_metadata,
#         media_body=media,
#         fields="id, webViewLink"
#     ).execute()

#     file_id = file["id"]

#     service.permissions().create(
#         fileId=file_id,
#         body={
#             "type": "anyone",
#             "role": "reader"
#         }
#     ).execute()

#     return file["webViewLink"]


import os
import io
import socket
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# --- CONFIGURATION ---
SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_FILE = "token.json"
CLIENT_SECRET_FILE = "client_secret.json"

def get_drive_service():
    """Authenticate user via OAuth and return Drive service with increased timeout."""
    creds = None

    # Load existing credentials if they exist
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, run the OAuth flow
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE, SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    # Set a global timeout for the socket (300 seconds = 5 minutes)
    # This prevents the "Read operation timed out" error during large transfers
    socket.setdefaulttimeout(300)

    return build("drive", "v3", credentials=creds)

def upload_to_drive(file_content, file_name, folder_id):
    """Uploads content using a resumable session for stability."""
    service = get_drive_service()

    file_metadata = {
        "name": file_name,
        "parents": [folder_id]
    }

    # Wrap bytes in a stream
    fh = io.BytesIO(file_content)
    
    # RESUMABLE UPLOAD: Breaks the file into chunks and allows for retries 
    # if the connection flickers. Essential for large high-res PDFs.
    media = MediaIoBaseUpload(
        fh, 
        mimetype="application/pdf", 
        chunksize=1024*1024, # 1MB chunks
        resumable=True
    )

    try:
        # 1. Create the file on Drive
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                # Optional: You could pass this progress back to the UI
                print(f"Uploaded {int(status.progress() * 100)}%.")

        file_id = response["id"]

        # 2. Set Public Permissions
        service.permissions().create(
            fileId=file_id,
            body={
                "type": "anyone",
                "role": "reader"
            }
        ).execute()

        return response["webViewLink"]

    except Exception as e:
        st.error(f"Upload interrupted: {e}")
        return None