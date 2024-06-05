"""
Code for update the WIFE sensor measurements.
It generates the YAML code for creating WIFE sensor update yaml file.
The data are updated according to the values on the dataset and the mapper file.
from the config files in config/devices/instances.
"""
from config import ROOT_DIR, CONFIG_DIR
from tools import FolderCreator, setup_logging, get_yaml_config, check_file, check_folder, save_dict_to_yaml
from pathlib import Path
from datetime import datetime
import os



#####################################################
# SETTINGS LOADING                                  #
#####################################################
# Get main config
check_file(Path(CONFIG_DIR, "config.yaml"))
config_session = get_yaml_config(Path(CONFIG_DIR, "config.yaml").__str__())

# Get folders
OUTPUT_DIR = Path(ROOT_DIR, *config_session["PATH"]["out"])
SENS_DIR = Path(ROOT_DIR, *config_session["PATH"]["instances"])
SENS_MODEL_DIR = Path(ROOT_DIR, *config_session["PATH"]["model"])

# Create out folder and logging
study_name = "".join(["WIFE_CREATION", "_", datetime.now().strftime("%d_%m_%Y_%H_%M_%S")])
OUT_SESS_DIR = FolderCreator(Path(OUTPUT_DIR, study_name))
logger = setup_logging(OUT_SESS_DIR.get_path())

# Get the sensor instances path and save the files
logger.info("checking instances on: {}".format(SENS_DIR))
check_folder(SENS_DIR)
logger.info("checking instances on: {}".format(SENS_MODEL_DIR))
check_folder(SENS_MODEL_DIR)

# Get the sensor model templates
yaml_path_model_templates = Path(SENS_MODEL_DIR, "sensor_WIFE.yaml")
check_file(yaml_path_model_templates)
model_template_dict = get_yaml_config(yaml_path_model_templates.__str__())

# Set the creation template
model_template_dict = model_template_dict["UPDATE"]

