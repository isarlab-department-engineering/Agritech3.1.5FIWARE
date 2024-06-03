import os
import sys
import yaml
from pathlib import Path
import json
import logging


class LoggerParser:
    @staticmethod
    def setup_logging(save_dir, log_config,  default_level=logging.INFO):
        """
        Setup logger
        """
        log_config = Path(log_config)
        save_dir = Path(save_dir)
        try:
            conf = json.load(open(log_config))
            # modify logger paths based on run configs
            for _, handler in conf['LOGGING']['handlers'].items():
                if 'filename' in handler:
                    handler['filename'] = str(os.path.join(save_dir, handler['filename']))
            logging.config.dictConfig(conf['LOGGING'])
        except FileNotFoundError as e:
            print("Unable to open the .json file {}, the returned error is: \n\t->{}".format(log_config, e))
            logging.basicConfig(level=default_level)
        except Exception as e:
            print("An error occur while setting up the logging: \n\t->{}".format(e))
            logging.basicConfig(level=default_level)


class YamlParser:
    @staticmethod
    def get_config(yaml_path):
        with open(yaml_path, "r") as stream:
            try:
                config_loaded = yaml.safe_load(stream)
            except yaml.YAMLError:
                msg = "Error while loading the yaml file : {}".format(yaml_path)
                logging.error(msg)
                sys.exit(1)
        return config_loaded

class FolderCreator:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        try:
            os.mkdir(self.path)
        except Exception as e:
            msg = ''.join(["Error while creating the folder for containing images: ", str(self.path), "\n", str(e)])
            print(msg)
            sys.exit(1)
