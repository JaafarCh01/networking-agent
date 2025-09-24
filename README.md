# Networking Agent

An automated networking tool that helps streamline professional outreach through LinkedIn and email. The tool assists in lead generation, message personalization, and outreach campaign management with a user-friendly dashboard interface.

## Features

- **Lead Generation**: Automated LinkedIn profile scraping based on search criteria
- **Message Personalization**: AI-powered message generation using OpenAI
- **Multi-Channel Outreach**: Support for both LinkedIn messages and email
- **Campaign Dashboard**: Streamlit-based interface for monitoring outreach campaigns
- **Reply Monitoring**: Gmail integration for tracking and triaging responses

## Project Structure

```
networking-agent/
├── src/
│   ├── lead_gen.py        # LinkedIn profile scraping and lead generation
│   ├── personalize.py     # OpenAI-powered message personalization
│   ├── sender.py          # Message sending functionality (LinkedIn/Email)
│   ├── dashboard.py       # Streamlit dashboard for campaign monitoring
│   ├── review_ui.py       # Interface for reviewing generated messages
│   └── inbox_listener.py  # Gmail integration for response tracking
├── infra/
│   ├── Dockerfile         # Container configuration
│   └── cloudformation.yaml # AWS infrastructure setup
└── requirements.txt       # Python dependencies
```

## Prerequisites

- Python 3.9+
- OpenAI API key
- LinkedIn account credentials
- Gmail API credentials (for email functionality)

## Environment Variables

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password
SENDING_METHOD=linkedin  # or "email"
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`

## Usage

### Running the Dashboard

```bash
streamlit run src/dashboard.py
```

The dashboard will be available at `http://localhost:8080`

### Lead Generation

```bash
python src/lead_gen.py
```

This will:
1. Load existing leads from CSV
2. Scrape new leads from LinkedIn
3. Deduplicate leads
4. Enrich lead data using Apollo
5. Save processed leads to CSV

### Sending Messages

```bash
python src/sender.py
```

This script will:
1. Read pending messages from the outbox
2. Send messages via LinkedIn or email based on configuration
3. Track sent messages
4. Handle rate limiting and delays

## Docker Support

Build and run the container:

```bash
docker build -t networking-agent -f infra/Dockerfile .
docker run -p 8080:8080 networking-agent
```

## Security Notes

- Store sensitive credentials securely using environment variables or a secrets manager
- Follow rate limiting guidelines for LinkedIn and email services
- Review and approve generated messages before sending
- Comply with LinkedIn's terms of service and email regulations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

[Add your chosen license here]
