
from libraries.common import (
    log_message,
    act_on_element,
    capture_page_screenshot,
)
from config import OUTPUT_FOLDER


class SCMedicaid():

    def __init__(self, rpa_selenium_instance, credentials: dict):
        self.browser = rpa_selenium_instance
        self.scmedicaid_url = credentials["url"]
        self.scmedicaid_login = credentials["login"]
        self.scmedicaid_password = credentials["password"]

    def login(self):
        """
        Login to SCMedicaid with Bitwarden credentials.
        """
        try:
            log_message("Start - Login SCMedicaid")
            self.browser.go_to(self.scmedicaid_url)
            self.input_credentials()
            self.submit_form()
            log_message("Finish - Login SCMedicaid")
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_scmedicaid_Login")
            raise Exception("Login to SCMedicaid failed")


    def input_credentials(self):
        """
        Function that writes the credentials in the login form.
        """
        # self.browser.click_element('//a[text()="LOGIN"]')
        self.browser.input_text_when_element_is_visible('//input[@id="Username"]', self.scmedicaid_login)
        self.browser.input_text_when_element_is_visible('//input[@id="Password"]', self.scmedicaid_password)
        return

    def submit_form(self):
        """
        Function that submits the login form and waits for the main page to load.
        """
        self.browser.click_element('//button[@name="login"]')
        #act_on_element('//div[@id="main"]', "find_element")
        return