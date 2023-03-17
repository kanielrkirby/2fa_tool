import io
import segno
import json as JSON
import os
import pyotp
import time

def get_file_contents(file_dir: str) -> str:
    """
    Gets the contents of a file.

    Args:
        file_dir (str): The directory where the file is located.

    Returns:
        str: The contents of the file.
    """
    if file_dir is None:
        print("Error: No file directory specified. Pass --json [FILE]")
        return 1
    with open(file_dir, "r") as f:
        return f.read()

def write_file(file_dir: str, new_contents: str, config):
    """
    Writes new contents to a file.

    Args:
        file_dir (str): The directory where the file is located.
        new_contents (str): The new contents to be written to the file.
    """
    file_dir = file_dir or config.get_json_directory()
    if file_dir is None:
        print("Error: No file directory specified. Pass --json [FILE]")
        return 1
    with open(file_dir, "w") as f:
        f.write(new_contents)

    return 0

def create_qr_code(link: str) -> str:
    out = io.StringIO()
    qr = segno.make(link)
    qr.terminal(out, compact=True, border=2)
    utf_code = out.getvalue()
    return utf_code

def get_data_list(json: str, config) -> list:
    json = test_json(json, config)
    if json is None:
        print("No JSON file specified. Pass --json [FILE]")
        return 1
    contents = get_file_contents(json)
    data_list = JSON.loads(contents)
    return data_list

def test_json(json: str, config) -> str:
    json = json or config.get_json_directory() or None
    if json is None:
        print("No JSON file specified. Pass --json [FILE]")
        return None
    if not os.path.isfile(json):
        print("File does not exist")
        return None
    if not json.endswith(".json"):
        print("File is not valid JSON")
        return None
    
    return json

def test_txt(txt: str, config) -> int:
    txt = txt or config.get_txt_directory() or None

    if txt is None:
        print("No TXT file specified. Pass --txt [FILE]")
        return 1
    if not os.path.isfile(txt):
        print("File does not exist")
        return 1
    if not txt.endswith(".txt"):
        print("File is not valid TXT")
        return 1
    
    return 0

def gen_code(secret: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.now()