from libraries.common import log_message, capture_page_screenshot, browser
from libraries.sharepoint.sharepoint import SharePoint
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
        
        sharepoint = SharePoint(browser, {"url": "https://esaeducation.sharepoint.com/:x:/g/behavioralhealth/cbo/EVatyGRU6WZFgQsYTlWfAFYBph75bBqPFsaMFGUQftMSlA?e=kZf4AY"})
        sharepoint.download_file()

        centralreach = CentralReach(browser, credentials["CentralReach"])
        centralreach.login()
        self.centralreach = centralreach

        waystar = Waystar(browser, credentials["Waystar"])
        waystar.login()
        self.waystar = waystar
        

    def start(self):
        """
        This is where the main process takes place, function, depends on your process, can contain:
          - splitted into macro steps that go one by one
          - contains the main process loop

        --------------------- THIS IS NOT THE FINAL PROCESS VERSION. IT WILL CHANGE
        """
        log_message("--------------- [Macro Step 2: Prepare for Process] ---------------")
        mapping_file_data_dict = self.waystar.read_mapping_file()
        log_message("--------------- [Macro Step 3: Prepare to Process Claims] ---------------")
        self.centralreach.filter_claims_list()
        payor_element_list = self.centralreach.get_payors_list()
        for payor_element in payor_element_list[2:]:
            self.centralreach.get_payor_name_from_element(payor_element)
            if self.centralreach.payor_name:
                log_message("******* Processing claims for payor {} *******".format(self.centralreach.payor_name))
                claims_result_list = self.centralreach.get_claims_result()
                for claim_row in claims_result_list:
                    is_sc_medicaid = self.centralreach.get_claim_information(claim_row)
                    log_message("***Processing claim with id {}****".format(self.centralreach.claim_id))
                    if is_sc_medicaid:
                        print("SC Medicaid")
                    else:
                        log_message("--------------- [Macro Step 4: Process Claims in Waystar] ---------------")
                        self.centralreach.labels_dict = self.waystar.determine_if_valid_secondary_claim(self.centralreach.claim_id, self.centralreach.labels_dict)
                        applied_labels = self.centralreach.apply_and_remove_labels_to_claims()
                        if not applied_labels:
                            is_valid_auth_number = self.centralreach.get_authorization_number()
                            if is_valid_auth_number:
                                self.waystar.populate_payer_information(mapping_file_data_dict, self.centralreach.payor_name)
                                self.waystar.populate_authorization_and_subscriber_information(self.centralreach.subscriber_info_dict, self.centralreach.authorization_number)
                                self.centralreach.labels_dict = self.waystar.check_remit_information(mapping_file_data_dict, self.centralreach.payor_name, self.centralreach.provider_label, self.centralreach.labels_dict)
                                self.centralreach.apply_and_remove_labels_to_claims()
                  

    def finish(self):
        """
        This is where the final steps of your DW are performed (even if main process failed), these can be:
         - moving files to the output folder
         - sending a report
         - uploading files to Google Drive, etc.
        """
        log_message("DW Process Finished")
        browser.close_browser()
        
