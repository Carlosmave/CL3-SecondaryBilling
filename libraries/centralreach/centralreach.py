import time
from libraries.common import (
    log_message,
    act_on_element,
    capture_page_screenshot,
    switch_window_and_go_to_url
)
from config import OUTPUT_FOLDER, tabs_dict
from datetime import datetime

class CentralReach():

    def __init__(self, rpa_selenium_instance, credentials: dict):
        self.browser = rpa_selenium_instance
        self.centralreach_url = credentials["url"]
        self.centralreach_login = credentials["login"]
        self.centralreach_password = credentials["password"]
        self.filtered_claims_url = ""

    def login(self):
        """
        Login to CentralReach with Bitwarden credentials.
        """
        try:
            log_message("Start - Login CentralReach")
            self.browser.go_to(self.centralreach_url)
            self.input_credentials()
            tabs_dict["CentralReachMain"] = len(tabs_dict)
            log_message("Finish - Login CentralReach")
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_Login")
            raise Exception("Login to CentralReach failed")


    def input_credentials(self):
        """
        Function that writes the credentials and submits the login form.
        """
        # self.browser.click_element('//a[text()="LOGIN"]')
        act_on_element('//input[@id="Username"]', "find_element")
        self.browser.input_text_when_element_is_visible('//input[@id="Username"]', self.centralreach_login)
        self.browser.input_text_when_element_is_visible('//input[@id="Password"]', self.centralreach_password)
        self.browser.click_element('//button[@id="login"]')
        act_on_element('//div[@id="contact-details"]', "find_element")
        return
    
    def filter_claims_list(self):
        """
        Filters claims in the Billing menu with two filters activated ('TA-Secondary' filter and date range).
        """
        log_message("Start - Filter Claims List")
        start_date = "03/01/2022"
        end_date = "03/27/2022"
        start_date = datetime.strptime(start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")

        self.filtered_claims_url = "https://members.centralreach.com/#billingmanager/billing/?startdate={}&enddate={}&billingLabelIdIncluded=23593&billStatus=4".format(start_date, end_date)
        switch_window_and_go_to_url(tabs_dict["CentralReachMain"], self.filtered_claims_url)
        log_message("End - Filter Claims List")

    def duplicate_filtered_claims_tab(self):
        """
        Function that opens a new tab and goes to the url with the filtered claim list.
        """
        log_message("Start - Duplicated filtered claims tab")
        self.browser.execute_javascript("window.open()")
        tabs_dict["CentralReachClaim1"] = len(tabs_dict)
        claims_clean_url = self.filtered_claims_url.split("&billingLabelIdIncluded")[0]
        switch_window_and_go_to_url(tabs_dict["CentralReachClaim1"], claims_clean_url)
        self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["CentralReachMain"]])
        log_message("Finish - Duplicated filtered claims tab")
        
    def get_payors_list(self):
        """
        Function that gets the payor list from the filtered claims.
        """
        try:
            log_message("Start - Get payors list")
            act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]/tr[last()]/th[contains(normalize-space(), "Payor")]/a', 'click_element')
            payor_element_list = act_on_element('//div[@id="insurancesFilterList"]//li/a[@class="filter-id" and not(child::span[text() = " > Medicaid"])]', "find_elements")
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_get_payors_list")
            raise Exception("Get payors list in CentralReach failed")
        log_message("Finish - Get payors list")
        return payor_element_list

    def check_excluded_payors(self, payor_name):
        """
        Function that checks if the payor is in the excluded list.
        """
        excluded_payors = ["Florida Medicaid", "Kentucky Medicaid FFS", "Kentucky SLP", "Tricare"]
        return payor_name in excluded_payors

    def get_claims_result(self):
        """Function that gets the claims from list with a specific payor"""
        log_message("Start - Get Claims Result")
        try:
            self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["CentralReachMain"]])
            rows = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item")]', "find_elements")
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_claims_result")
            log_message("No claims result found for this payor.")
            rows = []
            #raise Exception("No claims result found for this payor.")

        log_message("Finish - Get Claims Result")
        return rows

    def get_claim_id(self, claim_result):
        """
        Function that goes to the billing entry details, gets the claim id and searchs results in a new tab
        """
        log_message("Start - Get claim id")
        entry_id = claim_result.get_attribute("id")
        entry_id = entry_id.split("billing-grid-row-")[1].strip()
        claim_url = "https://members.centralreach.com/#claims/list/?billingEntryId={}".format(entry_id)
        self.browser.execute_javascript("window.open()")
        tabs_dict["CentralReachClaim2"] = len(tabs_dict)
        switch_window_and_go_to_url(tabs_dict["CentralReachClaim2"], claim_url)

        claim_id_column_pos = 3
        try:
            claim_id = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item") and position() = 1]/td[{}]'.format(claim_id_column_pos), "find_element").text
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_get_claim_id")
            #log_message("Get claim id failed.")
            raise Exception("Get claim id failed.")          
        self.browser.execute_javascript("window.close()")
        self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["CentralReachClaim1"]])
        self.browser.input_text_when_element_is_visible('//div[@class="module-search"]//input[@id="s2id_autogen2_search"]', claim_id)
        time.sleep(1)
        act_on_element('//li[child::div[@class="select2-result-label"]][1]', 'click_element')
        self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["CentralReachMain"]])
        
        log_message("Finish - Get claim id")
        return claim_id

    def get_claim_payor(self):
        """
        Function that gets the payor of the claim.
        """
        log_message("Start - Get claim payor")
        payor_column_pos = 10
        try:
            claim_payor = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item") and position() = 1]/td[{}]'.format(payor_column_pos),'find_element').text
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_get_claim_payor")
            #log_message("Get claim payor failed.")
            raise Exception("Get claim payor failed.")
        log_message("Finish - Get claim payor")
        return claim_payor

    def apply_and_remove_labels_to_claims(self):
        """
        Function that gets the payor of the claim.
        """
        log_message("Start - Apply and remove labels to claim")
        try:
            act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]/tr[last()]/th[contains(@class, "check")]/input[@type = "checkbox"]','click_element')
            act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]//button[contains(normalize-space(), "Label selected")]','click_element')
            self.browser.input_text_when_element_is_visible('//input[@id="s2id_autogen12"]', "AR:SECONDARY BILLED")
            act_on_element('//div[@id="select2-drop"]//div[@class="select2-result-label" and text() = "AR:Secondary Billed"]','click_element')
            self.browser.input_text_when_element_is_visible('//input[@id="s2id_autogen13"]', "AR:Need to Bill Secondary")
            act_on_element('//div[@id="select2-drop"]//div[@class="select2-result-label" and text() = "AR:Need to Bill Secondary"]','click_element')
            act_on_element('//button[text() = "Apply Label Changes"]','click_element')
        
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_Apply_and_remove_labels_to_claim")
            #log_message("Get claim payor failed.")
            raise Exception("Apply and remove labels to claims.")
        log_message("Finish - Apply and remove labels to claims")
          