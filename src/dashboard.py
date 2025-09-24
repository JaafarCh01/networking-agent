import streamlit as st
import pandas as pd
import os

# --- File Paths ---
LEADS_FILE = "leads_with_drafts.csv"
OUTBOX_FILE = "outbox.csv"
SENT_FILE = "sent.csv"
# A file to track replies would be needed for a complete funnel
# REPLIES_FILE = "replies.csv" 

st.set_page_config(layout="wide")
st.title("Networking Funnel Dashboard")

# --- Load Data ---
def load_df(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

leads_df = load_df(LEADS_FILE)
outbox_df = load_df(OUTBOX_FILE)
sent_df = load_df(SENT_FILE)
# replies_df = load_df(REPLIES_FILE) # Placeholder for reply tracking

# --- Calculate Funnel Metrics ---
total_leads = len(leads_df)
messages_drafted = len(leads_df[leads_df['draft_msg'].notna()])
messages_approved = len(outbox_df) + len(sent_df) # Approved are in outbox or already sent
messages_sent = len(sent_df)

# For replied and call booked, we'd need more data.
# These are placeholders to illustrate the concept.
# In a real scenario, this would come from the inbox listener and calendar integration.
replied = 0 # len(replies_df)
call_booked = 0 # len(replies_df[replies_df['status'] == 'call_booked'])

# --- Display Funnel ---
st.header("Outreach Funnel")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Leads", f"{total_leads}")
col2.metric("Messages Drafted", f"{messages_drafted}")
col3.metric("Messages Approved", f"{messages_approved}")
col4.metric("Messages Sent", f"{messages_sent}")

# --- Conversion Rates ---
st.header("Conversion Rates")
draft_rate = (messages_drafted / total_leads * 100) if total_leads > 0 else 0
approval_rate = (messages_approved / messages_drafted * 100) if messages_drafted > 0 else 0
sent_rate = (messages_sent / messages_approved * 100) if messages_approved > 0 else 0
# reply_rate = (replied / messages_sent * 100) if messages_sent > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Draft Rate", f"{draft_rate:.2f}%")
col2.metric("Approval Rate", f"{approval_rate:.2f}%")
col3.metric("Sent Rate", f"{sent_rate:.2f}%")


# --- Detailed View ---
st.header("Lead Status Overview")
st.dataframe(leads_df)
