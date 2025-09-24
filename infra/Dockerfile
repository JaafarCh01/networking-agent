# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables (placeholders - use a .env file or secrets manager in production)
# ENV OPENAI_API_KEY="your_key_here"
# ENV LINKEDIN_EMAIL="your_email_here"
# ENV LINKEDIN_PASSWORD="your_password_here"

# The command to run the application (e.g., the streamlit dashboard)
# You can override this with docker run command
CMD ["streamlit", "run", "src/dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]
