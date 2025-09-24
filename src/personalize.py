import os
import pandas as pd
import openai
from dotenv import load_dotenv

load_dotenv()

# --- Environment Variables ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# --- System Prompt ---
SYSTEM_PROMPT = "You are a polite new-grad SWE reaching out to a {role} at {company}. Keep it under 50 words, reference 1 shared detail."

def generate_message_prompt(lead):
    """Generates a specific prompt for a given lead."""
    # This example assumes the CSV has these columns.
    # You might need to adjust based on your actual lead data.
    prompt = f"""
    Write a 50-word LinkedIn DM to {lead.get('full_name', 'there')}, a {lead.get('headline', 'professional')} at {lead.get('company', 'their company')}.
    You both attended {lead.get('school', 'the same university')}.
    Politely ask for a 15-min career chat about their work.
    """
    # The guide mentions referencing a recent post, which would require more data.
    # Example: if 'recent_post_topic' in lead and lead['recent_post_topic']:
    #     prompt += f" Mention their recent post about {lead['recent_post_topic']}."
    return prompt

def get_personalized_message(lead):
    """Uses OpenAI to generate a personalized message for a lead."""
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY not found. Returning placeholder message.")
        return "This is a placeholder message. Please set your OPENAI_API_KEY."

    full_prompt = generate_message_prompt(lead)
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(role=lead.get('headline', 'professional'), company=lead.get('company', 'their company'))},
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating message for {lead.get('full_name')}: {e}")
        return "Error generating message."

if __name__ == "__main__":
    leads_df = pd.read_csv("leads_processed.csv")
    
    # Create a new column for the draft message
    leads_df['draft_msg'] = ''

    for index, row in leads_df.iterrows():
        print(f"Generating message for {row['full_name']}...")
        message = get_personalized_message(row.to_dict())
        leads_df.at[index, 'draft_msg'] = message

    leads_df.to_csv("leads_with_drafts.csv", index=False)
    print("Finished generating messages. Output saved to leads_with_drafts.csv")
