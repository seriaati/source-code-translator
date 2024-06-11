# source-code-translator

Python script to translate source code from Simplified Chinese to Traditional Chinese.

## Usage

1. Clone this repository.
2. Run `pip install -r requirements.txt` to install the required packages.
3. Run `python translator.py <code_folder> <file_extension> --modify` to convert the source code in the specified folder to Traditional Chinese. For example, `python translator.py ./code .py --modify` will convert all Python files in the `code` folder to Traditional Chinese. Without the `--modify` flag, the script will only print checked files and found characters to the console, without translating the files.
