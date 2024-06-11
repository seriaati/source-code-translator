# source-code-translator

將程式碼由簡體中文轉換為繁體中文的工具。

## 使用方式

1. `git clone` 此專案。
2. `pip install -r requirements.txt` 安裝相依套件。
3. 執行 `python translator.py <code_folder> <file_extension> --modify` 以將指定資料夾中的程式碼轉換為繁體中文。例如，`python translator.py ./code .py --modify` 會將 `code` 資料夾中的所有 Python 檔案轉換為繁體中文。若不加上 `--modify` 參數，則程式只會列印出已檢查過的檔案以及找到的中文字，而不會進行翻譯。
