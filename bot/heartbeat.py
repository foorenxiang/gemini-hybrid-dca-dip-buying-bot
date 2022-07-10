import time
from dotenv import dotenv_values
from bot.rest_api_handler import request_private_endpoint
from bot.utils import dotenv_path

_last_time = None

env_values = dotenv_values(dotenv_path)


def _set_last_heartbeat_time(time: int):
    global _last_time
    _last_time = time


def _get_last_heartbeat_time():
    return 0 if _last_time is None else _last_time


def _send_heartbeat(nonce: str):
    print("Sending heartbeat")
    endpoint = "/v1/heartbeat"
    payload = {"nonce": nonce, "request": endpoint}
    response = request_private_endpoint(endpoint, payload)

    if response["result"] == "ok":
        print("Heartbeat acknowledged")
        return

    print("Failed to send heartbeat, trying again...")
    _send_heartbeat(nonce)


def handle_heartbeat():
    current_time = int(time.time())
    if current_time - _get_last_heartbeat_time() > 15:
        _send_heartbeat(nonce=str(current_time))
        _set_last_heartbeat_time(current_time)
