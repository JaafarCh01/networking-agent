# Networking Agent

An automated networking tool that helps streamline professional outreach through LinkedIn and email. The tool assists in lead generation, message personalization, human-in-the-loop review, delivery, and response triage with a Streamlit-based dashboard.

## Features

- **Lead Generation**: Playwright-assisted LinkedIn public results scraping and optional Apollo enrichment
- **Message Personalization**: AI-powered message generation using OpenAI
- **Human Review Queue**: Approve or reject drafts before sending
- **Multi-Channel Outreach**: Send via LinkedIn DMs or cold email
- **Inbox Triage**: Gmail API integration to categorize replies
- **Campaign Dashboard**: Streamlit UI for funnel metrics

## Project Structure

```
networking-agent/
├── src/
│   ├── lead_gen.py        # LinkedIn scraping + de-dup + Apollo enrichment
│   ├── personalize.py     # OpenAI-powered message personalization
│   ├── review_ui.py       # Streamlit UI to approve/reject drafts → outbox.csv
│   ├── sender.py          # Delivery (LinkedIn via Playwright, or email via Gmail)
│   ├── inbox_listener.py  # Gmail integration for reply triage with GPT
│   └── dashboard.py       # Streamlit dashboard for funnel metrics
├── sql/
│   └── schema.sql         # Optional Postgres schema
├── infra/
│   ├── Dockerfile         # Container configuration (Streamlit entrypoint)
│   └── cloudformation.yaml # AWS ECS Fargate example
└── requirements.txt       # Python dependencies
```

## Prerequisites

- Python 3.9+
- Google Chrome (for Playwright) and Playwright browsers installed
- OpenAI API key
- LinkedIn account credentials
- Gmail creds (app password or OAuth) if using email or inbox triage
- Apollo API key (optional enrichment)

## Environment Variables

Create a `.env` file in `networking-agent/`:

```
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# LinkedIn login for Playwright
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# Email sending (optional for cold email)
GMAIL_USER=you@yourdomain.com
GMAIL_PASSWORD=your_app_password

# Lead enrichment (optional)
APOLLO_API_KEY=your_apollo_key

# Sending method: linkedin | email
SENDING_METHOD=linkedin
```

## Installation

1. Create and activate a virtual environment (recommended)
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers (only needed for LinkedIn sending and scraping):
   ```bash
   python -m playwright install
   ```
4. Add your `.env` file as shown above

## Data Files (local CSV workflow)

- `leads.csv`: Optional seed leads you already have
- `leads_processed.csv`: Output of `lead_gen.py` after scraping + enrichment
- `leads_with_drafts.csv`: Output of `personalize.py` with `draft_msg`
- `outbox.csv`: Approved messages from `review_ui.py`
- `sent.csv`: Messages successfully sent by `sender.py`

## Usage (end-to-end)

1) Lead Generation (optional if you already have leads)
```bash
python src/lead_gen.py
```
Outputs `leads_processed.csv`.

2) Personalize Messages with OpenAI
```bash
python src/personalize.py
```
Reads `leads_processed.csv`, writes `leads_with_drafts.csv`.

3) Review and Approve Drafts (Human-in-the-loop)
```bash
streamlit run src/review_ui.py
```
Approve messages to append them to `outbox.csv`.

4) Send Messages (LinkedIn or Email)
```bash
python src/sender.py
```
- Uses `SENDING_METHOD=linkedin` to send via Playwright to LinkedIn profiles in `outbox.csv`
- Or set `SENDING_METHOD=email` to send via Gmail to `email` column
- Appends successful sends to `sent.csv`

5) Monitor Replies (Email triage)
```bash
python src/inbox_listener.py
```
- Requires `credentials.json` (Gmail OAuth client) in the project root on first run
- Categorizes replies with GPT and prints results (extend to update your CRM)

6) Dashboard
```bash
streamlit run src/dashboard.py
```
- Shows funnel metrics sourced from the CSVs above
- Default port is exposed in Docker config as 8080

## Docker

Build and run locally:
```bash
docker build -t networking-agent -f infra/Dockerfile .
docker run -p 8080:8080 --env-file .env networking-agent
```

## Cloud (example)

- `infra/cloudformation.yaml` provides a starting point for ECS Fargate
- Store secrets in AWS Secrets Manager; mount as environment variables for the task
- Add networking, subnets, and optionally an ALB if exposing the dashboard

## Security & Compliance

- Keep credentials in environment variables or a secrets manager
- Respect LinkedIn ToS and rate limits; prefer HITL approval for V1
- Review and edit messages before sending; start with low daily volumes

## Testing

- Basic tests for `sender.py` live in `tests/test_sender.py`
- Extend with integration tests for the CSV pipeline as you evolve the system

## License

[Add your chosen license here]
