import requests
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENAI_API_KEY")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.get("https://openrouter.ai/api/v1/credits", headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    data = response.json()
    print(data)
    total_credits_purchased = data.get("data").get("total_credits")
    total_credits_used = data.get("data").get("total_usage")
    remaining_credits = total_credits_purchased - total_credits_used

    print(f"Total credits purchased: ${total_credits_purchased:.2f}")
    print(f"Total credits used: ${total_credits_used:.2f}")
    print(f"Remaining credits: ${remaining_credits:.2f}")

except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}")
except KeyError:
    print("Error parsing API response: Missing expected keys.")