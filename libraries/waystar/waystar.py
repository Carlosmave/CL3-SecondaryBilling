
from libraries.common import act_on_element, capture_page_screenshot, log_message, files
from config import OUTPUT_FOLDER


class Waystar():

    def __init__(self, rpa_selenium_instance, credentials: dict):
        self.browser = rpa_selenium_instance
        self.waystar_url = credentials["url"]
        self.waystar_login = credentials["login"]
        self.waystar_password = credentials["password"]

    def login(self):
        """
        Login to Waystar with Bitwarden credentials.
        """
        try:
            log_message("Start - Login Waystar")
            self.browser.go_to(self.waystar_url)
            self.input_credentials()
            self.submit_form()
            log_message("Finish - Login Waystar")
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_waystar_Login")
            raise Exception("Login to Waystar failed")


    def input_credentials(self):
        """
        Function that writes the credentials in the login form.
        """
        # self.browser.click_element('//a[text()="LOGIN"]')
        self.browser.input_text_when_element_is_visible('//input[@id="loginName"]', self.waystar_login)
        self.browser.input_text_when_element_is_visible('//input[@id="password"]', self.waystar_password)
        return

    def submit_form(self):
        """
        Function that submits the login form and waits for the main page to load.
        """
        self.browser.click_element('//input[@id="loginButton"]')
        act_on_element('//div[@id="mainContent"]', "find_element")
        return

    def read_local_mapping_file(self):
        """
        Function that opens the mapping file and reads the specified sheets
        """
        log_message("Start - Read Local Mapping File")
        mapping_file_data = {
            "Payor List": [],
            "Payor Address": [],
            "Provider Modifier": []
        }

        files.open_workbook("(SHARED) Thoughtful Automation Spreadsheet - Billing.xlsx")
        for sheet_name in mapping_file_data:
            excel_data_dict_list = files.read_worksheet(name = sheet_name, header = True)
            mapping_file_data[sheet_name] = excel_data_dict_list
        files.close_workbook()
        
        log_message("Finish - Read Local Mapping File")
        return mapping_file_data

