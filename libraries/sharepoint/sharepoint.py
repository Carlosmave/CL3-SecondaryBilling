from libraries.common import (
    log_message,
    act_on_element,
    capture_page_screenshot,
    check_file_download_complete
)
from config import OUTPUT_FOLDER

class SharePoint():

    def __init__(self, rpa_selenium_instance, credentials: dict):
        self.browser = rpa_selenium_instance
        self.sharepoint_url = credentials["url"]

    def download_file(self):
        """
        Function that downloads the XLSX file from SharePoint to the OUTPUT folder
        """
        try:
            log_message("Start - Download file from SharePoint")
            self.browser.go_to(self.sharepoint_url)       
            file_download_url = act_on_element('//form[@id="office_form"]/input[@name="fileGetUrl"]', "find_element").get_attribute("value")
            self.browser.go_to(file_download_url)
            check_file_download_complete("xlsx", 10)
            log_message("Finish - Download file from SharePoint")
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_Sharepoint_Download_File")
            raise Exception("Download file from SharePoint failed.")

    