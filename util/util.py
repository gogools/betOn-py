
import html
import os
from datetime import datetime


def val(value, html_scape: bool = False):
    try:
        val = float(value)
        if val.is_integer():
            return int(val)
        return val
    except ValueError:
        return html.unescape(value) if html_scape and isinstance(value, str) else value

def today_date(_format: str = "%Y-%m-%d") -> str:
    return datetime.now().strftime(_format)


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


def format_file_name(file_name: str, is_upper: bool = False) -> str:
    fn =  file_name.replace(" ", "_").lower()
    return fn.upper() if is_upper else fn