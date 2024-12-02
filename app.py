"""
Adeel's Copilot Usage Calculation API

This Flask application calculates and returns usage data for Orbital Copilot, 
an AI assistant for real estate lawyers. It fetches messages and reports from 
external report API to calculate credits consumed per message based on various rules, 
including base cost, character count, word length, unique word bonuses, and palindromes.

Author: Adeel Zafar
Date: 2024-11-29
"""

from flask import Flask, jsonify
import requests
import re
import logging
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Union

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants for credit calculation
CREDIT_COSTS: Dict[str, Union[int, float]] = {
    "base": 1,
    "char": 0.05,
    "third_vowel": 0.3,
    "length_penalty_threshold": 100,
    "length_penalty": 5,
    "unique_word_bonus": -2,
}
VOWELS: str = "aeiouAEIOU"
WORD_PATTERN: str = r"[a-zA-Z'-]+"

def is_palindrome(text: str) -> bool:
    """
    Check if the entire message is a palindrome after converting all uppercase letters into lowercase letters and removing all non-alphanumeric chars
    """
    cleaned_text: str = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
    return cleaned_text == cleaned_text[::-1]

def extract_words(text: str) -> List[str]:
    return re.findall(WORD_PATTERN, text)

def calculate_third_vowel_cost(text: str) -> float:
    """
    If any third (i.e. 3rd, 6th, 9th) character is an uppercase or lowercase vowel add 0.3 credits for each occurrence.
    """
    return sum(
        CREDIT_COSTS["third_vowel"] for i, char in enumerate(text, start=1) if i % 3 == 0 and char in VOWELS
    )

def calculate_char_cost(message_length: int) -> float:
    return CREDIT_COSTS["char"] * message_length

def calculate_word_costs(words: List[str]) -> float:
    """
    Calculate the total word cost based on word length categories.
    """
    category_costs: Dict[str, float] = {
        "short": 0.1,
        "medium": 0.2,
        "long": 0.3,
    }
    ranges: Dict[str, Tuple[int, Union[int, float]]] = {
        "short": (1, 3),
        "medium": (4, 7),
        "long": (8, float("inf")),
    }
    # Calculate cost by summing the number of words in each range multiplied by the category cost
    return sum(
        sum(1 for word in words if r[0] <= len(word) <= r[1]) * category_costs[c]
        for c, r in ranges.items()
    )

def calculate_credits(message_text: str, message_id: int) -> float:
    message_length: int = len(message_text)
    words: List[str] = extract_words(message_text)

    char_cost: float = calculate_char_cost(message_length)
    word_costs: float = calculate_word_costs(words)
    third_vowel_cost: float = calculate_third_vowel_cost(message_text)
    length_penalty: int = CREDIT_COSTS["length_penalty"] if message_length > CREDIT_COSTS["length_penalty_threshold"] else 0
    unique_word_bonus: int = CREDIT_COSTS["unique_word_bonus"] if len(set(words)) == len(words) else 0

    total_cost: float = (
        CREDIT_COSTS["base"]
        + char_cost
        + word_costs
        + third_vowel_cost
        + length_penalty
        + unique_word_bonus
    )

    if is_palindrome(message_text):
        total_cost *= 2

    total_cost = max(1, round(total_cost, 2))
    logging.info(f"Calculated credits: {total_cost} for message id: {message_id}")
    return total_cost

def fetch_messages() -> List[Dict[str, Union[str, int]]]:
    messages_url: str = "https://owpublic.blob.core.windows.net/tech-task/messages/current-period"
    try:
        response: requests.Response = requests.get(messages_url)
        response.raise_for_status()
        response_data: Dict[str, Union[List[Dict[str, Union[str, int]]], str]] = response.json()
        return response_data.get("messages", [])
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request to fetch messages failed: {e}")
        raise Exception("Failed to fetch messages due to an HTTP request error.")
    except ValueError as e:
        logging.error(f"Failed to parse JSON from messages API: {e}")
        raise Exception("Invalid JSON response from messages API.")

@lru_cache(maxsize=100)  # Cache up to 100 unique report IDs
def fetch_report(report_id: str) -> Optional[Dict[str, Union[str, int]]]:
    report_url: str = f"https://owpublic.blob.core.windows.net/tech-task/reports/{report_id}"
    try:
        response: requests.Response = requests.get(report_url)
        if response.status_code == 200:
            logging.info(f"Fetched report for report_id {report_id} successfully.")
            return response.json()
        elif response.status_code == 404:
            logging.warning(f"Report not found for report_id {report_id}.")
            return None
        elif response.status_code == 403:
            logging.error(f"Access forbidden for report_id {report_id}.")
            raise Exception("Access to report details is forbidden.")
        elif response.status_code >= 500:
            logging.error(f"Server error while fetching report_id {report_id}.")
            raise Exception("The reports service is currently unavailable.")
        else:
            logging.error(f"Unexpected HTTP status {response.status_code} for report_id {report_id}.")
            raise Exception(f"Unexpected error for report_id {report_id}.")
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request to fetch report {report_id} failed: {e}")
        raise Exception(f"Failed to fetch report {report_id} due to an HTTP request error.")

def process_report(report_id: str, message_text: str, message_id: int) -> Tuple[Optional[str], float]:
    report_data: Optional[Dict[str, Union[str, int]]] = fetch_report(report_id)
    if report_data:
        logging.info(f"Report {report_id} fetched successfully.")
        return report_data.get("name"), report_data.get("credit_cost", 0)

    logging.warning(f"Report {report_id} not found for message {message_id}.")
    return None, calculate_credits(message_text, message_id)

def process_messages(messages: List[Dict[str, Union[str, int]]]) -> List[Dict[str, Union[int, float, str]]]:
    usage_data: List[Dict[str, Union[int, float, str]]] = []
    for message in messages:
        usage_data.append(process_message(message))
    return usage_data

def process_message(message: Dict[str, Union[str, int]]) -> Dict[str, Union[int, float, str]]:
    try:
        if not isinstance(message, dict):
            raise ValueError(f"Invalid message format: {message}")
        message_id: int = message["id"]
        timestamp: str = message["timestamp"]
        report_id: Optional[str] = message.get("report_id")
        if report_id:
            report_name, credits_used = process_report(report_id, message["text"], message_id)
        else:
            report_name = None
            credits_used = calculate_credits(message["text"], message_id)

        usage_entry: Dict[str, Union[int, float, str]] = {
            "message_id": message_id,
            "timestamp": timestamp,
            "credits_used": credits_used,
        }
        if report_name:
            usage_entry["report_name"] = report_name
        return usage_entry
    except KeyError as e:
        raise ValueError(f"Missing key in message: {e}")

@app.route('/usage', methods=['GET'])
def usage() -> Dict[str, Union[str, List[Dict[str, Union[int, float, str]]]]]:
    try:
        messages: List[Dict[str, Union[str, int]]] = fetch_messages()
        logging.info(f"Fetched {len(messages)} messages successfully.")
        usage_data: List[Dict[str, Union[int, float, str]]] = process_messages(messages)
        logging.info(f"Successfully processed {len(usage_data)} messages.")
        return jsonify({"usage": usage_data})
    except ValueError as e:
        logging.error(f"Invalid data: {e}")
        return jsonify({"error": str(e)}), 400
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return jsonify({"error": "Failed to fetch data from external service."}), 503

if __name__ == '__main__':
    app.run(debug=True)

