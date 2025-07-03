import argparse
import asyncio
import os
import pathlib
import re
from typing import Final

import aiohttp
import aiofiles

parser = argparse.ArgumentParser(
    description="Python script to translate source code from Simplified Chinese to Traditional Chinese."
)
parser.add_argument("folder", type=str, help="Folder to search for files")
parser.add_argument("extension", type=str, help="File extension to search for")
parser.add_argument("--modify", action="store_true", help="Modify the files")
parser.add_argument(
    "--proxy", type=str, help="HTTP proxy URL (e.g., http://proxy.example.com:8080)"
)
args = parser.parse_args()


FOLDER: Final[str] = args.folder
EXTENSION: Final[str] = args.extension
MODIFY: Final[bool] = args.modify
PROXY: Final[str | None] = args.proxy or os.getenv("HTTP_PROXY")

API: Final[str] = "https://api.zhconvert.org/convert"


def extract_chinese_chars(text: str) -> list[str]:
    text_no_comments = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    text_no_comments = re.sub(r"/\*.*?\*/", "", text_no_comments, flags=re.DOTALL)
    return re.findall(r"[\u4e00-\u9fff]+", text_no_comments)


async def convert_to_traditional(session: aiohttp.ClientSession, text: str) -> str:
    params = {"text": text, "converter": "Traditional"}
    async with session.get(API, params=params, proxy=PROXY) as response:
        data = await response.json()
        return data["data"]["text"]


async def main():
    api_cache: dict[str, str] = {}
    checked_files = 0
    modified_files = 0

    connector = aiohttp.TCPConnector() if not PROXY else None
    async with aiohttp.ClientSession(connector=connector) as session:
        # Search recursively for files with the extension
        for path in pathlib.Path(FOLDER).rglob(f"*{EXTENSION}"):
            print(f"Checking: {path}")
            async with aiofiles.open(path, "r", encoding="utf-8") as file:
                text = await file.read()
                checked_files += 1

                chinese_chars = extract_chinese_chars(text)
                if not chinese_chars:
                    continue

                print(f"Found {len(chinese_chars)} Chinese characters")

                if not MODIFY:
                    continue

                # Get unique characters to avoid duplicate API calls
                unique_chars = list(set(chinese_chars))

                # Prepare translation tasks for characters not in cache
                tasks = []
                chars_to_translate = []
                for char in unique_chars:
                    if char not in api_cache:
                        chars_to_translate.append(char)
                        tasks.append(convert_to_traditional(session, char))

                # Execute all API calls concurrently with delay
                if tasks:
                    translations = []
                    for i, task in enumerate(tasks):
                        if i > 0:  # Add delay between requests
                            await asyncio.sleep(0.1)
                        translation = await task
                        translations.append(translation)

                    # Update cache with new translations
                    for char, translation in zip(chars_to_translate, translations):
                        api_cache[char] = translation

                # Replace all Chinese characters with their translations
                for char in chinese_chars:
                    translation = api_cache[char]
                    text = text.replace(char, translation)

                # Write the modified text back to the file
                async with aiofiles.open(path, "w", encoding="utf-8") as file:
                    print(f"Modifying: {path}")
                    await file.write(text)
                    modified_files += 1

    print(f"Checked {checked_files} files")
    print(f"Modified {modified_files} files")


asyncio.run(main())
