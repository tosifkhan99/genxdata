#!/usr/bin/env python3
"""
Artemis connectivity checker for AMQP (port 5672).

Usage:
  poetry run python tools/check_artemis_console.py --host localhost --port 5672
"""

import argparse
import socket
import sys


def check_connect(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Check AMQP broker TCP connectivity")
    parser.add_argument(
        "--host", default="localhost", help="Broker host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=5672, help="Broker port (default: 5672)"
    )
    parser.add_argument(
        "--timeout", type=float, default=3.0, help="Socket timeout in seconds"
    )

    args = parser.parse_args()

    ok = check_connect(args.host, args.port, args.timeout)
    if ok:
        print(f"✅ TCP connectivity OK: {args.host}:{args.port}")
        return 0
    else:
        print(f"❌ Cannot connect to {args.host}:{args.port}")
        print("Hints:")
        print(" - Ensure Docker container exposes 5672:5672")
        print(" - If using Docker machine, use its IP instead of localhost")
        print(" - Confirm Artemis is running and listening on 0.0.0.0")
        return 1


if __name__ == "__main__":
    sys.exit(main())
