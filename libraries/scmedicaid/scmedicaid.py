
from libraries.common import (
    log_message,
    act_on_element,
    capture_page_screenshot,
    switch_window
)
from config import OUTPUT_FOLDER


class SCMedicaid():

    def __init__(self, rpa_selenium_instance, credentials: dict):
        self.browser = rpa_selenium_instance
        self.scmedicaid_url = credentials["url"]
        self.scmedicaid_login = credentials["login"]
        self.scmedicaid_password = credentials["password"]
        self.provider_to_work = "EARLY AUTISM PROJECT INC - 1417477175"
        self.enter_professional_claim_url = "https://portal.scmedicaid.com/claimsentry/cmsclaimslist"

    def login(self):
        """
        Login to SCMedicaid with Bitwarden credentials.
        """
        try:
            log_message("Start - Login SCMedicaid")
            switch_window("SCMedicaid", self.scmedicaid_url)
            self.input_credentials()
            self.select_provider()
            log_message("Finish - Login SCMedicaid")
        except Exception:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_scmedicaid_Login")
            raise Exception("Login to SCMedicaid failed")


    def input_credentials(self):
        """
        Function that writes the credentials in the login form and submits it.
        """
        # self.browser.click_element('//a[text()="LOGIN"]')
        self.browser.input_text_when_element_is_visible('//input[@id="username"]', self.scmedicaid_login)
        self.browser.input_text_when_element_is_visible('//input[@id="password"]', self.scmedicaid_password)
        self.browser.click_element('//input[@id="submit_0"]')
        act_on_element('//div[@id="content"]', "find_element", 10)
        
    def select_provider(self):
        act_on_element('//select[@id="providerID2"]', "click_element")
        act_on_element('//select[@id="providerID2"]/option[text() = "{}"]'.format(self.provider_to_work), "click_element")
        act_on_element('//input[@id="update"]', "click_element")
        self.browser.go_to(self.enter_professional_claim_url)
        act_on_element('//input[@id="submit_3" and @value="Enter New Claim"]', "click_element")

    def populate_beneficiary_information(self, client_name):
        split_name = client_name.split(" ")
        first_name = split_name[0]
        last_name = split_name[1]
        act_on_element('//a[@id="listwindowdisplaylink" and text() ="Get from List"]', "click_element")
        table_base_xpath = '//table[@class="t-data-grid"]/tbody/tr'
        last_name_xpath = 'child::td[@class="lastName" and text() = "{}"]'.format(last_name)
        first_name_xpath = 'child::td[@class="firstName" and text() = "{}"]'.format(first_name)
        full_xpath = '{}[{} and {}]//a[@class="memberListLink"]'.format(table_base_xpath, last_name_xpath, first_name_xpath)
        print(full_xpath)
        act_on_element(full_xpath, "click_element") 
        act_on_element('//input[@value="Continue"]', "click_element") 

    def populate_rendering_provider(self, manager_name):
        act_on_element('//input[@id="checkbox_4a7e0e6cd49b0"]', "click_element")
        act_on_element('//a[@id="rendProvListWindowDisplayLink_4a7e0e6cd49b0"]', "click_element") 
        table_base_xpath = '//table[@class="t-data-grid"]/tbody/tr'
        manager_name_xpath = 'child::td[@class="providerName" and text() = "{}"]'.format(manager_name)
        full_xpath = '{}[{}]//a[@class="providerListLink"]'.format(table_base_xpath, manager_name_xpath)
        print(full_xpath)
        act_on_element(full_xpath, "click_element") 

        
