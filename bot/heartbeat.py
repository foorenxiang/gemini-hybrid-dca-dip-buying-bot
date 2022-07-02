import time
from dotenv import dotenv_values
from bot.rest_api_handler import request_private_endpoint

_last_time = None

env_values = dotenv_values(".env")


def _set_last_heartbeat_time(time: int):
    global _last_time
    _last_time = time


def _get_last_heartbeat_time():
    return 0 if _last_time is None else _last_time


def _send_heartbeat(nonce: str):
    endpoint = "/v1/heartbeat"
    payload = {"nonce": nonce, "request": endpoint}
    response = request_private_endpoint(endpoint, payload)

    if response["result"] != "ok":
        print("Failed to send heartbeat, trying again...")
        _send_heartbeat(nonce)
    else:
        print("Heartbeat sent")
        print("Heart acknowledged by API")


def handle_heartbeat():
    current_time = int(time.time())
    if current_time - _get_last_heartbeat_time() > 15:
        _send_heartbeat(nonce=str(current_time))
        _set_last_heartbeat_time(current_time)
