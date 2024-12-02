# Adeel's Copilot Usage API

Orbital Copilot is an AI assistant designed for Real Estate lawyers, allowing them to ask questions and generate reports about legal documents such as leases. This API processes usage data for the current billing period and calculates the credits consumed based on specific rules.

## Features

- Fetches raw message data from a remote API.
- Queries a report by ID to fetch its name and credit cost.
- Calculates credits consumed by each message based on the following:
  - Fixed report credit cost (when a report is available).
  - Character count, word length, third vowels, penalties, and bonuses (for text-based messages).
- Returns usage data in a JSON format.

## Installation

1. Clone the repository:

2. Install the dependencies

3. Run the Application

python app.py

The API will be accessible at http://127.0.0.1:5000/usage

4. Endpoints
/usage (GET)


Description: Returns usage data for the current billing period.

Response Format:

{
  "usage": [
    {
      "message_id": 1000,
      "timestamp": "2024-04-29T02:08:29.375Z",
      "report_name": "Tenant Obligations Report",
      "credits_used": 79
    },
    {
      "message_id": 1001,
      "timestamp": "2024-04-29T03:25:03.613Z",
      "credits_used": 5.2
    }
  ]
}

5. Testing
Unit tests are included to ensure correct functionality.

Run tests with:

python -m unittest test_app.py
