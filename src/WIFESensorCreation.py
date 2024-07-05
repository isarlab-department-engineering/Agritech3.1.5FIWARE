"""
Code for generating the WIFE sensor instances.
It generates the YAML code for creating WIFE sensor instances
from the config files in config/devices/instances.
"""
from config import ROOT_DIR, CONFIG_DIR
from tools import FolderCreator, setup_logging, get_yaml_config, check_file, check_folder, save_dict_to_json
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
model_template_dict = model_template_dict["CREATION"]

# Process all the sensor instances
logger.info("processing started")
for _, _, files in os.walk(SENS_DIR, topdown=True):
    for file in files:
        # Load yaml for each device instances
        sensor_yaml = Path(SENS_DIR, file).__str__()
        logger.info("processing sensor instance: {}".format(file))

        # Load the  dictionary of the instance
        sensor_instance = get_yaml_config(sensor_yaml)
        sensor_model_yaml = Path(SENS_MODEL_DIR, sensor_instance["config_file"])
        sensor_model = get_yaml_config(sensor_model_yaml)

        # We update the sensor instance dictionary with the model
        sensor_instance.update(sensor_model)

        # Create a new dictionary based on the template we already created
        sensor_creation_dict = model_template_dict

        # Update the value on the template
        for key in sensor_instance:
            if key in sensor_creation_dict:
                sensor_creation_dict[key] = sensor_instance[key]

        # Create the sensor yaml
        logger.info("Creating the yaml configuration for {} ...".format(file))
        save_dict_to_json(data=sensor_creation_dict, json_filename=file, savedir=OUT_SESS_DIR.get_path())

# Done, Ciao, Addio
logger.info("Done ...")

# TODO: ADD
#        - CHECKING FOR CREATION DATE AND DATETIME FORMAT -> TIMESTAMPS UNIX
