import os
import pandas as pd
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import time
import yagmail

load_dotenv()

# --- Environment Variables ---
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

OUTBOX_FILE = "outbox.csv"
SENT_FILE = "sent.csv"

def send_linkedin_message(playwright, profile_url, message):
    """Navigates to a LinkedIn profile and sends a message."""
    browser = playwright.chromium.launch(headless=False) # Set headless=True for production
    context = browser.new_context()
    page = context.new_page()

    try:
        # Login
        page.goto("https://www.linkedin.com/login")
        page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
        page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Go to profile
        page.goto(profile_url)
        page.wait_for_load_state('domcontentloaded')

        # Click message button and send
        page.click('button:has-text("Message")')
        time.sleep(2) # Wait for message box to appear
        page.fill('div.msg-form__contenteditable', message)
        page.click('button.msg-form__send-button')
        print(f"Message sent to {profile_url}")
        return True

    except Exception as e:
        print(f"Failed to send message to {profile_url}: {e}")
        return False
    finally:
        browser.close()

def send_cold_email(recipient_email, subject, body):
    """Sends a cold email using yagmail."""
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("Gmail credentials not found in environment variables.")
        return False
    
    try:
        yag = yagmail.SMTP(GMAIL_USER, GMAIL_PASSWORD)
        yag.send(
            to=recipient_email,
            subject=subject,
            contents=body
        )
        print(f"Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")
        return False

if __name__ == "__main__":
    SENDING_METHOD = os.getenv("SENDING_METHOD", "linkedin") # "linkedin" or "email"

    if not os.path.exists(OUTBOX_FILE):
        print("Outbox file not found. Nothing to send.")
        exit()

    outbox_df = pd.read_csv(OUTBOX_FILE)
    
    if not os.path.exists(SENT_FILE):
        pd.DataFrame(columns=outbox_df.columns).to_csv(SENT_FILE, index=False)

    if SENDING_METHOD == "linkedin":
        with sync_playwright() as p:
            for index, row in outbox_df.iterrows():
                success = send_linkedin_message(p, row['profile_url'], row['draft_msg'])
                if success:
                    pd.DataFrame([row]).to_csv(SENT_FILE, mode='a', header=False, index=False)
                    outbox_df.drop(index, inplace=True)
                    time.sleep(60)
    
    elif SENDING_METHOD == "email":
        for index, row in outbox_df.iterrows():
            if 'email' in row and pd.notna(row['email']):
                subject = f"Following up from {row.get('company', 'your company')}"
                success = send_cold_email(row['email'], subject, row['draft_msg'])
                if success:
                    pd.DataFrame([row]).to_csv(SENT_FILE, mode='a', header=False, index=False)
                    outbox_df.drop(index, inplace=True)
                    time.sleep(10)
            else:
                print(f"Skipping {row['full_name']} - no email address.")

    outbox_df.to_csv(OUTBOX_FILE, index=False)
    print("Finished sending messages.")