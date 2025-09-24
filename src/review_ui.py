import streamlit as st
import pandas as pd
import os

LEADS_FILE = "leads_with_drafts.csv"
APPROVED_FILE = "outbox.csv"

def load_data():
    """Loads the leads with drafted messages."""
    if os.path.exists(LEADS_FILE):
        return pd.read_csv(LEADS_FILE)
    return None

def save_approved(approved_leads_df):
    """Saves approved messages to the outbox."""
    if os.path.exists(APPROVED_FILE):
        approved_leads_df.to_csv(APPROVED_FILE, mode='a', header=False, index=False)
    else:
        approved_leads_df.to_csv(APPROVED_FILE, index=False)

st.title("Message Review UI")

df = load_data()

if df is not None:
    if 'status' not in df.columns:
        df['status'] = 'pending' # Add status column if it doesn't exist

    # Use session state to keep track of the current index
    if 'review_index' not in st.session_state:
        st.session_state.review_index = 0

    # Get the next pending message
    pending_reviews = df[df['status'] == 'pending']
    if not pending_reviews.empty:
        current_index = pending_reviews.index[0]
        
        lead = df.loc[current_index]

        st.subheader(f"Reviewing message for: {lead['full_name']}")
        st.write(f"**Company:** {lead['company']}")
        st.write(f"**Headline:** {lead['headline']}")
        st.write(f"**School:** {lead['school']}")
        
        st.text_area("Drafted Message", lead['draft_msg'], height=150)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Approve"):
                df.at[current_index, 'status'] = 'approved'
                save_approved(df.loc[[current_index]])
                st.rerun()

        with col2:
            if st.button("❌ Reject"):
                df.at[current_index, 'status'] = 'rejected'
                st.rerun()
        
        with col3:
            if st.button("✏️ Edit & Approve"):
                # For simplicity, we'll consider editing as direct approval in this version.
                # A more advanced version would allow text editing.
                df.at[current_index, 'status'] = 'approved'
                save_approved(df.loc[[current_index]])
                st.rerun()

        # Update the main dataframe with the new status
        df.to_csv(LEADS_FILE, index=False)

    else:
        st.success("All messages have been reviewed!")
        st.write("Approved messages are in `outbox.csv`.")

else:
    st.warning("No leads file found. Please run `personalize.py` first.")
