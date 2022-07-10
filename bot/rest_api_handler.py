import logging
from functools import lru_cache
from pprint import pprint
from typing import Dict, Optional
from dotenv import dotenv_values
import requests
import json
import base64
import hmac
import hashlib
import time
from string import Template
from bot.models import GeminiOrder
from bot.credentials import load_credentials, GeminiCredentials
from bot.utils import dotenv_path

logger = logging.getLogger(__name__)


@lru_cache(None)
def _get_base_url() -> str:
    environment = (
        ".sandbox"
        if dotenv_values(dotenv_path)["ENVIRONMENT"].lower() == "sandbox"
        else ""
    )
    base_url = Template("https://api$ENVIRONMENT.gemini.com").substitute(
        ENVIRONMENT=environment
    )
    return base_url


def compute_payload_nonce():
    epoch_time = time.time()
    payload_nonce = str(int(epoch_time))
    return payload_nonce


def _create_encoded_payload(payload: dict):
    return base64.b64encode(json.dumps(payload).encode())


def _create_post_request_headers(payload: dict):
    trader_credentials: GeminiCredentials = load_credentials()
    encoded_payload = _create_encoded_payload(payload)
    signature = hmac.new(
        trader_credentials.api_secret.encode(), encoded_payload, hashlib.sha384
    ).hexdigest()
    request_headers = {
        "Content-Type": "text/plain",
        "Content-Length": "0",
        "X-GEMINI-APIKEY": trader_credentials.api_key,
        "X-GEMINI-PAYLOAD": encoded_payload,
        "X-GEMINI-SIGNATURE": signature,
        "Cache-Control": "no-cache",
    }
    return request_headers


def request_private_endpoint(endpoint: str, payload: dict) -> dict:
    base_url = _get_base_url()
    response = requests.post(
        f"{base_url}{endpoint}",
        headers=_create_post_request_headers(payload),
    ).json()
    return response


def request_public_endpoint(endpoint: str, url_parameters=None) -> dict:
    base_url = _get_base_url()
    endpoint = add_url_parameters_to_endpoint(endpoint, base_url, url_parameters)
    response = requests.get(
        endpoint,
    ).json()
    return response


def add_url_parameters_to_endpoint(endpoint, base_url, url_parameters):
    assert isinstance(url_parameters, dict), "URL parameters should be a dict"
    endpoint = f"{base_url}{endpoint}"
    if not url_parameters:
        return endpoint
    for key, value in url_parameters.items():
        endpoint += f"?{key}={value}" if "?" not in endpoint else f"&{key}={value}"
    return endpoint


def cast_response_to_gemini_order(response: Dict[str, str]) -> Optional[GeminiOrder]:
    try:
        return GeminiOrder(
            avg_execution_price=float(response["avg_execution_price"]),
            executed_amount=float(response["executed_amount"]),
            options=response["options"],
            order_id=int(response["order_id"]),
            original_amount=float(response["original_amount"]),
            price=float(response["price"]),
            remaining_amount=float(response["remaining_amount"]),
            side=response["side"],
            symbol=response["symbol"],
            timestamp=int(response["timestamp"]),
            type=response["type"],
        )
    except Exception:
        logger.exception("Failed to make order")
        print("Response from API:")
        pprint(response)
