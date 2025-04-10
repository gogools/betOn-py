import json
import os
import time

from util import msg


def delete_files_in_folder(folder_path: str):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                delete_files_in_folder(file_path)
        except Exception as e:
            print(f"Error deleting file: {file_path}, {e}")


def verify_if_file_exists(file_name: str) -> bool:
    try:
        with open(f"{format_file_name(file_name)}", "r") as f:
            content = f.read().strip()
            if content == "" or content == "{}":
                return False
            return True
    except FileNotFoundError:
        return False


def format_file_name(file_name: str, is_upper: bool = False) -> str:
    fn = file_name.replace(" ", "_").lower()
    return fn.upper() if is_upper else fn


def save_dict_2_file(data: dict, file_name: str):
    with open(f"{file_name}", "w") as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))
        msg(f"Data saved to {file_name}")


def delete_24h_old_files(directory):
    msg(f"Trying to delete old files in {directory}")
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < time.time() - 24 * 60 * 60:
                os.remove(file_path)
                print(f"Deleted {file_path}")