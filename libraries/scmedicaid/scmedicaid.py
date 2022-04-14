
from libraries.common import (
    log_message,
    act_on_element,
    capture_page_screenshot,
    switch_window
)
from config import OUTPUT_FOLDER
import time

class SCMedicaid():

    def __init__(self, rpa_selenium_instance, credentials: dict):
        self.browser = rpa_selenium_instance
        self.scmedicaid_url = credentials["url"]
        self.scmedicaid_login = credentials["login"]
        self.scmedicaid_password = credentials["password"]
        self.provider_to_work = "EARLY AUTISM PROJECT INC - 1417477175"
        self.enter_professional_claim_url = "https://portal.scmedicaid.com/claimsentry/cmsclaimslist"
        self.primary_diagnosis_code = "F840"

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

    def populate_beneficiary_information(self, client_name: str):
        split_name = client_name.split(" ")
        first_name = split_name[0]
        last_name = split_name[1]
        act_on_element('//a[@id="listwindowdisplaylink" and text() = "Get from List"]', "click_element")
        time.sleep(1)
        table_base_xpath = '//table[@class="t-data-grid"]/tbody/tr'
        last_name_xpath = 'child::td[@class="lastName" and contains(translate(text(), "{}", "{}"), "{}")]'.format(last_name.upper(), last_name.lower(), last_name.lower())
        first_name_xpath = 'child::td[@class="firstName" and contains(translate(text(), "{}", "{}"), "{}")]'.format(first_name.upper(), first_name.lower(), first_name.lower())
        #//table[@class="t-data-grid"]/tbody/tr[child::td[@class="firstName" and contains(translate(text(), 'ETHAN', 'ethan'), 'ethan')]]//a[@class="memberListLink"]
        full_xpath = '{}[{} and {}]//a[@class="memberListLink"]'.format(table_base_xpath, last_name_xpath, first_name_xpath)
        print(full_xpath)
        act_on_element(full_xpath, "click_element") 
        time.sleep(1)
        act_on_element('//input[@value="Continue"]', "click_element") 

    def populate_rendering_provider(self, manager_name: str):
        act_on_element('//div[@class="fieldRow" and child::label[text() = "Billing provider and rendering provider are the same"]]/input[@name="checkbox"]', "click_element")
        act_on_element('//h4[contains(text(), "Rendering Provider")]/a[text() = "Get from List"]', "click_element") 
        table_base_xpath = '//table[@class="t-data-grid"]/tbody/tr'
        manager_name_xpath = 'child::td[@class="providerName" and text() = "{}"]'.format(manager_name.upper())
        full_xpath = '{}[{}]//a[@class="providerListLink"]'.format(table_base_xpath, manager_name_xpath)
        print(full_xpath)
        act_on_element(full_xpath, "click_element")
        time.sleep(1)
        act_on_element('//input[@value="Continue"]', "click_element") 

    def populate_authorization_number(self, authorization_number : str):
        self.browser.input_text_when_element_is_visible('//input[@name="priorAuthNumber"]', authorization_number)
        time.sleep(1)
        act_on_element('//input[@value="Continue"]', "click_element")

    def populate_primary_diagnosis(self):
        act_on_element('//div[contains(text(), "Primary Diagnosis Code")]/a[text() = "Get from List"]', "click_element") 
        table_base_xpath = '//table[@class="t-data-grid"]/tbody/tr'
        primary_diagnosis_code_xpath = '//a[@class="codeListLink" and text() = "{}"]'.format(self.primary_diagnosis_code)
        full_xpath = '{}{}'.format(table_base_xpath, primary_diagnosis_code_xpath)
        print(full_xpath)
        act_on_element(full_xpath, "click_element")
        time.sleep(1)
        act_on_element('//input[@value="Continue"]', "click_element")
        
    def populate_det_lines(self, service_lines_dict_list: list):
        for service_line in service_lines_dict_list:
            from_date_service_input = act_on_element('//input[@name="fromDateOfService"]', "find_element")
            from_date_service_input.click()
            from_date_service_input.clear()
            self.browser.input_text_when_element_is_visible(from_date_service_input, service_line['from_date_service'])
            to_date_service_input = act_on_element('//input[@name="toDateOfService"]', "find_element")
            to_date_service_input.click()
            to_date_service_input.clear()
            self.browser.input_text_when_element_is_visible(to_date_service_input, service_line['to_date_service'])
            act_on_element('//select[@name="placeOfService"]', "click_element")
            act_on_element('//select[@name="placeOfService"]/option[@value="{}"]'.format(service_line['place']), "click_element")
            self.browser.input_text_when_element_is_visible('//input[@name="hcpcsCode"]', service_line['hcpcs_code'])
            self.browser.input_text_when_element_is_visible('//input[@name="charge"]', service_line['charge'])
            self.browser.input_text_when_element_is_visible('//input[@name="units"]', service_line['units'])
            time.sleep(1)
            act_on_element('//input[@name="addLineButton"]', "click_element")
            time.sleep(3)
        act_on_element('//input[@value="Continue"]', "click_element")
        act_on_element('//input[@value="Continue"]', "click_element")
    
    def populate_other_coverage_info(self, client_name):
        insured_name = client_name.split(" ")
        insured_name = "{}, {}".format(insured_name[1], insured_name[0])
        act_on_element('//h4[contains(text(), "Add/Edit Other Insurance Coverage Information")]/a[text() = "Get from List"]', "click_element")
        number_of_pages = act_on_element('//div[@class="t-data-grid-pager"][1]/a[contains(@id, "pager")][last()]', "find_element").text
        number_of_pages = int(number_of_pages)
        for page in range(1, number_of_pages + 1):
            log_message("Populating modifiers for page {} of {}".format(page, number_of_pages))
            if page > 1:    
                act_on_element('//div[@class="t-data-grid-pager"][1]/a[contains(@id, "pager") and text() = "{}"]'.format(page), "click_element") 
            table_base_xpath = '//table[@class="t-data-grid"]/tbody/tr'
            insured_xpath = '[child::td[@class="name"]]//a[normalize-space() = "{}"]'.format(insured_name)
            full_xpath = '{}{}'.format(table_base_xpath, insured_xpath)
            print(full_xpath)
            try:
                act_on_element(full_xpath, "click_element")
            except:
                pass
            else:
                print("Patient {} was found in page {}".format(client_name, page))
                
                
            time.sleep(3)
        #act_on_element('//input[@value="Continue"]', "click_element")
    def fill_insured_coverage_form(self, insured_info):
        paid_amount_input = act_on_element('//input[@name="paidAmount"]', "find_element")
        paid_amount_input.click()
        paid_amount_input.clear()
        self.browser.input_text_when_element_is_visible(paid_amount_input, insured_info['paid_amount'])
        self.browser.input_text_when_element_is_visible('//input[@name="paidDate"]', insured_info['paid_date'])
        coinsurance_amount_input = act_on_element('//input[@name="coinsuranceAmount"]', "find_element")
        coinsurance_amount_input.click()
        coinsurance_amount_input.clear()
        self.browser.input_text_when_element_is_visible(coinsurance_amount_input, insured_info['coinsurance_amount'])
        act_on_element('//select[@name="placeOfService"]', "click_element")
        act_on_element('//select[@name="placeOfService"]/option[@value="{}"]'.format(service_line['place']), "click_element")
        self.browser.input_text_when_element_is_visible('//input[@name="hcpcsCode"]', service_line['hcpcs_code'])
        self.browser.input_text_when_element_is_visible('//input[@name="charge"]', service_line['charge'])
        self.browser.input_text_when_element_is_visible('//input[@name="units"]', service_line['units'])