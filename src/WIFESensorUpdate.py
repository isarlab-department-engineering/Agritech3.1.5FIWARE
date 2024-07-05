"""
Code for update the WIFE sensor measurements.
It generates the YAML code for creating WIFE sensor update yaml file.
The data are updated according to the values on the dataset and the mapper file.
from the config files in config/devices/instances.
"""
import copy

from config import ROOT_DIR, CONFIG_DIR
from tools import *
from pathlib import Path
from datetime import datetime
import os
import argparse
from alive_progress import alive_bar

#####################################################
# SETTINGS LOADING                                  #
#####################################################
# Get Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--mapper", required=True, help="Path of mapper.yaml file, that must within a folder "
                                                    "containing the .xlsx file. example \n --mapper "
                                                    "/home/.../mapper.yaml ")
args = parser.parse_args()
mapper_path = Path(args.mapper)

# Get main config
check_file(Path(CONFIG_DIR, "config.yaml"))
config_session = get_yaml_config(Path(CONFIG_DIR, "config.yaml").__str__())

# Get folders
OUTPUT_DIR = Path(ROOT_DIR, *config_session["PATH"]["out"])
SENS_DIR = Path(ROOT_DIR, *config_session["PATH"]["instances"])
SENS_MODEL_DIR = Path(ROOT_DIR, *config_session["PATH"]["model"])

# Create out folder and logging
study_name = "".join(["WIFE_UPDATE", "_", datetime.now().strftime("%d_%m_%Y_%H_%M_%S")])
OUT_SESS_DIR = FolderCreator(Path(OUTPUT_DIR, study_name))
logger = setup_logging(OUT_SESS_DIR.get_path())

# Get the sensor instances path and save the files
logger.info("checking instances on: {}".format(SENS_DIR))
check_folder(SENS_DIR)
logger.info("checking instances on: {}".format(SENS_MODEL_DIR))
check_folder(SENS_MODEL_DIR)

# Get the sensor model templates
yaml_path_model_templates = Path(SENS_MODEL_DIR, "sensor_WIFE.json")
check_file(yaml_path_model_templates)
model_template_dict = get_yaml_config(yaml_path_model_templates.__str__())

# Set the creation template
model_template_dict = model_template_dict["UPDATE"]

# Read the mapper.yaml config file
mapper_dict = get_yaml_config(mapper_path.__str__())
file_dataset = Path(mapper_path.parent, mapper_dict["DATASET"]["name"])
check_file(file_dataset)
logging.info("dataset selected: {}".format(file_dataset))

# load dataframe
dataset_df = load_dataset_to_df(file_dataset)
logging.info("dataframe loaded")

# Process all the sensor instances
logger.info("processing started")



#####################################################
# REPROCESSING                                      #
#####################################################

# We get the sensor list mapped: getting the ID
id_sensor_mapping = []
[id_sensor_mapping.append(id_sens) for id_sens in mapper_dict["DEVICES"].keys()]
sensor_list_matched = []
folder_list_updated = []

# We get the sensor list instanced and find the matched  one
for _, _, files in os.walk(SENS_DIR, topdown=True):
    for file in files:
        sensor_json = Path(SENS_DIR, file).__str__()
        sensor_instance = get_json_config(sensor_json)
        sensor_instance_id=sensor_instance["id"]
        if sensor_instance_id in id_sensor_mapping:

            folder = FolderCreator(Path(OUT_SESS_DIR.get_path(), sensor_instance_id.split(":")[-1]).__str__())
            folder_list_updated.append(folder)
            sensor_model_json = Path(SENS_MODEL_DIR, sensor_instance["config_file"])
            sensor_model = get_json_config(sensor_model_json)

            # We update the sensor instance dictionary with the model
            sensor_instance.update(sensor_model)

            # Create a new dictionary based on the template we already created
            sensor_update_instance = copy.deepcopy(model_template_dict)

            # Update the value on the template
            for key in sensor_instance:
                if key in sensor_update_instance:
                    sensor_update_instance[key] = sensor_instance[key]

            # Add the sensor to the list of sensors
            sensor_list_matched.append(sensor_update_instance)


#####################################################
# PROCESSING DATASET                                #
#####################################################

# We get the sensor list instanced and find the matched one
with alive_bar(total=len(dataset_df), title="Processing Rows") as bar:
    for index_rox, row in dataset_df.iterrows():
        for index_sens, sens in enumerate(sensor_list_matched):
            sens_inst = copy.deepcopy(sens)
            sens_inst_id = sens_inst["id"]
            # Update Controlled Property
            features_mapped = mapper_dict["DEVICES"][sens_inst_id]["controlledProperty"]
            sens_inst["value"] = row[features_mapped].to_list()

            # Update Time
            time_row_label = mapper_dict["DATASET"]["date_time_col"]
            time_df = str(row[time_row_label])
            time_iso8601 = datetime_to_iso8601(time_df)
            sens_inst["dateObserved"] = time_iso8601

            # write the instance to the corresponding folder
            folder = folder_list_updated[index_sens]
            save_dict_to_json(data=sens_inst, json_filename="".join(["data_", f"{index_rox:04}", ".json"]),
                          savedir=folder.get_path())

        bar()




