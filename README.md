# Adeel's Copilot Usage API

Copilot is an AI assistant designed for Real Estate lawyers, allowing them to ask questions and generate reports about legal documents such as leases. This API processes usage data for the current billing period and calculates the credits consumed based on specific rules.

## Features

- Fetches all raw message data from a remote API.
- Queries a report by ID to fetch its name and credit cost.
- Calculates credits consumed by each message based on the following:
  - Fixed report credit cost (when a report is available).
  - Text-based calculation rules include Character count, word length, third vowels, penalties, palindrome, unique word bonus.
- Returns usage data for each message in a JSON format with report_name(if applicable) and credits_used.
- Since reports are reused, can fetch them at once. Using LRU cache to get 100 unique reports at once.
- Logging all important details when processing each message, and also its report.
- Exception Handling and providing appropriate error messages.
- Unit tests: Added 11 unit tests to cover all functionalities of the Copilot.

## Installation

**1. Clone the repository:**
```
git@github.com:iadeelzafar/copilot.git
```
Navigate to the cloned repository
```
cd copilot
```
**2. Install the dependencies**

First off, you need Python if not already
```
sudo apt install python3
```
Then install the requirements using pip3
```
pip3 install -r requirements.txt
```

**3. Run the Application**

```
python3 app.py
```
![app_run](https://github.com/user-attachments/assets/e5a7343c-9dfc-459a-9af4-9758822f61f1)

The API will be accessible at http://127.0.0.1:5000/usage

![result](https://github.com/user-attachments/assets/82c50eba-295e-44c2-8306-a3447fb3f9fd)

**Endpoints** /usage (GET)

Returns usage data for the current billing period.

Can see the GET request coming in here, with status code 200

![logs_1](https://github.com/user-attachments/assets/9f18b66a-f45c-441b-9f24-264495778522)

```
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
```

**5. Testing**

Unit tests are included to ensure correct functionality.

Run tests with:
```
python3 -m unittest test_app.py
```
![test_ss](https://github.com/user-attachments/assets/8f827e99-6f9a-41e0-ae7c-77a57d1f2377)


