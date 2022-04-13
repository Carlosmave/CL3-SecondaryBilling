import time
from libraries.common import (
    log_message,
    act_on_element,
    capture_page_screenshot,
    switch_window
)
from config import OUTPUT_FOLDER, RunMode, tabs_dict
from datetime import datetime

class CentralReach():

    def __init__(self, rpa_selenium_instance, credentials: dict):
        self.browser = rpa_selenium_instance
        self.centralreach_url = credentials["url"]
        self.centralreach_login = credentials["login"]
        self.centralreach_password = credentials["password"]
        self.start_date = "03/01/2022"
        self.end_date = "03/27/2022"
        self.base_filtered_claims_url = ""
        self.full_filtered_claims_url = ""
        self.payor_name = ""
        self.client_id = ""
        self.claim_id = ""
        self.provider_label = ""
        self.authorization_number = ""
        self.sc_medicaid_cr_name = "S: South Carolina Medicaid"
        self.labels_dict = {}
        self.subscriber_info_dict = {}



    def login(self):
        """
        Login to CentralReach with Bitwarden credentials.
        """
        try:
            log_message("Start - Login CentralReach")
            #tabs_dict["CentralReachMain"] = len(tabs_dict)
            switch_window("CentralReachMain", self.centralreach_url, open_new_window = False)
            self.input_credentials()
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
        act_on_element('//div[@id="contact-details"]', "find_element", 10)
        return

    def filter_claims_list(self):
        """
        Filters claims in the Billing menu with two filters activated ('TA-Secondary' filter and date range).
        """
        log_message("Start - Filter Claims List")
        start_date_tmp = datetime.strptime(self.start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        end_date_tmp = datetime.strptime(self.end_date, "%m/%d/%Y").strftime("%Y-%m-%d")

        self.base_filtered_claims_url = "https://members.centralreach.com/#billingmanager/billing/?startdate={}&enddate={}".format(start_date_tmp, end_date_tmp)
        self.full_filtered_claims_url = "{}&billingLabelIdIncluded=23593&billStatus=4".format(self.base_filtered_claims_url)
        switch_window("CentralReachMain", self.full_filtered_claims_url)
        self.open_extra_centralreach_tabs()
        log_message("End - Filter Claims List")

    def open_extra_centralreach_tabs(self):
        """
        Function that opens two tabs 
        CentralReachClaim1: claims list only with date range filter and later used for searching by claim id.
        CentralReachClaim2: shows each billing entry details
        CentralReachClientInfo: client details such as auths and payor information
        """
        log_message("Start - Open Extra CentralReach tabs")

        new_tabs_to_open_list = {
            "CentralReachClaim1": self.base_filtered_claims_url,
            "CentralReachClaim2": "",
            "CentralReachClientInfo": ""
        }
        for new_tab_name, new_tab_url in new_tabs_to_open_list.items():
            switch_window(new_tab_name, new_tab_url)

        log_message("Finish - Open Extra CentralReach tabs")
        
    def get_payors_list(self):
        """
        Function that gets the payor list from the filtered claims.
        """
        log_message("Start - Get Payors List")
        try:
            switch_window("CentralReachMain")
            act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]/tr[last()]/th[contains(normalize-space(), "Payor")]/a', 'click_element')
            payor_element_list = act_on_element('//div[@id="insurancesFilterList"]//li/a[@class="filter-id" and not(child::span[text() = " > Medicaid"])]', "find_elements")
        except:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_get_payors_list")
            raise Exception("Get payors list in CentralReach failed")
        log_message("Finish - Get payors list")
        return payor_element_list

    def get_payor_name_from_element(self, payor_element):
        """
        Function that gets the name of the current payor element in the loop
        and also checks if it's in the excluded list.
        """
        try:
            switch_window("CentralReachMain")
            self.payor_name = payor_element.find_element_by_xpath('./span').text
            self.payor_name = self.payor_name.replace(">", "").strip()
            excluded_payors = ["Florida Medicaid", "Kentucky Medicaid FFS", "Kentucky SLP", "Tricare"]
            if self.payor_name in excluded_payors:
                log_message("{} is in the excluded payor list. Skipping".format(self.payor_name))
                self.payor_name = None
            else:
                act_on_element(payor_element, "click_element")
        except:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_get_payor_name_from_element")
            raise Exception("Get payor name from element failed.")

    def get_claims_result(self):
        """Function that gets the claims from list with a specific payor"""
        log_message("Start - Get Claims Result")
        try:
            switch_window("CentralReachMain")
            time.sleep(2)
            rows = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item")]', "find_elements")
        except:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_claims_result")
            log_message("No claims result found for this payor.")
            rows = []
            #raise Exception("No claims result found for this payor.")

        log_message("Finish - Get Claims Result")
        return rows

    def get_claim_information(self, claim_result):
        """
        Function that gets the claim id and searchs it in a new tab to extract the full details
        """
        log_message("Start - Get Claim Information")
        claim_id_column_pos = 3
        payor_column_pos = 10
        client_name_column_pos = 9
        provider_column_pos = 11
        try:
            switch_window("CentralReachMain")
            entry_id = claim_result.get_attribute("id")
            entry_id = entry_id.split("billing-grid-row-")[1].strip()
            billing_entry_url = "https://members.centralreach.com/#claims/list/?billingEntryId={}".format(entry_id)
            switch_window("CentralReachClaim2", billing_entry_url)

            self.claim_id = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item") and position() = 1]/td[{}]'.format(claim_id_column_pos), "find_element").text
            claim_search_url = "{}&claimId={}".format(self.base_filtered_claims_url, self.claim_id)
            switch_window("CentralReachClaim1", claim_search_url)
            time.sleep(2)
            claim_payor = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item") and position() = 1]/td[{}]'.format(payor_column_pos),'find_element', 10).text
            self.client_id = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item") and position() = 1]/td[{}]/a[contains(@class, "vcard")]'.format(client_name_column_pos),'find_element', 10).get_attribute("contactid")
            print("client_id", self.client_id)
            act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item") and position() = 1]/td[{}]/a[contains(@class, "vcard")]'.format(provider_column_pos),'click_element', 10)
            self.provider_label = act_on_element('//span[@class="tag-name" and contains(text(), "Certification")]', 'find_element').text
            self.labels_dict = {
                "labels_to_add": [],
                "labels_to_remove": []
            }
        except:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_get_claim_information")
            raise Exception("Get Claim information failed.")
        
        log_message("Finish - Get Claim Information")
        return self.sc_medicaid_cr_name.lower() in claim_payor.lower()
         

    def get_authorization_number(self):
        """
        Function that gets the authorization number of the secondary Claim.
        """
        log_message("Start - Get Authorization Number on CentralReach")
        date_column_pos = 7
        code_column_pos = 5

        switch_window("CentralReachClaim1")
        claim_dates = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item")]/td[{}]/span[contains(@class, "inline-block")]'.format(date_column_pos),'find_elements')
        claim_dates = [datetime.strptime(claim_date.text, "%m/%d/%y") for claim_date in claim_dates]
        first_claim_date = claim_dates[0]
        claim_month_date = int(first_claim_date.strftime("%m"))
        claim_year_date = first_claim_date.strftime("%Y")
        auth_url = "https://members.centralreach.com/#billingmanager/authorizations/?clientId={}".format(self.client_id)
        
        switch_window("CentralReachClientInfo", auth_url)
        act_on_element('//button[child::span[@data-bind="text: monthDisplay"]]','click_element')
        act_on_element('//li[{}]/a[@data-click="setMonth"]'.format(claim_month_date),'click_element')
        act_on_element('//button[child::span[@data-bind="text: year"]]','click_element')
        act_on_element('//li/a[@data-click="setYear" and text() = "{}"]'.format(claim_year_date),'click_element')
        time.sleep(3)
        try:
            secondary_rows = act_on_element('//div[@class="module-grid"]/table/tbody/tr[child::td[position() = {} and descendant::a[text() = "SECONDARY"]]]'.format(code_column_pos),'find_elements')
        except:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_get_authorization_number")
            log_message("Secondary claim not found")   
        else:
            since_column_pos = 6
            until_column_pos = 7
            valid_secondary_claims = []
            for row in secondary_rows:
                since_date = row.find_element_by_xpath('./td[{}]/div'.format(since_column_pos)).text
                since_date = datetime.strptime(since_date, "%m/%d/%Y")
                until_date = row.find_element_by_xpath('./td[{}]/div'.format(until_column_pos)).text
                until_date = datetime.strptime(until_date, "%m/%d/%Y")
                claims_in_range = [claim_date for claim_date in claim_dates if since_date <= claim_date <= until_date]

                if len(claims_in_range) == len(claim_dates):
                    log_message("All claims are in valid range for this secondary.")
                    valid_secondary_claims.append(row)
                
            if len(valid_secondary_claims) == 1:
                secondary_row = valid_secondary_claims[0]
                auth_doc_url = secondary_row.find_element_by_xpath('./td[{}]/a[child::i[contains(@class, "fa-file")]]'.format(code_column_pos)).get_attribute("href")
                self.browser.go_to(auth_doc_url)
                self.authorization_number = act_on_element('//input[@data-bind="value: authorizationNumber"]', 'find_element', 15).get_attribute("value")
            elif len(valid_secondary_claims) >= 2:
                self.authorization_number = None
        time.sleep(5)
        log_message("Finish - Get authorization number in CentralReach")
        return self.check_if_valid_auth_number()


    def check_if_valid_auth_number(self):
        """
        Function that checks if the authorization number is valid. Otherwise, apply labels
        """
        valid_auth_number = True
        if self.authorization_number is None:
            self.labels_dict['labels_to_add'].append("TA: Split Secondary Auth")
            self.apply_and_remove_labels_to_claims()
            valid_auth_number = False
        elif self.authorization_number == "":
            self.labels_dict['labels_to_add'].append("TA: No Secondary Auth")
            self.apply_and_remove_labels_to_claims()
            valid_auth_number = False
        else:
            self.get_subscriber_information()

        return valid_auth_number
        
    def get_subscriber_information(self):
        """
        Function that gets subscriber information from the secondary payor of the client.
        """
        log_message("Start - Get Subscriber Information on CentralReach")

        payors_patient_info_url = "https://members.centralreach.com/#contacts/details/?id={}&mode=profile&edit=payors".format(self.client_id)
        switch_window("CentralReachClientInfo", payors_patient_info_url)
        act_on_element('//div[@class="list-group"]/div[descendant::div[@class = "txt-lg" and normalize-space() = "Secondary: {}"]]//a[text() = "Details"]'.format(self.payor_name),'click_element', 15)
        act_on_element('//a[@data-toggle="tab" and child::span[text() = "Subscriber"]]','click_element')
        try:
            first_name = act_on_element('//input[@data-bind="value: firstName"]','find_element').get_attribute("value")
            last_name = act_on_element('//input[@data-bind="value: lastName"]','find_element').get_attribute("value")
            gender = act_on_element('//select[contains(@data-bind, "value: gender")]','find_element').get_attribute("value")
            insured_id =  act_on_element('//input[@data-bind="value: policyId"]','find_element').get_attribute("value")
            birth_date_month = act_on_element('//input[@data-bind="value: birthDateMonth"]','find_element').get_attribute("value")
            birth_date_day = act_on_element('//input[@data-bind="value: birthDateDay"]','find_element').get_attribute("value")
            birth_date_year = act_on_element('//input[@data-bind="value: birthDateYear"]','find_element').get_attribute("value")
        
            act_on_element('//a[@data-toggle="tab" and child::span[text() = "Patient"]]','click_element')
            patient_relationship_to_subscriber = act_on_element('//select[contains(@data-bind, "value: relationType")]','find_element').get_attribute("value")

            relationship_to_check = "18"
            if patient_relationship_to_subscriber.upper() == relationship_to_check.upper():
                birthday = "{}/{}/{}".format(birth_date_month, birth_date_day, birth_date_year)
            else:
                birthday = ""
        except:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_get_subscriber_information")
            raise Exception("Get Subscriber Information failed.")
        else:
            self.subscriber_info_dict['first_name'] = first_name
            self.subscriber_info_dict['last_name'] = last_name
            self.subscriber_info_dict['gender'] = gender
            self.subscriber_info_dict['insured_id'] = insured_id
            self.subscriber_info_dict['patient_relationship_to_subscriber'] = patient_relationship_to_subscriber
            self.subscriber_info_dict['birthday'] = birthday

            print("subscriber_info", self.subscriber_info_dict)
            log_message("Finish - Get Subscriber Information on CentralReach")

            time.sleep(5)

    
    def apply_and_remove_labels_to_claims(self):
        """
        Function that bulk applies and removes certain labels to claims.
        """
        log_message("Start - Apply and Remove Labels to Claims")
        applied_changes = True
        if len(self.labels_dict['labels_to_add']) > 0 or len(self.labels_dict['labels_to_remove']) > 0:
            switch_window("CentralReachClaim1")
            time.sleep(2)
            labels_to_add = self.labels_dict.get('labels_to_add', [])
            labels_to_remove = self.labels_dict.get('labels_to_remove', [])
            try:
                act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]/tr[last()]/th[contains(@class, "check")]/input[@type = "checkbox"]','click_element')
                act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]//button[contains(normalize-space(), "Label selected")]','click_element')
                
                for label in labels_to_add:
                    self.browser.input_text_when_element_is_visible('//div[@class="modal-body"]/div[@class="panel panel-default" and descendant::h4 = "Apply Labels"]//input[@class="select2-input select2-default"]', label)
                    act_on_element('//div[@id="select2-drop"]//div[@class="select2-result-label" and text() = "{}"]'.format(label),'click_element')
                
                for label in labels_to_remove:
                    self.browser.input_text_when_element_is_visible('//div[@class="modal-body"]/div[@class="panel panel-default" and descendant::h4 = "Remove Labels"]//input[@class="select2-input select2-default"]', label)
                    act_on_element('//div[@id="select2-drop"]//div[@class="select2-result-label" and text() = "{}"]'.format(label),'click_element')
                
                time.sleep(2)
                if RunMode.save_changes:
                    act_on_element('//button[text() = "Apply Label Changes"]','click_element')
                else:
                    act_on_element('//div[@class="modal in" and descendant::h2[contains(text(), "Bulk Apply Labels")]]//button[text() = "Close"]','click_element')
        
                act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]//a[@id="btnBillingPayment"]','click_element')
                act_on_element('//input[@class = "form-control hasDatepicker"]','find_element', 10)
                todays_date = datetime.today().strftime("%m/%d/%Y")
                self.browser.input_text_when_element_is_visible('//input[@class = "form-control hasDatepicker"]', todays_date)
                
                act_on_element('//select[@name="payment-type"]', "click_element")
                act_on_element('//select[@name="payment-type"]/option[text() = "Activity"]', "click_element")
                reference_txt = ", ".join(labels_to_add)
                self.browser.input_text_when_element_is_visible('//input[contains(@data-bind, "reference")]', reference_txt)
                act_on_element('//select[@class = "form-control required add-create-payor"]', "click_element")
                act_on_element('//select[@class = "form-control required add-create-payor"]/option[contains(text(), "Secondary:")]', "click_element")
                time.sleep(8) #delete later
                if RunMode.save_changes:
                    act_on_element('//button[text() = "Apply Payments"]','click_element')
                else:
                    act_on_element('//div[@class="bulk-payments-container"]//button[text() = "Cancel"]','click_element')
            except Exception as e:
                capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_Apply_and_remove_labels_to_claim")
                raise Exception("Apply and remove labels to claims failed.")
        else:
            applied_changes = False
        log_message("Finish - Apply and Remove Labels to Claims")
        return applied_changes
