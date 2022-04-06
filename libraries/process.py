from libraries.common import act_on_element, log_message, capture_page_screenshot, browser, switch_window_and_go_to_url
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
        
        # sharepoint = SharePoint(browser, {"url": "https://esaeducation.sharepoint.com/:x:/g/behavioralhealth/cbo/EVatyGRU6WZFgQsYTlWfAFYBph75bBqPFsaMFGUQftMSlA?e=kZf4AY"})
        # sharepoint.download_file()
        
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
        """
        log_message("Macro Step 2: Prepare for Process")
        mapping_file_data_dict = self.waystar.read_mapping_file()
        print(mapping_file_data_dict)
        log_message("Macro Step 3: Prepare to Process Claims")
        self.centralreach.filter_claims_list()
        self.centralreach.open_extra_centralreach_tabs()
        payor_element_list = self.centralreach.get_payors_list()
        for payor_element in payor_element_list[1:]:
            payor_name = payor_element.find_element_by_xpath('./span').text
            payor_name = payor_name.replace(">", "").strip()
            log_message("Processing claims for payor {}".format(payor_name))
            is_excluded_payor = self.centralreach.check_excluded_payors(payor_name)
            if not is_excluded_payor:
                act_on_element(payor_element, "click_element")
                time.sleep(1)
                claims_result_list = self.centralreach.get_claims_result()
                # time.sleep(5)
                print("len claims_result_list", len(claims_result_list))
                for claims_row in claims_result_list:
                    claim_id = self.centralreach.get_claim_id(claims_row)
                    log_message("Processing claim with id {}".format(claim_id))
                    claim_payor = self.centralreach.get_claim_payor()
                    log_message("The payor of the claim is {}".format(claim_payor))
                    sc_medicaid_cr_name = "s: south carolina medicaid"
                    if sc_medicaid_cr_name in claim_payor.lower():
                        print("SC Medicaid")
                    else:
                        log_message("Macro Step 4: Process Claims in Waystar")
                        self.waystar.filter_claim_by_id(claim_id)
                        has_secondary_claim = self.waystar.check_claim_seq()
                        if has_secondary_claim:
                            log_message("Claim has a secondary in Waystar.")
                            labels_to_apply = ["AR:Secondary Billed"]
                            labels_to_remove = ["AR:Need to Bill Secondary"]
                            #self.centralreach.apply_and_remove_labels_to_claims(labels_to_apply, labels_to_remove)
                        else:
                            log_message("Claim has not a secondary in Waystar.")
                            apply_exclusion_label = self.waystar.check_payer_to_exclude_waystar()
                            if  apply_exclusion_label:
                                labels_to_apply = ["TA: Payor Exclusion"]
                                labels_to_remove = []
                                #self.centralreach.apply_and_remove_labels_to_claims(labels_to_apply, labels_to_remove)
                            else:
                                has_remit = self.waystar.check_if_has_remit()
                                if not has_remit:
                                    labels_to_apply = ["TA: No Primary Remit"]
                                    labels_to_remove = []
                                    #self.centralreach.apply_and_remove_labels_to_claims(labels_to_apply, labels_to_remove)
                                else:
                                    log_message("Has remit. Work In Progress")
                                    # time.sleep(4)
                                    self.waystar.populate_payer_information(mapping_file_data_dict, payor_name)
                                    authorization_number = self.centralreach.get_authorization_number()
                                    if authorization_number == "":
                                        print("No Secondary auth")
                                        labels_to_apply = ["TA: No Secondary Auth"]
                                        labels_to_remove = []
                                        self.centralreach.apply_and_remove_labels_to_claims(labels_to_apply, labels_to_remove)
                                    else:
                                        self.waystar.populate_authorization_number(authorization_number)
                                        subscriber_info_dict = self.centralreach.get_subscriber_information(payor_name)
                                        self.waystar.populate_subscriber_information(subscriber_info_dict)
                                    raise Exception("Breakpoint")
                        time.sleep(3)
                switch_window_and_go_to_url(url = self.centralreach.full_filtered_claims_url)
            else:
                log_message("{} is a excluded payor. Skipping.".format(payor_name))
            time.sleep(3)                    
        

    def finish(self):
        """
        This is where the final steps of your DW are performed (even if main process failed), these can be:
         - moving files to the output folder
         - sending a report
         - uploading files to Google Drive, etc.
        """
        log_message("DW Process Finished")
        browser.close_browser()
        
