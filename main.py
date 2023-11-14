import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request
from openai import OpenAI, RateLimitError, AuthenticationError, APIError
import openai
from dotenv import load_dotenv
from flask.json import jsonify as flask_jsonify
from db import connect_to_database, log_error
from helpers import is_rate_limited, validate_prompt_data

load_dotenv()


app = Flask(__name__)

open_api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=open_api_key)


@app.route("/openai-completion", methods=["POST"])
def openai_completion():
    """
    Generates a completion text using the OpenAI API.

    Parameters:
    - None

    Returns:
    - A JSON response containing the generated completion text.
    - If an error occurs, a JSON response containing the error message.

    Raises:
    - None
    """
    if is_rate_limited():
        return (
            flask_jsonify({"error": "Rate limit exceeded. Please try again later."}),
            429,
        )

    data = request.get_json()
    message, error_response = validate_prompt_data(data)
    if error_response:
        return error_response

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": message}]
        )
        completion_text = response.choices[0].message.content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn, cursor = connect_to_database()
        cursor.execute(
            "INSERT INTO logs (timestamp, prompt, completion) VALUES (?, ?, ?)",
            (timestamp, message, completion_text),
        )
        conn.commit()

        return flask_jsonify({"completion": completion_text})

    except RateLimitError as e:
        log_error(message, f"Rate Limit Error: {str(e)}")
        return (
            flask_jsonify({"error": "Rate limit exceeded. Please try again later."}),
            429,
        )

    except AuthenticationError as e:
        log_error(message, f"Authentication Error: {str(e)}")
        return flask_jsonify({"error": "Authentication failed."}), 401

    except APIError as e:
        log_error(message, f"OpenAI API Error: {str(e)}")
        return flask_jsonify({"error": str(e)}), 500

    except Exception as e:
        log_error(message, f"Error: {str(e)}")
        return flask_jsonify({"error": "An unexpected error occurred."}), 500


if __name__ == "__main__":
    app.run(debug=True)
