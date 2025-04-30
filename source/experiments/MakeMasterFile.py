import glob
import os

import pandas as pd
from pandas import DataFrame

path_for_masterfile: str = "results/po/general/"
result_csv_files = os.listdir(path_for_masterfile)

all_data: DataFrame = pd.concat([pd.read_csv(path_for_masterfile + file_name) for file_name in result_csv_files], ignore_index=True)
all_data.to_csv(path_for_masterfile + "Masterfile_General")