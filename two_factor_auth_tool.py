import json as JSON
import os
from config import config
from fileutils import get_file_contents, write_file, create_qr_code, test_json, get_data_list, test_txt, gen_code
    
class TwoFactorAuthTool:
    """
    A class that represents a 2FA tool for adding and updating 2FA information.
    """

    def add(self, json: str, name: str, issuer: str, secret: str, backup: str, phrase: str, force: bool) -> int:
        """
        Adds new 2FA information to the JSON file.

        Args:
            json (str): The directory where the JSON file is located.
            name (str): The name of the account.
            issuer (str): The issuer of the 2FA.
            secret (str): The secret key for the 2FA.
            backup (str): The backup code for the 2FA.
            phrase (str): The recovery phrase for the 2FA.
            force (bool): A flag indicating whether to force adding duplicate data.

        Returns:
            int: 0 if the operation is successful, 1 otherwise.
        """
        data_list = get_data_list(json, config)
        if data_list == 1:
            print("Error. Something went wrong.")
            return 1
        duplicates = [data for data in data_list if 
            (data["name"] == name and name is not None) or 
            (data["issuer"] == issuer and issuer is not None) or 
            (data["secret"] == secret and secret is not None) or 
            (data["backup"] == backup and backup is not None) or 
            (data["phrase"] == phrase and phrase is not None)]
        if len(duplicates) > 0 and not force:
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

        write_file(json, JSON.dumps(data_list), config)

        return 0

    def remove(self, json: str, name: str, issuer: str, secret: str, backup: str, phrase: str, force: bool) -> int:
        """
        Removes 2FA information from the JSON file.

        Args:
            json (str): The directory where the JSON file is located.
            name (str): The name of the account.
            issuer (str): The issuer of the 2FA.
            secret (str): The secret key for the 2FA.
            backup (str): The backup code for the 2FA.
            phrase (str): The recovery phrase for the 2FA.
            force (bool): A flag indicating whether to force removing multiple data.

        Returns:
            int: 0 if the operation is successful, 1 otherwise.
        """
        data_list = get_data_list(json, config)
        new_data_list = [data for data in data_list 
            if (not data.get("name") == name and name is not None) or 
            (not data.get("issuer") == issuer and issuer is not None) or 
            (not data.get("secret") == secret and secret is not None) or 
            (not data.get("backup") == backup and backup is not None) or 
            (not data.get("phrase") == phrase and phrase is not None)]
        
        if len(data_list) - len(new_data_list) > 1 and not force:
            print("Too many objects removed. Pass -f to force.")
            return 1

        write_file(json, JSON.dumps(new_data_list), config)
        return 0
    
    def set_file_directory(self, text: str, json: str) -> int:
        """
        Sets the default directory where the JSON or TXT file is located.

        Args:
            One of the following is required:
                json (str): The directory where the JSON file is located.
                text (str): The directory where the TXT file is located.
        """
        if not text and not json:
            print("Must specify either text or json.")
            return 1
        if text:
            text = test_txt(text, config)
            if not text:
                print("File/Directory does not exist, or is not valid.")
                return 1
            config.set_txt_directory(text)
        if json:
            json = test_json(json, config)
            if not json:
                print("File/Directory does not exist, or is not valid.")
                return 1
            config.set_json_directory(json)
        return 0

    def unset_file_directory(self, json: bool, text: bool) -> int:
        """
        Unsets the default directory where the JSON and/or TXT file is located.

        Args:
            One of the following is required:
                json (bool): Flag to unset the JSON directory.
                text (bool): Flag to unset the TXT directory.
        """
        if not json and not text:
            print("Must specify either json or text.")
            return 1
        if json:
            config.set_json_directory(None)
        if text:
            config.set_txt_directory(None)
        return 0

    def list_objects(self, json: str, name: str, issuer: str, secret: str, backup: str, phrase: str) -> int:
        """
        Lists all 2FA information in the JSON file.

        Args:
            json (str): The directory where the JSON file is located.
            name (str): The name of the account.
            issuer (str): The issuer of the 2FA.
            secret (str): The secret key for the 2FA.
            backup (str): The backup code for the 2FA.
            phrase (str): The recovery phrase for the 2FA.

        Returns:
            int: 0 if the operation is successful, 1 otherwise.
        """
        json = test_json(json, config)
        if not json:
            print("JSON file does not exist, or is not valid.")
            return 1
        
        data_list = get_data_list(json, config)
        if data_list == 1:
            print("Error. Something went wrong.")
            return 1

        all = False
        if not name and not issuer and not secret and not backup and not phrase:
            all = True
        
        for data in data_list:
            print(f"Name: {data['name']}")
            if issuer or all:
                print(f"Issuer: {data['issuer']}")
            if secret or all:
                print(f"Secret: {data['secret']}")
            if backup or all:
                print(f"Backup: {data['backup']}")
            if phrase or all:
                print(f"Phrase: {data['phrase']}")
            print()

        return 0
        
    def update_text(self, json: str, text: str) -> int:
        """
        Updates the TXT file with the latest 2FA information.

        Args:
            json (str): The directory where the JSON file is located. Required.
            text (str): The directory where the TXT file is located. Required.

        Returns:
            int: 0 if the operation is successful, 1 otherwise.
        """
        if json is None or text is None:
            print("No JSON/TXT file specified. Pass --json [FILE] --txt [FILE]")
            return 1
        json = test_json(json, config)
        if not json:
            print("JSON file does not exist, or is not valid.")
            return 1
        text = test_txt(text, config)
        if not text:
            print("TXT file does not exist, or is not valid.")
            return 1

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

        data_list = get_data_list(json, config)
        for data in data_list:
            name, issuer, secret, backup, phrase = data.get("name"), data.get("issuer"), data.get("secret"), data.get("backup"), data.get("phrase")

            link = f"otpauth://totp/{name}?secret={secret}&issuer={issuer}".replace(" ", "%20")
            qr = create_qr_code(link)
            all_info += f"{f'Name:       {name}{nl}' if name else ''}{f'Secret:     {secret}{nl}' if secret else ''}{f'Link:       {link}{nl}' if link else ''}{f'Backup:     {backup}{nl}' if backup else ''}{f'Phrase:     {phrase}{nl}' if phrase else ''}\n\n\n"
            secrets += f"{name}\n{secret}\n\n\n" if secret else ""
            links += f"{link}\n" if link else ""
            backups += f"{name}\n\n{backup}\n\n\n" if backup else ""
            qrs += f"{name}\n\n{qr}\n\n\n" if qr else ""
            phrases += f"{name}\n\n{phrase}\n\n\n" if phrase else ""
            names += f"{name}\n" if name else ""

        TXT = f"\n{title('All')}\n\n{all_info}\n{div}{title('Secrets')}\n{secrets}\n{div}{title('Links')}\n{links}\n{div}{title('Backups')}\n{backups}\n{div}{title('Phrases')}\n{phrases}\n{div}{title('Names')}\n{names}\n{title('QR Codes')}\n{qrs}"
        write_file(text, TXT, config)
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
        json = test_json(json, config)
        if not json:
            print("JSON file does not exist, or is not valid.")
            return 1
        
        contents = get_file_contents(json)
        data_list = JSON.loads(contents)
        specified = [data for data in data_list if 
            (data["name"] == name and name is not None) or 
            (data["issuer"] == issuer and issuer is not None) or 
            (data["secret"] == secret and secret is not None) or 
            (data["backup"] == backup and backup is not None) or 
            (data["phrase"] == phrase and phrase is not None)]
        for data in specified:
            if not data.get("name") or not data.get("issuer") or not data.get("secret"):
                print("All 2FA information must be in the JSON file.")
                return 1
            link = f"otpauth://totp/{data['name']}?secret={data['secret']}&issuer={data['issuer']}".replace(" ", "%20")
            qr = create_qr_code(link)
            print(f'{data["name"]}\n\n{qr}\n\n')
            
        return 0
    
    def code(self, json: str, name: str, secret: str):
        """
        Generates a code for the 2FA.

        Args:
            json (str): The directory where the JSON file is located. Required.
            name (str): The name of the account you want to generate.
            secret (str): The secret key for the 2FA.

        Returns:
            str: The code.
        """
        if secret is not None:
            code = gen_code(secret)
            print(f'{name} Code: {code}')
            return 0

        json = test_json(json, config)
        if not json:
            print("JSON file does not exist, or is not valid.")
            return 1
        
        contents = get_file_contents(json)
        data_list = JSON.loads(contents)
        specified = [data for data in data_list if 
            (data["name"] == name and name is not None) or 
            (data["secret"] == secret and secret is not None)]
        if len(specified) == 0:
            print("Could not find 2FA information in the JSON file based on the name.")
            return 1
            
        for data in specified:
            code = gen_code(data["secret"])
            print(f'{data["name"]} Code: {code}')

        return 0