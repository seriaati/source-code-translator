import argparse
import asyncio
import pathlib
import re
from typing import Final

import requests

parser = argparse.ArgumentParser(
    description="Python script to convert source code from Simplified Chinese to Traditional Chinese."
)
parser.add_argument("folder", type=str, help="Folder to search for files")
parser.add_argument("extension", type=str, help="File extension to search for")
parser.add_argument("--modify", action="store_true", help="Modify the files")
args = parser.parse_args()


FOLDER: Final[str] = args.folder
EXTENSION: Final[str] = args.extension
MODIFY: Final[bool] = args.modify

API: Final[str] = "https://api.zhconvert.org/convert"


def extract_chinese_chars(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]+", text)


def convert_to_traditional(text: str) -> str:
    data = requests.get(API, params={"text": text, "converter": "Traditional"}).json()
    return data["data"]["text"]


async def main():
    api_cache: dict[str, str] = {}
    checked_files = 0
    modified_files = 0

    # Search recursively for files with the extension
    for path in pathlib.Path(FOLDER).rglob(f"*{EXTENSION}"):
        print(f"Checking: {path}")
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()
            checked_files += 1

            chinese_chars = extract_chinese_chars(text)
            if not chinese_chars:
                continue

            print(f"Found {len(chinese_chars)} Chinese characters")

            if not MODIFY:
                continue

            for char in chinese_chars:
                translation = api_cache.get(char)
                if not translation:
                    translation = convert_to_traditional(char)
                    api_cache[char] = translation
                text = text.replace(char, translation)

            # Write the modified text back to the file
            with open(path, "w", encoding="utf-8") as file:
                print(f"Modifying: {path}")
                file.write(text)
                modified_files += 1

    print(f"Checked {checked_files} files")
    print(f"Modified {modified_files} files")


asyncio.run(main())
