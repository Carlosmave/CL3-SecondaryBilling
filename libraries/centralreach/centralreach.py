from tracemalloc import start
from libraries.common import (
    log_message,
    act_on_element,
    capture_page_screenshot,
)
from config import OUTPUT_FOLDER
from datetime import datetime

class CentralReach():

    def __init__(self, rpa_selenium_instance, credentials: dict):
        self.browser = rpa_selenium_instance
        self.centralreach_url = credentials["url"]
        self.centralreach_login = credentials["login"]
        self.centralreach_password = credentials["password"]

    def login(self):
        """
        Login to CentralReach with Bitwarden credentials.
        """
        try:
            log_message("Start - Login CentralReach")
            self.browser.go_to(self.centralreach_url)
            self.input_credentials()
            self.submit_form()
            log_message("Finish - Login CentralReach")
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_Login")
            raise Exception("Login to CentralReach failed")


    def input_credentials(self):
        """
        Function that writes the credentials in the login form.
        """
        # self.browser.click_element('//a[text()="LOGIN"]')
        act_on_element('//input[@id="Username"]', "find_element")
        self.browser.input_text_when_element_is_visible('//input[@id="Username"]', self.centralreach_login)
        self.browser.input_text_when_element_is_visible('//input[@id="Password"]', self.centralreach_password)
        return

    def submit_form(self):
        """
        Function that submits the login form and waits for the main page to load.
        """
        self.browser.click_element('//button[@id="login"]')
        act_on_element('//div[@id="contact-details"]', "find_element")
        return
    
    def filter_claims_list(self):
        """
        Filters claims in the Billing menu.
        """
        log_message("Start - Filter Claims List")
        start_date = "03/01/2022"
        end_date = "03/27/2022"
        start_date = datetime.strptime(start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")

        full_link = "https://members.centralreach.com/#billingmanager/billing/?billingLabelIdIncluded=23593&billStatus=4&startdate={}&enddate={}".format(start_date, end_date)
        self.browser.go_to(full_link)
        log_message("End - Filter Claims List")