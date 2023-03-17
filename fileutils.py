def get_file_contents(self, file_dir: str) -> str:
    """
    Gets the contents of a file.

    Args:
        file_dir (str): The directory where the file is located.

    Returns:
        str: The contents of the file.
    """
    file_dir = file_dir or config.get_json_directory()
    if file_dir is None:
        print("Error: No file directory specified. Pass --json [FILE]")
        return 1
    with open(file_dir, "r") as f:
        return f.read()

def write_file(self, file_dir: str, new_contents: str):
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

def create_qr_code(self, link: str) -> str:
    out = io.StringIO()
    qr = segno.make(link)
    qr.terminal(out, compact=True, border=2)
    utf_code = out.getvalue()
    return utf_code