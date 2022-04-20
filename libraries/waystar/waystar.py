
from libraries.common import act_on_element, capture_page_screenshot, log_message, switch_window, close_window, files
from config import OUTPUT_FOLDER, RunMode
import time
from copy import deepcopy

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
        log_message("Start - Login Waystar")
        try:
            switch_window("Waystar", self.waystar_url)
            self.input_credentials()
            self.check_additional_authentication()
            act_on_element('//div[@id="mainContent"]', "find_element")
            
        except Exception:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_waystar_Login")
            raise Exception("Login to Waystar failed")
        log_message("Finish - Login Waystar")

        
    def input_credentials(self):
        """
        Function that writes the credentials and submits the login form.
        """
        self.browser.input_text_when_element_is_visible('//input[@id="loginName"]', self.waystar_login)
        self.browser.input_text_when_element_is_visible('//input[@id="password"]', self.waystar_password)
        self.browser.click_element('//input[@id="loginButton"]')
        return

    def check_additional_authentication(self):
        """
        Function that checks if additional authentication is needed and answers the question.
        """
        try:
            act_on_element('//input[@id="verifyAnswer"]', 'find_element', 2)
            self.browser.input_text_when_element_is_visible('//input[@id="verifyAnswer"]', self.additional_authentication_answer)
            #act_on_element('//input[@id="trustDevice"]', "click_element")
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
            "Provider Modifier": [],
            "Location Modifier": []
        }
        try:
            files.open_workbook("{}/{}".format(OUTPUT_FOLDER, self.mapping_file_name))
            #files.open_workbook("{}".format(self.mapping_file_name))
            for sheet_name in mapping_file_data:
                excel_data_list = files.read_worksheet(name = sheet_name, header = True)
                excel_data_cleaned_list = [row for row in [{key: value for key, value in row_dict.items() if value != None} for row_dict in excel_data_list] if len(row)>0]
                mapping_file_data[sheet_name] = excel_data_cleaned_list
            files.close_workbook()
        except Exception as e:
            raise Exception("Read mapping file failed:" , e)

        log_message("Finish - Read Mapping File")
        return mapping_file_data

    def determine_if_valid_secondary_claim(self, claim_id: str, labels_dict: dict):
        """
        Function that searchs the claim and checks if it has a proper secondary 
        """        
        log_message("Start - Determine If Valid Secondary Claim")

        seq_number_to_check = "2"
        new_labels_dict = deepcopy(labels_dict)

        switch_window("Waystar", self.claims_search_url)
        act_on_element('//select[@id="SearchCriteria_Status"]', "click_element")
        act_on_element('//select[@id="SearchCriteria_Status"]/option[@value="-1"]', "click_element")
        self.browser.input_text_when_element_is_visible('//input[@id="SearchCriteria_PatNumber"]', claim_id)
        act_on_element('//select[@id="SearchCriteria_TransDate"]', "click_element")
        act_on_element('//select[@id="SearchCriteria_TransDate"]/option[text()="All"]', "click_element")
        act_on_element('//input[@id="ClaimListingSearchButtonBottom"]', "click_element")

        claim_seq = act_on_element('//table[@id="claimsGrid"]//tr[contains(@class,"gridViewRow")][1]/td[contains(@class, "sequenceNumCell")]', "find_element").text
        if seq_number_to_check == claim_seq.strip():
            new_labels_dict['labels_to_add'].append("AR:Secondary Billed")
            new_labels_dict['labels_to_remove'].append("AR:Need to Bill Secondary")
        else:   
            payer_name_waystar = act_on_element('//table[@id="claimsGrid"]//tr[contains(@class,"gridViewRow")][1]/td[contains(@class, "subPayerCell")]/span', "find_element").get_attribute("title")
            if "tricare" in payer_name_waystar.lower() or "humana" in payer_name_waystar.lower():
                new_labels_dict['labels_to_add'].append("TA: Payor Exclusion")
            else:
                try:
                    act_on_element('//table[@id="claimsGrid"]//tr[contains(@class,"tagRow")][1]//span[@title = "Has Remit"]', 'find_element', 2)
                except:
                    log_message("Claim doesn't have remit")
                    new_labels_dict['labels_to_add'].append("TA: No Primary Remit")

        log_message("Finish - Determine If Valid Secondary Claim")
        return new_labels_dict

    def populate_payer_information(self, mapping_file_data_dict_list: dict, payor_name_cr: str):
        """
        Function that populates payer information from the mapping file to Waystar using the CentralReach payor name.
        """
        log_message("Start - Populate Payer Information")

        switch_window("Waystar")
        self.browser.mouse_over('//table[@id="claimsGrid"]//tr[contains(@class,"gridViewRow")][1]')
        act_on_element('//a[@id="gridActionSecond"]', 'click_element', 7)
        switch_window("WaystarSubInfo", open_new_window = False)
        act_on_element('//input[@id="scr1_ChangePayerButton"]', 'click_element')
        payor = next((payor for payor in mapping_file_data_dict_list['Payor List'] if payor_name_cr.upper() == str(payor['CentralReach Payor Name']).upper()), None)
        if payor:
            self.browser.input_text_when_element_is_visible('//input[@id="scr1_name"]', payor['Waystar Payer Name'])
            self.browser.input_text_when_element_is_visible('//input[@id="scr1_payerid"]', payor['Payer ID'])
            if payor['Requires Address'].upper() == "YES":
                payor_address = next((payor for payor in mapping_file_data_dict_list['Payor Address'] if payor_name_cr.upper() == str(payor['CentralReach Payor Name']).upper()), None)
                if payor_address:
                    self.browser.input_text_when_element_is_visible('//input[@id="scr1_payeradd1"]', payor_address['Address Line 1'])
                    self.browser.input_text_when_element_is_visible('//input[@id="scr1_payercity"]', payor_address['City'])
                    self.browser.input_text_when_element_is_visible('//input[@id="scr1_payerstate"]', payor_address['State'])
                    self.browser.input_text_when_element_is_visible('//input[@id="scr1_payerzip"]', payor_address['Zip'])
        time.sleep(5) #delete later
        if RunMode.save_changes:
            act_on_element('//input[@id="scr1_SaveButton"]', 'click_element')
        else:
            act_on_element('//a[@id="scr1_CloseWindow"]', 'click_element')
        
        log_message("Finish - Populate Payer Information")

    def populate_authorization_and_subscriber_information(self, subscriber_info_dict: dict, authorization_number: str):
        """
        Function that populates subscriber information that was previously extracted from CentralReach
        """
        log_message("Start - Populate Authorization and Subscriber Information")

        release_information_option_value = "Y"
        assign_benefits_option_value = "Y"

        switch_window("WaystarSubInfo")
        self.browser.input_text_when_element_is_visible('//input[@id="scr1_FV2_priorauth"]', authorization_number)
        self.browser.input_text_when_element_is_visible('//input[@id="scr1_FV3_fname"]', subscriber_info_dict["first_name"])
        self.browser.input_text_when_element_is_visible('//input[@id="scr1_FV3_lname"]', subscriber_info_dict["last_name"])
        act_on_element('//select[@id="scr1_FV3_sex"]', "click_element")
        act_on_element('//select[@id="scr1_FV3_sex"]/option[@value = "{}"]'.format(subscriber_info_dict["gender"]), "click_element")
        self.browser.input_text_when_element_is_visible('//input[@id="scr1_FV3_birthdate"]', subscriber_info_dict["birthday"])
        self.browser.input_text_when_element_is_visible('//input[@id="scr1_FV3_membernum"]', subscriber_info_dict["insured_id"])
        act_on_element('//select[@id="scr1_FV3_relation"]', "click_element")
        act_on_element('//select[@id="scr1_FV3_relation"]/option[@value = "{}"]'.format(subscriber_info_dict["patient_relationship_to_subscriber"]), "click_element")
        act_on_element('//select[@id="scr1_FV3_releaseinfo"]', "click_element")
        act_on_element('//select[@id="scr1_FV3_releaseinfo"]/option[@value = "{}"]'.format(release_information_option_value), "click_element")
        act_on_element('//select[@id="scr1_FV3_assignbenefits"]', "click_element")
        act_on_element('//select[@id="scr1_FV3_assignbenefits"]/option[@value = "{}"]'.format(assign_benefits_option_value), "click_element")
        time.sleep(5)#delete later 
        act_on_element('//input[@id="NextButton"]', 'click_element')

        log_message("Finish - Populate Authorization and Subscriber Information")


    def check_remit_information(self, mapping_file_data_dict_list: dict, payor_name_cr: str, provider_label: str, labels_dict: dict):
        """
        Function that checks if the remit information is valid to proceed. Otherwise set labels.
        """
        new_labels_dict = deepcopy(labels_dict)
        payor = next((payor for payor in mapping_file_data_dict_list['Payor List'] if payor_name_cr.upper() == str(payor['CentralReach Payor Name']).upper()), None)
        if payor:
            valid_billing = self.check_billing_information(payor)
            if valid_billing:
                act_on_element('//input[@id="NextButton"]', 'click_element')
                valid_adjudication = self.check_adjudication_information()
                if valid_adjudication:
                    act_on_element('//input[@id="NextButton"]', 'click_element')
                    self.populate_modifiers_information(payor, mapping_file_data_dict_list, payor_name_cr, provider_label)
                    new_labels_dict['labels_to_add'].append("AR:Secondary Billed")
                    new_labels_dict['labels_to_remove'].append("AR:Need to Bill Secondary")
                else:
                    new_labels_dict['labels_to_add'].append("TA: Multiple Primary Remits")
            else:
                new_labels_dict['labels_to_add'].append("TA: Rendering Provider")
        else:
            raise Exception("Waystar payor in mapping file not found")
        return new_labels_dict

    def check_billing_information(self, payor_dict: dict):
        """
        Checks if the payor is a RENDERING provider and the individual rendering option is checked on Waystar
        """
        log_message("Start - Check Billing Information")

        individual_rendering_checked = act_on_element('//input[@id="scr2_rendering_FV_rbIndividual"]', 'find_element').get_attribute("checked")

        log_message("Finish - Check Billing Information")
        return payor_dict['Rendering Provider'].upper() == "RENDERING" and individual_rendering_checked
                
    def check_adjudication_information(self):
        """
        Function that checks if claim paid date, payer paid amount and other payer control number inputs are auto-populated
        """
        log_message("Start - Check Adjudication Information")

        adjudication_date_value = act_on_element('//input[@id="scr3_FV_claimpaiddate"]', 'find_element').get_attribute("value")
        payer_paid_amount_value = act_on_element('//input[@id="scr3_FV_payerpaid"]', 'find_element').get_attribute("value")
        other_payer_claim_control_num_value = act_on_element('//input[@id="scr3_FV_otherPayerControlNum"]', 'find_element').get_attribute("value")

        log_message("Finish - Check Adjudication Information")
        return adjudication_date_value and payer_paid_amount_value and other_payer_claim_control_num_value
    

    def populate_modifiers_information(self, payor_dict: dict, mapping_file_data_dict_list: dict, payor_name_cr: str, provider_label: str):
        """
        Function that populates modifiers for each service row based on the mapping file information.
        Each row can be populated up to 2 modifiers with two different types (PROVIDER and PLACE OF SERVICE)
        """
        log_message("Start - Populate Modifiers Information")

        if payor_dict['MODIFIER'].upper() == "YES":
            number_of_modifiers = payor_dict['# OF MODIFIERS']
            place_of_service_column_pos = 4
            procedure_code_column_pos = 5
            modifiers_column_pos = 6
            page_count = act_on_element('//span[@id="scr4_FV1_topPager_lblPageCount"]', 'find_element').text
            page_count = int(page_count)
            
            for page in range(1, page_count + 1):
                log_message("Populating modifiers for page {} of {}".format(page, page_count))
                try:
                    act_on_element('//input[@id="scr4_FV1_topPager_txtPage" and @value = "{}"]'.format(page), 'find_element', 4)
                    service_rows = act_on_element('//table[@id="scr4_FV1_GV"]//tr[descendant::a[text() = "Delete"]]', 'find_elements')
                except:
                    capture_page_screenshot(OUTPUT_FOLDER, "Exception_get_service_rows_Waystar")
                    log_message("Get service rows failed")
                else:
                    for service_row in service_rows:
                        procedure_code = service_row.find_element_by_xpath('./td[{}]//input'.format(procedure_code_column_pos)).get_attribute("value")
                        
                        for modifier_number in range(1, number_of_modifiers + 1):
                            try:

                                modifier = "MODIFIER {}".format(modifier_number)
                                if payor_dict[modifier].upper() == "PROVIDER":
                                    provider_modifier = next((provider_mod for provider_mod in mapping_file_data_dict_list['Provider Modifier'] if payor_name_cr.upper() == str(provider_mod['CentralReach Payor Name']).upper() and provider_label.upper() == str(provider_mod['Provider Label']).upper() and procedure_code.upper() == str(provider_mod['Billing Code']).upper()), None)
                                    if provider_modifier:
                                        modifier_input = service_row.find_element_by_xpath('./td[{}]//input[{}]'.format(modifiers_column_pos, modifier_number))
                                        self.browser.input_text_when_element_is_visible(modifier_input, provider_modifier["PROVIDER {}".format(modifier)])
                                elif payor_dict[modifier].upper() == "PLACE OF SERVICE":
                                    place_of_service_value = service_row.find_element_by_xpath('./td[{}]//input'.format(place_of_service_column_pos)).get_attribute("value")
                                    location_modifier = next((location_mod for location_mod in mapping_file_data_dict_list['Location Modifier'] if payor_name_cr.upper() == str(location_mod['Payor'].upper()) and place_of_service_value == str(location_mod['Location'])), None)
                                    if location_modifier:
                                        modifier_input = service_row.find_element_by_xpath('./td[{}]//input[{}]'.format(modifiers_column_pos, modifier_number))
                                        self.browser.input_text_when_element_is_visible(modifier_input, location_modifier[modifier.title()])
                            except Exception as e:
                                print(e)
                                capture_page_screenshot(OUTPUT_FOLDER, "Exception_Populating_Modifier_number_{}_Waystar".format(modifier_number))
                                log_message("Populating Modifier number {} for payor {} in Waystar failed".format(modifier_number, payor_dict['Waystar Payer Name']))
                
                
                if page_count > 1 and page < page_count:
                    try:
                        act_on_element('//a[@id="scr4_FV1_topPager_lnkNext"]', 'click_element', 1)
                    except:
                        print("next page not clicked")              
        else:
            log_message("This payor doesn't have any modifiers")
        time.sleep(5) #delete later
        if RunMode.save_changes:
            act_on_element('//input[@id="SubmitButton"]', 'click_element')
        else:
            close_window("WaystarSubInfo")

        log_message("Finish - Populate Modifiers Information")