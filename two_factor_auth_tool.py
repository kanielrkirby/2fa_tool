import json as JSON
import os
import io
from config import config
from fileutils import get_file_contents, write_file, create_qr_code
    
class TwoFactorAuthTool:
    """
    A class that represents a 2FA tool for adding and updating 2FA information.
    """

    def add(self, json: str, name: str, issuer: str, secret: str, backup: str, phrase: str, force: bool) -> int:
        """
        Adds new 2FA information to the JSON file.

        Args:
            json (str): The directory where the JSON file is located. Required.
            name (str): The name of the account.
            issuer (str): The issuer of the 2FA.
            secret (str): The secret key for the 2FA.
            backup (str): The backup code for the 2FA.
            phrase (str): The recovery phrase for the 2FA.
            force (bool): A flag indicating whether to force adding duplicate data.

        Returns:
            int: 0 if the operation is successful, 1 otherwise.
        """
        json = json or config.get_json_directory()
        if json is None:
            print("Error: No JSON file specified. Pass --json [FILE]")
            return 1
        if not os.path.isfile(json):
            print("File does not exist")
            return 1
        if not json.endswith(".json"):
            print("File is not valid JSON")
            return 1

        contents = get_file_contents(json)
        data_list: List[dict] = JSON.loads(contents)
        for data in data_list:
            if ("name" in data and data["name"] == name and name is not None) or \
                    ("issuer" in data and data["issuer"] == issuer and issuer is not None) or \
                    ("secret" in data and data["secret"] == secret and secret is not None) or \
                    ("backup" in data and data["backup"] == backup and backup is not None) or \
                    ("phrase" in data and data["phrase"] == phrase and phrase is not None):
                    if not force:
                        print("Duplicate data. Pass -f to force.")
                        return 1
        obj = {"name": name}
        if issuer:
            obj["issuer"] = issuer
        if secret:
            obj["secret"] = secret
        if backup:
            obj["backup"] = backup
        if phrase:
            obj["phrase"] = phrase
        data_list.append(obj)
        data_list.sort(key=lambda x: x["name"].lower())

        write_file(json, JSON.dumps(data_list))

        return 0

    def remove(self, json: str, name: str, issuer: str, secret: str, backup: str, phrase: str, force: bool) -> int:
        """
        Removes 2FA information from the JSON file.

        Args:
            json (str): The directory where the JSON file is located. Required.
            name (str): The name of the account.
            issuer (str): The issuer of the 2FA.
            secret (str): The secret key for the 2FA.
            backup (str): The backup code for the 2FA.
            phrase (str): The recovery phrase for the 2FA.
            force (bool): A flag indicating whether to force removing multiple data.

        Returns:
            int: 0 if the operation is successful, 1 otherwise.
        """
        json = json or config.get_json_directory() or None
        if not os.path.isfile(json) or not json.endswith(".json"):
            return 1

        contents = get_file_contents(json)
        data_list = JSON.loads(contents)

        new_data_list = [data for data in data_list if not (data.get("name") == name) or not (data.get("issuer") == issuer) or not (data.get("secret") == secret) or not (data.get("backup") == backup) or not (data.get("phrase") == phrase)]
        
        if len(data_list) - len(new_data_list) > 1:
            print("Too many objects removed. Pass -f to force.")
            return 1

        write_file(json, JSON.dumps(data_list))
        return 0
    
    def set_file_directory(self, text: str, json: str) -> None:
        """
        Sets the directory where the JSON or TXT file is located.

        Args:
            One of the following is required:
                json (str): The directory where the JSON file is located.
                text (str): The directory where the TXT file is located.
        """
        if text:
            if not os.path.isfile(text):
                print("File/Directory does not exist")
                return 1
            config.set_txt_directory(text)
        if json:
            if not os.path.isfile(json):
                print("File/Directory does not exist")
                return 1
            config.set_json_directory(json)
        if not text and not json:
            print("Must specify either text or json.")
            return 1
        return 0
            
    def update_text(self, json: str, text: str, name: str, issuer: str, secret: str, backup: str, phrase: str) -> int:
        """
        Updates the TXT file with the latest 2FA information.

        Args:
            json (str): The directory where the JSON file is located. Required.
            text (str): The directory where the TXT file is located. Required.
            name (str): The name of the account.
            issuer (str): The issuer of the 2FA.
            secret (str): The secret key for the 2FA.
            backup (str): The backup code for the 2FA.
            phrase (str): The recovery phrase for the 2FA.

        Returns:
            int: 0 if the operation is successful, 1 otherwise.
        """
        json = json or config.get_json_directory() or None
        text = text or config.get_txt_directory() or None
        if json is None or text is None:
            print("No JSON/TXT file specified. Pass --json [FILE] --txt [FILE]")
            return 1
        if not os.path.isfile(json):
            print("File does not exist")
            return 1
        if not json.endswith(".json"):
            print("File is not valid JSON")
            return 1

        contents = get_file_contents(json)
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

        data_list: List[dict] = JSON.loads(contents)
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
        write_file(text, TXT)
        return 0
    
    def get_qr(self, json: str, name: str, issuer: str, secret: str, backup: str, phrase: str):
        """
        Gets the QR code for the 2FA.

        Args:
            json (str): The directory where the JSON file is located. Required.
            name (str): The name of the account.
            issuer (str): The issuer of the 2FA.
            secret (str): The secret key for the 2FA.
            backup (str): The backup code for the 2FA.
            phrase (str): The recovery phrase for the 2FA.

        Returns:
            str: The QR code.
        """
        json = json or config.get_json_directory() or None
        if json is None:
            print("No JSON file specified. Pass --json [FILE]")
            return 1
        
        
