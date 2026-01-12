"""Test script to run in the tui"""

import logging
import argparse

LOGGER = logging.getLogger("test_script")


def main(args: argparse.Namespace | dict) -> None:
    if type(args) is dict:
        args = argparse.Namespace(**args)
    print("Main function of test_script called.")
    LOGGER.info("Main function of test_script called.")
    # legacy_script.py
    print("Hello! What is your name?")
    name = input()
    print(f"Nice to meet you, {name}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test script to run in the tui")
    parser.add_argument("--ip", default="10.0.190.70", help="ip address")
    parser.add_argument("--port", type=int, help="port number")
    parser.add_argument("--loglevel", default="INFO", help="logging level")
    parser.add_argument("--logfile", type=str, help="log file")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    main(args)
