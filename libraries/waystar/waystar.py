
from platform import release
from libraries.common import act_on_element, capture_page_screenshot, log_message, switch_window_and_go_to_url, files
from config import OUTPUT_FOLDER, tabs_dict
import time

class Waystar():

    def __init__(self, rpa_selenium_instance, credentials: dict):
        self.browser = rpa_selenium_instance
        self.waystar_url = credentials["url"]
        self.waystar_login = credentials["login"]
        self.waystar_password = credentials["password"]
        self.additional_authentication_answer = "Thoughtful Automation"
        self.claims_search_url = "https://claims.zirmed.com/Claims/Listing/Index?appid=1"
        self.mapping_file_name = "(SHARED) Thoughtful Automation Spreadsheet - Billing.xlsx"

    def login(self):
        """
        Login to Waystar with Bitwarden credentials.
        """
        try:
            log_message("Start - Login Waystar")
            self.browser.execute_javascript("window.open()")
            tabs_dict["Waystar"] = len(tabs_dict)
            switch_window_and_go_to_url(tabs_dict["Waystar"], self.waystar_url)
            self.input_credentials()
            self.check_additional_authentication()
            log_message("Finish - Login Waystar")
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_waystar_Login")
            raise Exception("Login to Waystar failed")

    def input_credentials(self):
        """
        Function that writes the credentials and submits the login form.
        """
        self.browser.input_text_when_element_is_visible('//input[@id="loginName"]', self.waystar_login)
        self.browser.input_text_when_element_is_visible('//input[@id="password"]', self.waystar_password)
        self.browser.click_element('//input[@id="loginButton"]')
        
        act_on_element('//div[@id="mainContent"]', "find_element")
        return

    def check_additional_authentication(self):
        """
        Function that checks if additional authentication is needed and answers the question.
        """
        try:
            act_on_element('//input[@id="verifyAnswer"]', 'find_element', 2)
            self.browser.input_text_when_element_is_visible('//input[@id="verifyAnswer"]', self.additional_authentication_answer)
            act_on_element('//input[@id="trustDevice"]', "click_element")
            act_on_element('//input[@id="VerifyButton"]', "click_element")
        except:
            pass

    def read_mapping_file(self):
        """
        Function that opens the mapping file and reads the specified sheets
        """
        log_message("Start - Read Mapping File")
        mapping_file_data = {
            "Payor List": [],
            "Payor Address": [],
            "Provider Modifier": []
        }
        try:
            #files.open_workbook("{}/{}".format(OUTPUT_FOLDER, self.mapping_file_name))
            files.open_workbook("{}".format(self.mapping_file_name))
            for sheet_name in mapping_file_data:
                excel_data_dict_list = files.read_worksheet(name = sheet_name, header = True)
                mapping_file_data[sheet_name] = excel_data_dict_list
            files.close_workbook()
        except Exception as e:
            log_message("Read mapping file failed.")
            raise Exception("Read mapping file failed.")

        log_message("Finish - Read Mapping File")
        return mapping_file_data

    def filter_claim_by_id(self, claim_id):
        """
        Function that filters the claim by claim id
        """
        switch_window_and_go_to_url(tabs_dict["Waystar"], self.claims_search_url)
        act_on_element('//select[@id="SearchCriteria_Status"]', "click_element")
        act_on_element('//select[@id="SearchCriteria_Status"]/option[@value="-1"]', "click_element")
        self.browser.input_text_when_element_is_visible('//input[@id="SearchCriteria_PatNumber"]', claim_id)
        act_on_element('//select[@id="SearchCriteria_TransDate"]', "click_element")
        act_on_element('//select[@id="SearchCriteria_TransDate"]/option[text()="All"]', "click_element")
        act_on_element('//input[@id="ClaimListingSearchButtonBottom"]', "click_element")

    def check_claim_seq(self):
        """
        Function that checks if the claim seq is "2" (has secondary) 
        """
        number_to_check = "2"
        claim_seq = act_on_element('//table[@id="claimsGrid"]//tr[contains(@class,"gridViewRow")][1]/td[contains(@class, "sequenceNumCell")]', "find_element").text
        return number_to_check == claim_seq.strip()

    def check_payer_to_exclude_waystar(self):
        """
        Function that checks if the payer has to be excluded and skipped.
        """
        payer_name_waystar = act_on_element('//table[@id="claimsGrid"]//tr[contains(@class,"gridViewRow")][1]/td[contains(@class, "subPayerCell")]/span', "find_element").get_attribute("title")
        return "tricare" in payer_name_waystar.lower() or "humana" in payer_name_waystar.lower()

    def check_if_has_remit(self):
        """
        Function that checks if the claim has a remit attached to it
        """
        try:
            act_on_element('//table[@id="claimsGrid"]//tr[contains(@class,"tagRow")][1]//span[@title = "Has Remit"]', 'find_element', 2)
            return True
        except:
            log_message("Claim doesn't have remit")
            return False

    def populate_payer_information(self, mapping_file_data_dict, payor_name_cr):
        """
        Function that populates payer information from the mapping file to Waystar using the CentralReach payor name.
        """
        self.browser.mouse_over('//table[@id="claimsGrid"]//tr[contains(@class,"gridViewRow")][1]')
        act_on_element('//a[@id="gridActionSecond"]', 'click_element')
        tabs_dict["WaystarSubInfo"] = len(tabs_dict)
        self.browser.switch_window(locator="NEW")
        act_on_element('//input[@id="scr1_ChangePayerButton"]', 'click_element')
        payor = next((payor for payor in mapping_file_data_dict['Payor List'] if payor_name_cr.upper() == payor['CentralReach Payor Name'].upper()), None)
        print("Payor", payor)
        if payor:
            self.browser.input_text_when_element_is_visible('//input[@id="scr1_name"]', payor['Waystar Payer Name'])
            self.browser.input_text_when_element_is_visible('//input[@id="scr1_payerid"]', payor['Payer ID'])
            if payor['Requires Address'].upper() == "YES":
                payor_address = next((payor for payor in mapping_file_data_dict['Payor Address'] if payor_name_cr.upper() == payor['CentralReach Payor Name'].upper()), None)
                print("Payor address", payor_address)
                if payor_address:
                    self.browser.input_text_when_element_is_visible('//input[@id="scr1_payeradd1"]', payor_address['Address Line 1'])
                    self.browser.input_text_when_element_is_visible('//input[@id="scr1_payercity"]', payor_address['City'])
                    self.browser.input_text_when_element_is_visible('//input[@id="scr1_payerstate"]', payor_address['State'])
                    self.browser.input_text_when_element_is_visible('//input[@id="scr1_payerzip"]', payor_address['Zip'])
        time.sleep(5)
        act_on_element('//a[@id="scr1_CloseWindow"]', 'click_element')
        #act_on_element('//input[@id="scr1_SaveButton"]', 'click_element')
        #act_on_element('//input[@id="NextButton"]', 'click_element')

        #raise Exception("Breakpoint")

    def populate_authorization_number(self, authorization_number):
        """
        Function that populates authorization number extracted from CentralReach in the Prior Auth input
        """
        self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["WaystarSubInfo"]])
        self.browser.input_text_when_element_is_visible('//input[@id="scr1_FV2_priorauth"]', authorization_number)
        time.sleep(5)

        #raise Exception("Breakpoint")

    def populate_subscriber_information(self, subscriber_info_dict):
        """
        Function that populates authorization number extracted from CentralReach in the Prior Auth input
        """

        release_information_option_value = "Y"
        assign_benefits_option_value = "Y"

        self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["WaystarSubInfo"]])
        self.browser.input_text_when_element_is_visible('//input[@id="scr1_FV3_fname"]', subscriber_info_dict["first_name"])
        self.browser.input_text_when_element_is_visible('//input[@id="scr1_FV3_lname"]', subscriber_info_dict["last_name"])
        act_on_element('//select[@id="scr1_FV3_sex"]', "click_element")
        act_on_element('//select[@id="scr1_FV3_sex"]/option[@value = "{}"]'.format(subscriber_info_dict["gender"]), "click_element")


        self.browser.input_text_when_element_is_visible('//input[@id="scr1_FV3_birthdate"]', subscriber_info_dict["birthday"])
        #self.browser.clear_element_text('//input[@id="scr1_FV3_birthdate"]')
            
        self.browser.input_text_when_element_is_visible('//input[@id="scr1_FV3_membernum"]', subscriber_info_dict["insured_id"])
        act_on_element('//select[@id="scr1_FV3_relation"]', "click_element")
        act_on_element('//select[@id="scr1_FV3_relation"]/option[@value = "{}"]'.format(subscriber_info_dict["patient_relationship_to_subscriber"]), "click_element")
        act_on_element('//select[@id="scr1_FV3_releaseinfo"]', "click_element")
        act_on_element('//select[@id="scr1_FV3_releaseinfo"]/option[@value = "{}"]'.format(release_information_option_value), "click_element")
        act_on_element('//select[@id="scr1_FV3_assignbenefits"]', "click_element")
        act_on_element('//select[@id="scr1_FV3_assignbenefits"]/option[@value = "{}"]'.format(assign_benefits_option_value), "click_element")
        time.sleep(5)   
        act_on_element('//input[@id="NextButton"]', 'click_element')