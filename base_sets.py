import os

USERS = os.getenv("USERS", "default_user")
OnePath = os.getenv("OnePath", "default_path")
BASE_PATH = f"C:\\Users\\{USERS}\\{OnePath}"

# ms2
MS2_PATH_COMBINATE = os.path.join(BASE_PATH, "ms2\\triplets\\lists\\combinate")
MS2_PATH_TMP = os.path.join(BASE_PATH, "ms2\\triplets\\tmp")