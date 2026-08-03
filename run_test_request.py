#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv


REQUEST_FILE = Path("test_request.json")
RESPONSE_FILE = Path("test_response.json")
TRACEBACK_MARKERS = (
    "Traceback (most recent call last)",
    "Exception in ASGI application",
    "Internal Server Error",
)


def load_test_request(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Request file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Request file is not valid JSON: {exc}")

    required = {"category", "tool_name", "api_name", "tool_input", "strip", "toolbench_key"}
    missing = sorted(required - payload.keys())
    if missing:
        raise SystemExit(f"Request is missing required field(s): {', '.join(missing)}")

    if isinstance(payload["tool_input"], str):
        try:
            parsed_input = json.loads(payload["tool_input"])
        except json.JSONDecodeError as exc:
            raise SystemExit(f"tool_input must be a JSON object string: {exc}")
        if not isinstance(parsed_input, dict):
            raise SystemExit("tool_input must decode to a JSON object")
    elif not isinstance(payload["tool_input"], dict):
        raise SystemExit("tool_input must be a JSON object string or object")

    return payload


def mirrorapi_endpoint(base_url: str) -> str:
    return urljoin(base_url.rstrip("/") + "/", "virtual")


def send_request_to_mirrorapi(url: str, payload: dict[str, Any], timeout: int) -> tuple[int, Any]:
    try:
        response = requests.post(
            url,
            headers={"accept": "application/json", "Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=timeout,
        )
    except requests.ConnectionError as exc:
        raise SystemExit(f"MirrorAPI reachable: FAIL\nCould not connect to {url}: {exc}")
    except requests.Timeout:
        raise SystemExit(f"MirrorAPI reachable: FAIL\nRequest timed out after {timeout} seconds: {url}")

    try:
        return response.status_code, response.json()
    except ValueError:
        raise SystemExit(f"Valid JSON returned: FAIL\nHTTP {response.status_code} response was not JSON")


def validate_api_response(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["response must be a JSON object"]
    if not payload:
        return ["response JSON object is empty"]

    text = json.dumps(payload, ensure_ascii=False)
    for marker in TRACEBACK_MARKERS:
        if marker.lower() in text.lower():
            errors.append(f"response contains server failure marker: {marker}")

    if "error" not in payload:
        errors.append("missing outer field: error")
    elif not isinstance(payload["error"], str):
        errors.append("outer field error must be a string")

    if "response" not in payload:
        errors.append("missing outer field: response")
    elif payload["response"] in ("", None, [], {}):
        errors.append("outer field response is empty")

    return errors


def save_api_response(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one StableToolBench MirrorAPI smoke request.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print the request without sending it.")
    parser.add_argument("--timeout", type=int, default=int(os.getenv("MIRRORAPI_TIMEOUT", "60")))
    args = parser.parse_args()

    load_dotenv()
    base_url = os.getenv("MIRRORAPI_URL", "http://127.0.0.1:8080")
    url = mirrorapi_endpoint(base_url)
    request_payload = load_test_request(REQUEST_FILE)

    if args.dry_run:
        print(f"Request URL: {url}")
        print(json.dumps(request_payload, indent=2))
        return 0

    status, response_payload = send_request_to_mirrorapi(url, request_payload, args.timeout)
    print(f"HTTP status: {status}")
    print(json.dumps(response_payload, indent=2, ensure_ascii=False))
    save_api_response(RESPONSE_FILE, response_payload)

    validation_errors = validate_api_response(response_payload)
    if not 200 <= status < 300:
        print("MirrorAPI reachable: PASS")
        print("Request accepted: FAIL")
        print(f"HTTP status was {status}")
        return 1
    if validation_errors:
        print("MirrorAPI reachable: PASS")
        print("Request accepted: PASS")
        print("Valid JSON returned: PASS")
        print("Response structure valid: FAIL")
        for error in validation_errors:
            print(f"- {error}")
        return 1

    print("MirrorAPI reachable: PASS")
    print("Request accepted: PASS")
    print("Valid JSON returned: PASS")
    print("Response structure valid: PASS")
    print("Paid API used: NO")
    print("Overall test: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
