from libraries.common import log_message, capture_page_screenshot, browser
from libraries.centralreach.centralreach import CentralReach
from libraries.waystar.waystar import Waystar
import time
from config import OUTPUT_FOLDER

class Process:
    def __init__(self, credentials: dict):
        log_message("Initialization.")
        """
        All the initialization steps are performed here, without which it makes no sense to go to the main process.
        This part may include:
         - authorization to the site
         - connection to Gmail and Google Disk is created, etc.
         - the files that are necessary for the process are downloaded
        """

        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "download.default_directory": OUTPUT_FOLDER,
            "download.prompt_for_download": False,
        }
        browser.open_available_browser(preferences = prefs)
        browser.set_window_size(1920, 1080)
        browser.maximize_browser_window()
        
        print(credentials)
        centralreach = CentralReach(browser, credentials["CentralReach"])
        centralreach.login()
        self.centralreach = centralreach
        time.sleep(5)

        # waystar = Waystar(browser, credentials["Waystar"])
        # #waystar.login()
        # self.waystar = waystar

    def start(self):
        """
        This is where the main process takes place, function, depends on your process, can contain:
          - splitted into macro steps that go one by one
          - contains the main process loop
        """
        log_message("Macro Step 1: Prepare for Process")
        # mapping_file_data_dict = self.waystar.read_local_mapping_file()
        #print(mapping_file_data_dict)
        log_message("Macro Step 2: Prepare to Process Claims")
        # self.centralreach.filter_claims_list()

    def finish(self):
        """
        This is where the final steps of your DW are performed (even if main process failed), these can be:
         - moving files to the output folder
         - sending a report
         - uploading files to Google Drive, etc.
        """
        log_message("DW Process Finished")
        browser.close_browser()
        
