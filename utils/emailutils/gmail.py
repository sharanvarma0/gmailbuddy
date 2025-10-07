import os
from loguru import logger
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/gmail.labels"]
project_path = os.getenv("PYTHONPATH")


def initialize_gmail_interaction(credentials):
    service = None
    try:
        service = build("gmail", "v1", credentials=credentials)
    except HttpError as error:
        logger.error(f"Error when attempting to establish Gmail Connection: {error}")
        service = None
    return service



def login_to_gmail():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(f"{project_path}/token.json"):
    creds = Credentials.from_authorized_user_file(f"{project_path}/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          f"{project_path}/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(f"{project_path}/token.json", "w") as token:
      token.write(creds.to_json())
  return creds


def get_all_valid_labels(service):
    available_labels = []
    try:
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        logger.debug("Available Gmail Labels:")
        for label in labels:
            available_labels.append(label['id'])
            logger.debug(f"{label['name']:30} → {label['id']}")
    except Exception as exc:
        logger.error(f"Exception when attempting to list available labels: {exc}")


def update_email(service, email_id, target_labels):
    """This will allow us to update an email in our inbox with the labels provided.
    Example usage:
    service_obj
    email_id: id of the email
    labels: ["SPAM", etc]
    
    If the label does not exist, it will be created before pushing the change
    """
    
    try:
        #available_labels = get_all_valid_labels(service)
        target_label_ids = []
        logger.debug(f"Obtained email_id: {email_id}, labels for change: {target_labels}")
        labels = service.users().labels().list(userId='me').execute().get('labels', [])
        label_id = None
        for tl in target_labels:
            for l in labels:
                if l['id'].lower() == tl.lower():
                    target_label_ids.append(l['id'])
                    break
            if not target_label_ids:
                label = service.users().labels().create(userId='me', body={'name': tl, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}).execute()
                target_label_ids.append(label['id'].upper())
        print(target_label_ids)
        service.users().messages().modify(userId='me', id=email_id, body={'removeLabelIds': ['INBOX', 'UNREAD'], 'addLabelIds': target_label_ids}).execute()
        logger.debug(f"Moved email {email_id} to {labels} and marked them")
    except Exception as mail_update_exc:
        logger.error(f"Exception when trying to update email {email_id}: {mail_update_exc}")

