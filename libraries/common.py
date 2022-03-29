import shutil, time, os, sys
from robot.api import logger
from datetime import datetime, timedelta
from RPA.Robocorp.Vault import Vault
from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem
from ta_bitwarden_cli.ta_bitwarden_cli import Bitwarden
from config import OUTPUT_FOLDER
from RPA.Excel.Files import Files


browser = Selenium()
file_system = FileSystem()
files = Files()


def log_message(message: str, level: str = 'INFO', console: bool = True):
    """
    Logs the message passed as an argument.
    """
    log_switcher = {
        'TRACE': logger.trace,
        'INFO': logger.info,
        'WARN': logger.warn,
        'ERROR': logger.error
    }
    if not level.upper() in log_switcher.keys() or level.upper() == 'INFO':
        logger.info(message, True, console)
    else:
        if level.upper() == 'ERROR':
            logger.info(message, True, console)
        else:
            log_switcher.get(level.upper(), logger.error)(message, True)


def print_version():
    """
    Prints the current version of the digital worker.
    """
    try:
        file = open('VERSION')
        try:
            log_message('Version {}'.format(file.read().strip()))
        except Exception as ex:
            log_message('Error reading VERSION file. {}'.format(str(ex)))
        finally:
            file.close()
    except Exception as e:
        log_message('VERSION file not found. {}'.format(str(e)))


def create_or_clean_dir(folder_path: str):
    """
    Creates a directory or cleans it.
    """
    shutil.rmtree(folder_path, ignore_errors=True)
    try:
        os.mkdir(folder_path)
    except FileExistsError:
        log_message('Folder {} already exists'.format(folder_path))

def get_bitwarden_data(credentials_name: str = 'bitwarden_credentials') -> dict:
    """
    Gets the data from Bitwarden.
    """
    items = {
        "CentralReach": "CentralReach",
        "Waystar": "CL Waystar",
        "SCMedicaid": "SC Medicaid"
    }
    if len(sys.argv) > 1 and sys.argv[1].lower() == "local":
        bitwarden_credentials = {
            "username": os.getenv("BITWARDEN_USERNAME"),
            "password": os.getenv("BITWARDEN_PASSWORD"),
            "client_id": os.getenv("BITWARDEN_CLIENT_ID"),
            "client_secret": os.getenv("BITWARDEN_CLIENT_SECRET")
        }
    else:
        vault = Vault()
        bitwarden_credentials = vault.get_secret(credentials_name)

    bw = Bitwarden(bitwarden_credentials)
    bw.bitwarden_login()
    bw.get_data(items)
    return bw.data


def capture_page_screenshot(folder_path: str, name: str = None):
    """
    Captures and screenshot of the actual screen.
    """
    if not name:
        name = "Exception_{}.png".format(datetime.now().strftime("%H_%M_%S"))
    else:
        name = "{}_{}.png".format(name.replace("/", ""), datetime.now().strftime("%H_%M_%S"))
    browser.capture_page_screenshot(
        os.path.join(
            folder_path,
            name,
        )
    )


def act_on_element(path: str, action: str, time_range: int = 5):
    """
    Acts as the fluent wait of Selenium.
    """
    timer = datetime.now() + timedelta(0, time_range)
    while timer > datetime.now():
        try:
            if action == "click_element":
                browser.click_element(path)
                return True
            elif action == "find_elements":
                results = browser.find_elements(path)
                if results:
                    return results
                else:
                    raise Exception
            elif action == "find_element":
                result = browser.find_element(path)
                return result
        except Exception as e:
            time.sleep(1)
    raise Exception("Element {} not found".format(path))


def check_file_download_complete(file_extension: str, time_range: int = 10, folder: str = OUTPUT_FOLDER):
    """
    Checks that a file has finished downloading.
    """
    actual_downloaded_files_amount = len(file_system.find_files("{}/*.{}".format(folder, file_extension)))
    downloaded_files_amount = actual_downloaded_files_amount
    timer = datetime.now() + timedelta(0, time_range)
    while not downloaded_files_amount == actual_downloaded_files_amount + 1 and timer > datetime.now():
        time.sleep(1)
        downloaded_files = file_system.find_files("{}/*.{}".format(folder, file_extension))
        downloaded_files_amount = len(downloaded_files)
    if downloaded_files_amount != actual_downloaded_files_amount + 1:
        raise Exception("The file download timed out")
    else:
        return downloaded_files


def switch_window_and_go_to_url(tab: int = 0, url: str = ""):
    """Function that switchs to the desired tab and goes to the url"""
    browser.switch_window(locator=browser.get_window_handles()[tab])
    browser.go_to(url)