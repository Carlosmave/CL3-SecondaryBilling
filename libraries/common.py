import shutil
import time

from robot.api import logger
import os
import sys
from datetime import datetime
from RPA.Robocloud.Items import Items
from RPA.Robocloud.Secrets import Secrets


def log_message(message: str, level: str = "INFO", console: bool = True):
    log_switcher = {"TRACE": logger.trace, "INFO": logger.info, "WARN": logger.warn, "ERROR": logger.error}
    if not level.upper() in log_switcher.keys() or level.upper() == "INFO":
        logger.info(message, True, console)
    else:
        if level.upper() == "ERROR":
            logger.info(message, True, console)
        else:
            log_switcher.get(level.upper(), logger.error)(message, True)


def get_downloaded_file_path(path_to_temp: str, extension: str, error_message: str = "") -> str:
    downloaded_files = []
    timer = datetime.datetime.now() + datetime.timedelta(0, 60 * 1)

    while timer > datetime.datetime.now():
        time.sleep(1)
        downloaded_files = [f for f in os.listdir(path_to_temp) if os.path.isfile(os.path.join(path_to_temp, f))]
        if len(downloaded_files) > 0 and downloaded_files[0].endswith(extension):
            time.sleep(1)
            break
    if len(downloaded_files) == 0:
        if error_message:
            raise Exception(error_message)
        return ""
    file_path = os.path.join(path_to_temp, downloaded_files[0])
    return file_path


def print_version():
    try:
        file = open("VERSION")
        try:
            print("Version {}".format(file.read().strip()))
        except Exception as ex:
            print("Error reading VERSION file. {}".format(str(ex)))
        finally:
            file.close()
    except Exception as e:
        log_message("VERSION file not found. {}".format(str(e)))


def create_or_clean_dir(folder_path: str):
    shutil.rmtree(folder_path, ignore_errors=True)
    try:
        os.mkdir(folder_path)
    except FileExistsError:
        pass


def get_input(input_date: datetime, input_text: str, executor_email: str):
    if len(sys.argv) > 1 and sys.argv[1].lower() == "local":
        input_date = datetime(2021, 11, 3)
        input_text = "Test text"
        executor_email = "test@thoughtfulautomation.com"
        log_message("LOCAL RUN")
    else:
        library = Items()
        library.load_work_item_from_environment()

        executor_email: str = library.get_work_item_variable("userEmail")
        # How get text input
        input_text: str = library.get_work_item_variable("text_input_id")
        # How get date input
        input_date_str: str = library.get_work_item_variable("date_input_id")
        input_date = datetime.strptime(input_date_str, "%m/%d/%Y")
    return input_date, input_text, executor_email


def get_bitwarden_credentials(credentials_name: str = "bitwarden_credentials") -> dict:
    if len(sys.argv) > 1 and sys.argv[1].lower() == "local":
        bitwarden_credentials = {
            "username": os.getenv("BITWARDEN_USERNAME"),
            "password": os.getenv("BITWARDEN_PASSWORD"),
            "client_id": os.getenv("BITWARDEN_CLIENT_IT"),
            "client_secret": os.getenv("BITWARDEN_CLIENT_SECRET"),
        }
        log_message("LOCAL RUN")
    else:
        secrets = Secrets()
        bitwarden_credentials = secrets.get_secret(credentials_name)
    return bitwarden_credentials
