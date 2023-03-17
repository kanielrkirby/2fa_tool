import os
import json

class Config:
    """
    Configuration class for all the config related methods.
    """
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
        self.config = {}
        self.load_config()

    def load_config(self):
        """
        Loads the config file.
        """
        with open(self.config_file, "r") as f:
            self.config = json.load(f)

    def save_config(self):
        """
        Saves the config file.
        """
        with open(self.config_file, "w") as f:
            json.dump(self.config, f)

    def get_json_directory(self):
        """
        Returns the directory where the JSON files are stored.
        """
        if self.config.get("json_directory"):
            return self.config["json_directory"]
        else:
            return None

    def get_txt_directory(self):
        """
        Returns the directory where the TXT files are stored.
        """
        if self.config.get("txt_directory"):
            return self.config["txt_directory"]
        else:
            return None

    def set_json_directory(self, directory: str):
        """
        Sets the directory where the JSON files are stored.
        """
        self.config["json_directory"] = directory
        self.save_config()

    def set_txt_directory(self, directory: str):
        """
        Sets the directory where the TXT files are stored.
        """
        self.config["txt_directory"] = directory
        self.save_config()

config = Config()