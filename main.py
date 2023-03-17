from two_factor_auth_tool import TwoFactorAuthTool
import argparse
import sys
import os
import json

def main():
    """
    The main function that handles command-line arguments and calls the appropriate methods.
    """
    parser = argparse.ArgumentParser(description="Command-line tool for handling 2FA information in JSON format.")
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # Add parser
    parser_add = subparsers.add_parser("add", help="Add a 2FA object to a JSON file.")
    parser_add.add_argument("--json", help="Specify the JSON file.")
    parser_add.add_argument("--name", help="Specify the name of the account.")
    parser_add.add_argument("--issuer",  help="Specify the issuer of the 2FA.")
    parser_add.add_argument("--secret", help="Specify the secret key for 2FA.")
    parser_add.add_argument("--backup", help="Specify the backup codes for 2FA.")
    parser_add.add_argument("--phrase", help="Specify the phrase for 2FA (Like crypto wallet phrases).")
    parser_add.add_argument("-f", "--force", action="store_true", help="Force the adding of duplicate data.")

    # Remove parser
    parser_remove = subparsers.add_parser("remove", help="Remove a 2FA object from the JSON file.")
    parser_remove.add_argument("--json", help="Specify the JSON file.")
    parser_remove.add_argument("--name", help="Specify the name of the account.")
    parser_remove.add_argument("--issuer", help="Specify the issuer of the 2FA.")
    parser_remove.add_argument("--secret", help="Specify the secret key for 2FA.")
    parser_remove.add_argument("--backup", help="Specify the backup codes for 2FA.")
    parser_remove.add_argument("--phrase", help="Specify the phrase for 2FA (Like crypto wallet phrases).")
    parser_remove.add_argument("-f", "--force", action="store_true", help="Force deletion of all objects that match.")

    # Update parser
    parser_update = subparsers.add_parser("update", help="Update the 2FA text file with the information from the JSON file. Requires both a JSON file and TXT file.")
    parser_update.add_argument("--text", help="Specify the 2FA text file.")
    parser_update.add_argument("--json", help="Specify the JSON file.")
    parser_update.add_argument("--name", help="Specify the name of the account.")
    parser_update.add_argument("--issuer", help="Specify the issuer of the 2FA.")
    parser_update.add_argument("--secret", help="Specify the secret key for 2FA.")
    parser_update.add_argument("--backup", help="Specify the backup codes for 2FA.")
    parser_update.add_argument("--phrase", help="Specify the phrase for 2FA (Like crypto wallet phrases).")

    # Get QR parser
    parser_get_qr = subparsers.add_parser("get-qr", help="Get the QR code for a 2FA object from the JSON file.")
    parser_get_qr.add_argument("--json", help="Specify the JSON file.")
    parser_get_qr.add_argument("--name", help="Get QR based on the name of the account.")
    parser_get_qr.add_argument("--issuer", help="Get QR based on the issuer of the 2FA.")
    parser_get_qr.add_argument("--secret", help="Get QR based on the secret key for 2FA.")
    parser_get_qr.add_argument("--backup", help="Get QR based on the backup codes for 2FA.")
    parser_get_qr.add_argument("--phrase", help="Get QR based on the phrase for 2FA (Like crypto wallet phrases).")

    # Set parser
    parser_set = subparsers.add_parser("set", help="Set the default location of the TXT and/or JSON files.")
    parser_set.add_argument("--json", help="Set the JSON file.")
    parser_set.add_argument("--text", help="Set the 2FA text file.")

    # Unset parser
    parser_unset = subparsers.add_parser("unset", help="Unset the default location of the TXT and/or JSON files.")
    parser_unset.add_argument("--json", action="store_true", help="Flag to unset the JSON file location.")
    parser_unset.add_argument("--text", action="store_true", help="Flag to unset the text file location.")

    # List parser
    parser_list = subparsers.add_parser("list", help="List all 2FA objects in the JSON file.")
    parser_list.add_argument("--json", help="Specify the JSON file.")
    parser_list.add_argument("--name", action="store_true", help="Flag to just receive the names of the account.")
    parser_list.add_argument("--issuer", action="store_true", help="Flag to just receive the issuers of the 2FA.")
    parser_list.add_argument("--secret", action="store_true", help="Flag to just receive the secrets key for 2FA.")
    parser_list.add_argument("--backup", action="store_true", help="Flag to just receive the backups codes for 2FA.")
    parser_list.add_argument("--phrase", action="store_true", help="Flag to just receive the phrases for 2FA (Like crypto wallet phrases).")

    # List alias
    parser_ls = subparsers.add_parser("ls", help="List all 2FA objects in the JSON file.")
    parser_ls.add_argument("--json", help="Specify the JSON file.")
    parser_ls.add_argument("--name", action="store_true", help="Flag to just receive the names of the account.")
    parser_ls.add_argument("--issuer", action="store_true", help="Flag to just receive the issuers of the 2FA.")
    parser_ls.add_argument("--secret", action="store_true", help="Flag to just receive the secrets key for 2FA.")
    parser_ls.add_argument("--backup", action="store_true", help="Flag to just receive the backups codes for 2FA.")
    parser_ls.add_argument("--phrase", action="store_true", help="Flag to just receive the phrases for 2FA (Like crypto wallet phrases).")

    # Code parser
    parser_code = subparsers.add_parser("code", help="Generate a 2FA code.")
    parser_code.add_argument("--json", help="Specify the JSON file.")
    parser_code.add_argument("--name", help="Specify the name of the account.")
    parser_code.add_argument("--secret", help="Specify the secret key for 2FA.")
    
    # Parse arguments

    args = parser.parse_args()

    tool = TwoFactorAuthTool()

    if args.command == "add":
        try:
            return_code = tool.add(json=args.json, name=args.name, issuer=args.issuer, secret=args.secret, backup=args.backup, phrase=args.phrase, force=args.force)
            if return_code == 0:
                print("Successfully added.")
            else:
                print("Failed to add.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "remove":
        try:
            return_code = tool.remove(json=args.json, name=args.name, issuer=args.issuer, secret=args.secret, backup=args.backup, phrase=args.phrase, force=args.force)
            if return_code == 0:
                print("Successfully removed.")
            else:
                print("Failed to remove.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "update":
        try:
            return_code = tool.update_text(json=args.json, text=args.text)
            if return_code == 0:
                print("Successfully updated 2FA text file.")
            else:
                print("Failed to update 2FA text file.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "get-qr":
        try:
            return_code = tool.get_qr(json=args.json, name=args.name, issuer=args.issuer, secret=args.secret, backup=args.backup, phrase=args.phrase)
            if not return_code == 0:
                print("Failed to retrieve QR code.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "set":
        try:
            return_code = tool.set_file_directory(json=args.json, text=args.text)
            if return_code == 0:
                print("Successfully set file location.")
            else:
                print("Failed to set file location.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "unset":
        try:
            return_code = tool.unset_file_directory(json=args.json, text=args.text)
            if return_code == 0:
                print("Successfully set file location.")
            else:
                print("Failed to set file location.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "list" or args.command == "ls":
        try:
            return_code = tool.list_objects(json=args.json, name=args.name, issuer=args.issuer, secret=args.secret, backup=args.backup, phrase=args.phrase)
            if not return_code == 0:
                print("Failed to list 2FA objects.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "code":
        try:
            return_code = tool.code(json=args.json, name=args.name, secret=args.secret)
            if not return_code == 0:
                print("Failed to generate 2FA code.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
