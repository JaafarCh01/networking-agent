import os
import base64
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import openai

# --- Scopes and Setup ---
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_PICKLE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json' # Download from Google Cloud Console

def get_gmail_service():
    """Authenticates with Google and returns a Gmail service object."""
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        creds = Credentials.from_authorized_user_file(TOKEN_PICKLE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PICKLE, 'w') as token:
            token.write(creds.to_json())
            
    return build('gmail', 'v1', credentials=creds)

def list_unread_messages(service):
    """Lists unread messages in the inbox."""
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])
    return messages

def get_message_details(service, msg_id):
    """Gets the full details of a message."""
    return service.users().messages().get(userId='me', id=msg_id).execute()

def triage_reply(message_body):
    """Uses GPT to categorize a reply."""
    prompt = f"""
    Categorize this email reply as: 1=interested, 2=busy, 3=decline, 4=needs-follow-up.
    The email is:
    ---
    {message_body}
    ---
    Category:
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error triaging reply: {e}")
        return "Error"

if __name__ == "__main__":
    # This script requires user interaction for the first run to authenticate.
    # You need a credentials.json file from the Google Cloud Console.
    
    if not os.path.exists(CREDENTIALS_FILE):
        print("Error: credentials.json not found. Please download it from the Google Cloud Console.")
    else:
        service = get_gmail_service()
        unread_messages = list_unread_messages(service)

        if not unread_messages:
            print("No unread messages.")
        else:
            leads_df = pd.read_csv('sent.csv') # Assuming we check replies for sent messages

            for msg in unread_messages:
                msg_details = get_message_details(service, msg['id'])
                payload = msg_details['payload']
                
                # Extract sender and body
                sender = next(h['value'] for h in payload['headers'] if h['name'] == 'From')
                
                if 'parts' in payload:
                    body_data = payload['parts'][0]['body']['data']
                else:
                    body_data = payload['body']['data']
                
                body = base64.urlsafe_b64decode(body_data).decode('utf-8')

                print(f"New reply from: {sender}")
                
                # Triage the reply
                category = triage_reply(body)
                print(f"Triage category: {category}")

                # Here you would update your database/CRM
                # For now, we'll just print the result
                # Example: Find the lead by email and update their status
                # leads_df.loc[leads_df['email'] == sender_email, 'status'] = category
                
            # leads_df.to_csv('leads_updated.csv', index=False)
            print("Finished processing replies.")
