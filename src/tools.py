import os
import sys
import json

import pandas.errors
import pandas as pd
import yaml
from datetime import datetime
from pathlib import Path
import logging
import argparse


# Parse the arguments and extract the indexes
def update_parser():
    parser = argparse.ArgumentParser(description='Parser for updatind sensor. Note the mapper.yaml file is needed')
    parser.add_argument('--dataset', type=str, required=True,
                        help='xlsx Dataset and mapper.yaml folder path')

    return parser


def setup_logging(log_out_path: Path):
    # Create Folder session out
    now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    out_file = os.path.join(str(log_out_path), "".join(["log_", now, "_.log"]))

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(out_file)
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%d-%b-%y %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info("Session started")
    return logger


def get_yaml_config(yaml_path):
    with open(yaml_path, "r") as stream:
        try:
            config_loaded = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            msg = "Error while loading the yaml file : {}".format(e)
            logging.error(msg)
            sys.exit(1)
    return config_loaded


def get_json_config(json_path):
    """Loads configuration data from a JSON file.

    Args:
        json_path: The path to the JSON configuration file.

    Returns:
        A dictionary containing the configuration data.

    Raises:
        SystemExit: If an error occurs during JSON parsing.
    """
    with open(json_path, "r") as f:
        try:
            config_loaded = json.load(f)
        except json.JSONDecodeError as e:
            msg = "Error while loading the JSON file: {} \n->{} ".format(json_path, e)
            logging.error(msg)
            sys.exit(1)
    return config_loaded


def load_dataset_to_df(path_dataset) -> pd.DataFrame:
    """Loads the data files from Excel file (xlsx).

    Args:
        path_dataset: The path to the xlsx dataset file.

    Returns:
        A DataFrame containing the  data.

    Raises:
        SystemExit: If an error occurs loading dataset.
    """

    try:
        dataframe = pd.read_excel(path_dataset, index_col=0)
    except FileNotFoundError:
        msg = "File {} not found while loading the dataset".format(path_dataset)
        logging.error(msg)
        sys.exit(1)
    except pandas.errors.DataError as e:
        msg = "Error while loading the data from file file: {} \n->{} ".format(path_dataset, e)
        logging.error(msg)
        sys.exit(1)
    return dataframe


def datetime_to_iso8601(datetime_str):
    """Converts a datetime string in the format 'YYYY-MM-DD HH:MM:SS' to ISO 8601.

    Args:
        datetime_str: The datetime string to convert.

    Returns:
        The datetime string in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
    """
    try:
        dt_object = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return dt_object.isoformat() + "Z"  # Add 'Z' for UTC timezone
    except ValueError:
        msg = "Error while converting {} to ISO 8601 ".format(datetime_str)
        logging.error(msg)
        sys.exit(1)

def save_dict_to_json(data, json_filename, savedir):
    check_folder(savedir)
    outfilename = Path(savedir, json_filename).__str__()
    with open(outfilename, "w") as json_file:
        # Dump the YAML data to the file
        json.dump(data, json_file, indent=1, sort_keys=False, separators=(',', ':'))

class FolderCreator:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        try:
            os.mkdir(self.path)
        except Exception as e:
            msg = ''.join(["Error while creating the folder for containing images: ", str(self.path), "\n", str(e)])
            logging.error(msg)
            sys.exit(1)

    def get_path(self):
        return self.path


def check_file(file_path_str):
    if not os.path.isfile(file_path_str):
        message = "File {} NOT found".format(file_path_str)
        logging.debug(message)
        return False
    else:
        return True


def check_folder(folder_path):
    if not Path(folder_path).exists():
        message = "Folder {} NOT found".format(folder_path)
        logging.debug(message)
        return False
    else:
        return True
