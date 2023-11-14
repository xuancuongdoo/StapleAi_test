from flask.json import jsonify as flask_jsonify
from datetime import datetime, timedelta


MAX_REQUESTS_PER_MINUTE = 5
request_count = 0
last_request_time = datetime.now()


def validate_prompt_data(data):
    """
    Validates and serializes prompt data.

    Parameters:
    - data (dict): The JSON payload received in the request.

    Returns:
    - prompt (str): The serialized prompt data.
    - error_response (tuple): A tuple containing the Flask JSON response and status code.
    """
    message = data.get("message")

    if not message:
        error_response = (
            flask_jsonify({"error": "Invalid request. 'prompt' field is required."}),
            400,
        )
        return None, error_response
    return message, None


def is_rate_limited():
    """
    Determines if the rate limit has been reached for making requests.

    Returns:
        bool: True if the rate limit has been reached, False otherwise.
    """
    global request_count, last_request_time
    current_time = datetime.now()

    if current_time - last_request_time < timedelta(minutes=1):
        request_count += 1
        last_request_time = current_time
        return request_count > MAX_REQUESTS_PER_MINUTE
    else:
        request_count = 1
        last_request_time = current_time
        return False
