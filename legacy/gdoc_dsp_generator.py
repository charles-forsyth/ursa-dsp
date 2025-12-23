import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- Configuration ---
SCOPES = ["https://www.googleapis.com/auth/documents"]
CLIENT_SECRET_FILE = "scripts/client_secret.json"
TOKEN_PICKLE_FILE = "token.pickle"


def get_credentials():
    """Gets valid user credentials from storage or initiates the OAuth2 flow."""
    creds = None
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PICKLE_FILE, "wb") as token:
            pickle.dump(creds, token)

    return creds


def create_google_doc(title, body_content):
    """Creates a new Google Doc with the given title and content."""
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    # Create the document
    document = service.documents().create(body={"title": title}).execute()
    doc_id = document.get("documentId")
    print(f"Created Google Doc with ID: {doc_id}")

    # Add the content
    requests = []
    index = 1
    for item in body_content:
        # Insert section title as a Heading 1
        requests.append(
            {"insertText": {"location": {"index": index}, "text": item["title"] + "\n"}}
        )
        requests.append(
            {
                "updateParagraphStyle": {
                    "range": {
                        "startIndex": index,
                        "endIndex": index + len(item["title"]),
                    },
                    "paragraphStyle": {
                        "namedStyleType": "HEADING_1",
                    },
                    "fields": "namedStyleType",
                }
            }
        )
        index += len(item["title"]) + 1

        # Insert the generated response text
        requests.append(
            {
                "insertText": {
                    "location": {"index": index},
                    "text": item["response"] + "\n\n",
                }
            }
        )
        index += len(item["response"]) + 2

    # Execute the batch update
    service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()
    print("Successfully added content to the Google Doc.")

    return f"https://docs.google.com/document/d/{doc_id}/edit"


def main(project_name):
    """Main function to generate the Google Doc."""
    print(f"--- Starting Google Doc DSP Generation for project: {project_name} ---")

    # 1. Load the generated content
    log_path = os.path.join(
        "projects", project_name, f"{project_name}_DSP_Generation_Log.json"
    )
    if not os.path.exists(log_path):
        print(
            f"ERROR: Could not find the generation log at {log_path}. Please run the main generator script first."
        )
        return

    with open(log_path, "r") as f:
        generation_log = json.load(f)

    print("Successfully loaded the generation log.")

    # 2. Create the Google Doc
    doc_title = f"Data Security Plan: {project_name}"
    doc_url = create_google_doc(doc_title, generation_log)

    print("\n--- Google Doc Generation Complete ---")
    print(f"You can access the new document here: {doc_url}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 gdoc_dsp_generator.py <ProjectFolderName>")
    else:
        main(sys.argv[1])
