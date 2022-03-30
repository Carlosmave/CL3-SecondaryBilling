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
        self.base_filtered_claims_url = ""
        self.full_filtered_claims_url = ""
        self.labels_to_apply = ["AR:Secondary Billed"]
        self.labels_to_remove = ["AR:Need to Bill Secondary"]

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

        self.base_filtered_claims_url = "https://members.centralreach.com/#billingmanager/billing/?startdate={}&enddate={}".format(start_date, end_date)
        self.full_filtered_claims_url = "{}&billingLabelIdIncluded=23593&billStatus=4".format(self.base_filtered_claims_url)
        switch_window_and_go_to_url(tabs_dict["CentralReachMain"], self.full_filtered_claims_url)
        log_message("End - Filter Claims List")

    def open_extra_centralreach_tabs(self):
        """
        Function that opens two tabs 
        CentralReachClaim1: claims list only with date range filter and later used for searching by claim id.
        CentralReachClaim2: shows each billing entry details
        """
        log_message("Start - Open Extra CentralReach tabs")
        self.browser.execute_javascript("window.open()")
        tabs_dict["CentralReachClaim1"] = len(tabs_dict)
        switch_window_and_go_to_url(tabs_dict["CentralReachClaim1"], self.base_filtered_claims_url)
        
        self.browser.execute_javascript("window.open()")
        tabs_dict["CentralReachClaim2"] = len(tabs_dict)

        self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["CentralReachMain"]])
        log_message("Finish - Open Extra CentralReach tabs")
        
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
        Function that goes to the billing entry details, gets the claim id and searchs it in a new tab
        """
        log_message("Start - Get claim id")
        try:
            self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["CentralReachMain"]])
            entry_id = claim_result.get_attribute("id")
            entry_id = entry_id.split("billing-grid-row-")[1].strip()
            billing_entry_url = "https://members.centralreach.com/#claims/list/?billingEntryId={}".format(entry_id)
            switch_window_and_go_to_url(tabs_dict["CentralReachClaim2"], billing_entry_url)
            print(tabs_dict)

            claim_id_column_pos = 3
            claim_id = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item") and position() = 1]/td[{}]'.format(claim_id_column_pos), "find_element").text
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_get_claim_id")
            #log_message("Get claim id failed.")
            raise Exception("Get claim id failed.")

        claim_search_url = "{}&claimId={}".format(self.base_filtered_claims_url, claim_id)
        switch_window_and_go_to_url(tabs_dict["CentralReachClaim1"], claim_search_url)
        
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
        Function that bulk applies and removes certain labels to claims.
        """
        self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["CentralReachClaim2"]])
        log_message("Start - Apply and remove labels to claim")
        try:
            act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]/tr[last()]/th[contains(@class, "check")]/input[@type = "checkbox"]','click_element')
            act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]//button[contains(normalize-space(), "Label selected")]','click_element')
            
            for label in self.labels_to_apply:
                self.browser.input_text_when_element_is_visible('//div[@class="modal-body"]/div[@class="panel panel-default" and descendant::h4 = "Apply Labels"]//input[@class="select2-input select2-default"]', label)
                act_on_element('//div[@id="select2-drop"]//div[@class="select2-result-label" and text() = "{}"]'.format(label),'click_element')
            
            for label in self.labels_to_remove:
                self.browser.input_text_when_element_is_visible('//div[@class="modal-body"]/div[@class="panel panel-default" and descendant::h4 = "Remove Labels"]//input[@class="select2-input select2-default"]', label)
                act_on_element('//div[@id="select2-drop"]//div[@class="select2-result-label" and text() = "{}"]'.format(label),'click_element')
            
            # act_on_element('//button[text() = "Apply Label Changes"]','click_element')
            act_on_element('//div[@class="modal in" and descendant::h2[contains(text(), "Bulk Apply Labels")]]//button[text() = "Close"]','click_element')
        
            act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]//a[@id="btnBillingPayment"]','click_element')
            act_on_element('//input[@class = "form-control hasDatepicker"]','find_element')
            todays_date = datetime.today().strftime("%m/%d/%Y")
            self.browser.input_text_when_element_is_visible('//input[@id="dp1648594034096"]]', todays_date)
            
            act_on_element('//select[@name="payment-type"]', "click_element")
            act_on_element('//select[@name="payment-type"]/option[text() = "Activity"]', "click_element")
            reference_txt = ", ".join(self.labels_to_apply)
            self.browser.input_text_when_element_is_visible('//input[contains(@data-bind, "reference")]', reference_txt)
            act_on_element('//select[@class = "form-control required add-create-payor"]', "click_element")
            act_on_element('//select[@class = "form-control required add-create-payor"]/option[contains(text(), "Secondary:")]', "click_element")

            #act_on_element('//button[text() = "Apply Payments"]','click_element')
            act_on_element('//div[@class="bulk-payments-container"]//button[text() = "Cancel"]','click_element')
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_Apply_and_remove_labels_to_claim")
            #log_message("Apply and remove labels to claims failed.")
            raise Exception("Apply and remove labels to claims failed.")
    
        log_message("Finish - Apply and remove labels to claims.")
          