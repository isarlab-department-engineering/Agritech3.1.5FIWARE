from pathlib import Path
import pandas as pd
import numpy as np


###########main:
ROOT_DIR = Path(__file__).resolve().parents[1]
LOG_CONFIG = Path(ROOT_DIR, "logger_conf.json")

dataset_path = "/home/croc/Documenti/Repositories/Agritech3.1.5FIWARE/data/Dataset_1/finalSAP.xlsx"
data = pd.read_excel(dataset_path)

