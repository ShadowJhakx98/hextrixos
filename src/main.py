"""
main.py

Entry point. Loads config, creates JARVIS, runs a simple loop for commands.
"""

import asyncio
import json
import os

from jarvis import JARVIS

def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    return {}

async def main():
    config = load_config()
    jarvis = JARVIS(config)

    print("Welcome to JARVIS. Type commands like:")
    print(" - 'stream audio gemini'")
    print(" - 'stream video gemini'")
    print(" - 'stream audio local'")
    print(" - 'stream video local'")
    print(" - 'gemini text Hello AI'")
    print(" - 'local text Hello locally'")
    while True:
        cmd = input("\nYour Command> ").strip()
        if cmd.lower() in ["quit", "exit"]:
            print("Exiting.")
            break
        resp = await jarvis.process_command(cmd)
        print(">>", resp)

if __name__ == "__main__":
    asyncio.run(main())
