import json
import sys
import segno
import io
import argparse
from typing import List
import datetime
import os


class TwoFactorAuthTool:
    """
    A class that represents a 2FA tool for adding and updating 2FA information.

    Attributes:
        json_file_dir (str): The directory where the JSON file is located.
        txt_file_dir (str): The directory where the TXT file is located.
        backups_dir (str): The directory where backup JSON files are stored.
    """

    def __init__(self, json_file_dir: str, txt_file_dir: str, backups_dir: str):
        """
        Initializes the TwoFactorAuthTool object.

        Args:
            json_file_dir (str): The directory where the JSON file is located.
            txt_file_dir (str): The directory where the TXT file is located.
            backups_dir (str): The directory where backup JSON files are stored.
        """
        self.json_file_dir = json_file_dir
        self.txt_file_dir = txt_file_dir
        self.backups_dir = backups_dir

    def test_file_exists(self, file_dir: str) -> bool:
        """
        Tests whether a file exists.

        Args:
            file_dir (str): The directory where the file is located.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.isfile(file_dir)

    def test_file_json(self, file_dir: str) -> bool:
        """
        Tests whether a file is a valid JSON file.

        Args:
            file_dir (str): The directory where the file is located.

        Returns:
            bool: True if the file is a valid JSON file, False otherwise.
        """
        return file_dir.endswith(".json")

    def get_file_contents(self, file_dir: str) -> str:
        """
        Gets the contents of a file.

        Args:
            file_dir (str): The directory where the file is located.

        Returns:
            str: The contents of the file.
        """
        with open(file_dir, "r") as f:
            return f.read()

    def write_file(self, file_dir: str, new_contents: str):
        """
        Writes new contents to a file.

        Args:
            file_dir (str): The directory where the file is located.
            new_contents (str): The new contents to be written to the file.
        """
        with open(file_dir, "w") as f:
            f.write(new_contents)

    def create_backup(self):
        """
        Creates a backup of the JSON file.
        """
        os.makedirs(self.backups_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file_name = f"2fa_{timestamp}.json"
        backup_file_path = os.path.join(self.backups_dir, backup_file_name)

        contents = self.get_file_contents(self.json_file_dir)

        latest_backup = None
        latest_mtime = 0
        for file in os.listdir(self.backups_dir):
            file_path = os.path.join(self.backups_dir, file)
            if file.endswith(".json") and os.path.getmtime(file_path) > latest_mtime:
                latest_mtime = os.path.getmtime(file_path)
                latest_backup = file_path

        if latest_backup is not None:
            latest_backup_contents = self.get_file_contents(latest_backup)
            if contents == latest_backup_contents:
                print("No changes detected. Backup not created.")
                return

        self.write_file(backup_file_path, contents)
        print(f"Backup created:{backup_file_path}")
    def create_qr_code(self, link: str) -> str:
        """
        Creates a QR code from a given link.

        Args:
            link (str): The link to be used to generate the QR code.

        Returns:
            str: The QR code in UTF format.
        """
        out = io.StringIO()
        qr = segno.make(link)
        qr.terminal(out, compact=True, border=2)
        utf_code = out.getvalue()
        return utf_code

    def add(self, name: str, issuer: str, secret: str, backup: str, phrase: str, force: bool):
        """
        Adds new 2FA information to the JSON file.

        Args:
            name (str): The name of the account.
            issuer (str): The issuer of the 2FA.
            secret (str): The secret key for the 2FA.
            backup (str): The backup code for the 2FA.
            phrase (str): The recovery phrase for the 2FA.
            force (bool): A flag indicating whether to force adding duplicate data.

        Returns:
            int: 0 if the operation is successful, 1 otherwise.
        """
        self.create_backup()
        if not self.test_file_exists(self.json_file_dir):
            print("File does not exist")
            return 1
        if not self.test_file_json(self.json_file_dir):
            print("File is not valid JSON")
            return 1

        contents = self.get_file_contents(self.json_file_dir)
        data_list: List[dict] = json.loads(contents)
        for data in data_list:
            if ("name" in data and data["name"] == name and name is not None) or \
                    ("issuer" in data and data["issuer"] == issuer and issuer is not None) or \
                    ("secret" in data and data["secret"] == secret and secret is not None) or \
                    ("backup" in data and data["backup"] == backup and
                backup is not None) or \
                ("phrase" in data and data["phrase"] == phrase and phrase is not None):
                if not force:
                    print("Duplicate data. Pass -f to force.")
                    return 1
        obj = {"name": name, "issuer": issuer}
        if secret:
            obj["secret"] = secret
        if backup:
            obj["backup"] = backup
        if phrase:
            obj["phrase"] = phrase
        data_list.append(obj)
        data_list.sort(key=lambda x: x["name"].lower())

        self.write_file(self.json_file_dir, json.dumps(data_list))

        return 0

    def remove(self, name: str) -> int:
        """
        Removes 2FA information from the JSON file.

        Args:
            name (str): The name of the account to be removed.

        Returns:
            int: 0 if the operation is successful, 1 otherwise.
        """
        self.create_backup()
        if not self.test_file_exists(self.json_file_dir) or not self.test_file_json(self.json_file_dir):
            return 1

        contents = self.get_file_contents(self.json_file_dir)
        data_list: List[dict] = json.loads(contents)

        data_list = [data for data in data_list if not (data.get("name") == name)]

        self.write_file(self.json_file_dir, json.dumps(data_list))
        return 0

    def update_text(self):
        """
        Updates the TXT file with the latest 2FA information.
        """
        if not self.test_file_exists(self.json_file_dir):
            print("File does not exist")
            return 1
        if not self.test_file_json(self.json_file_dir):
            print("File is not valid JSON")
            return 1

        contents = self.get_file_contents(self.json_file_dir)
        all_info = ""
        names = ""
        secrets = ""
        links = ""
        backups = ""
        phrases = ""
        qrs = ""
        div = "-" * 50
        ret = "\n\n\n"
        nl = "\n"

        def title(t: str) -> str:
            return f"{div}\n{t}\n{div}"

        data_list: List[dict] = json.loads(contents)
        for data in data_list:
            name, issuer, secret, backup, phrase = data.get("name"), data.get("issuer"), data.get("secret"), data.get("backup"), data.get("phrase")

            link = f"otpauth://totp/{name}?secret={secret}&issuer={issuer}".replace(" ", "%20")
            qr = self.create_qr_code(link)
            all_info += f"{f'Name:       {name}{nl}' if name else ''}{f'Secret:     {secret}{nl}' if secret else ''}{f'Link:       {link}{nl}' if link else ''}{f'Backup:     {backup}{nl}' if backup else ''}{f'Phrase:     {phrase}{nl}' if phrase else ''}\n\n\n"
            secrets += f"{name}\n{secret}\n\n\n" if secret else ""
            links += f"{link}\n" if link else ""
            backups += f"{name}\n\n{backup}\n\n\n" if backup else ""
            qrs += f"{name}\n\n{qr}\n\n\n" if qr else ""
            phrases += f"{name}\n\n{phrase}\n\n\n" if phrase else ""
            names += f"{name}\n" if name else ""

        TXT = f"\n{title('All')}\n\n{all_info}\n{div}{title('Secrets')}\n{secrets}\n{div}{title('Links')}\n{links}\n{div}{title('Backups')}\n{backups}\n{div}{title('Phrases')}\n{phrases}\n{div}{title('Names')}\n{names}\n{title('QR Codes')}\n{qrs}"
        self.write_file(self.txt_file_dir, TXT)
        return 0

def main():
    """
    The main function that handles command-line arguments and calls the appropriate methods.
    """
    parser = argparse.ArgumentParser(description="2FA tool for adding and updating 2FA information.")
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # Add parser
    parser_add = subparsers.add_parser("add", help="Add new 2FA information.")
    parser_add.add_argument("--name", required=True, help="Name of the account.")
    parser_add.add_argument("--issuer", required=True, help="Issuer of the 2FA.")
    parser_add.add_argument("--secret", help="Secret key for 2FA.")
    parser_add.add_argument("--backup", help="Backup code for 2FA.")
    parser_add.add_argument("--phrase", help="Recovery phrase for 2FA.")
    parser_add.add_argument("-f", "--force", action="store_true", help="Force adding duplicate data.")

    # Remove parser
    parser_remove = subparsers.add_parser("remove", help="Remove 2FA information.")
    parser_remove.add_argument("--name", required=True, help="Name of the account.")

    # Update parser
    parser_update = subparsers.add_parser("update", help="Update the 2FA text file.")

    args = parser.parse_args()

    json_file_dir = "/Volumes/VERACRYPT/2fa.json"
    txt_file_dir = "/Volumes/VERACRYPT/2fa.txt"
    backups_dir = "/Volumes/VERACRYPT/backups"
    tool = TwoFactorAuthTool(json_file_dir, txt_file_dir, backups_dir)

    if args.command == "add":
        try:
            return_code = tool.add(args.name, args.issuer, args.secret, args.backup, args.phrase, args.force)
            if return_code == 0:
                print("Successfully added 2FA information.")
            else:
                print("Failed to add 2FA information.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "remove":
        try:
            return_code = tool.remove(args.name)
            if return_code == 0:
                print("Successfully removed 2FA information.")
            else:
                print("Failed to remove 2FA information.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "update":
        try:
            return_code = tool.update_text()
            if return_code == 0:
                print("Successfully updated 2FA text file.")
            else:
                print("Failed to update 2FA text file.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
