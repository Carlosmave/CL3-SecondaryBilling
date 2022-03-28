from tracemalloc import start
from libraries.common import (
    log_message,
    act_on_element,
    capture_page_screenshot,
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
            self.submit_form()
            tabs_dict["CentralReachMain"] = len(tabs_dict)
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

        self.filtered_claims_url = "https://members.centralreach.com/#billingmanager/billing/?startdate={}&enddate={}&billingLabelIdIncluded=23593&billStatus=4".format(start_date, end_date)
        self.browser.go_to(self.filtered_claims_url)
        log_message("End - Filter Claims List")

    def get_payors_list(self):
        """
        Function that gets the payor list from the filtered claims.
        """
        act_on_element('//div[@id="content"]/table/thead[@class="tableFloatingHeaderOriginal"]/tr[last()]/th[contains(normalize-space(), "Payor")]/a', 'click_element')
        payor_element_list = act_on_element('//div[@id="insurancesFilterList"]//li/a[@class="filter-id"]', "find_elements")
        return payor_element_list

    def check_excluded_payors(self, payor_name):
        """
        Function that check if the payer is in the excluded list.
        """
        excluded_payors = ["Florida Medicaid", "Kentucky Medicaid FFS", "Kentucky SLP", "Tricare"]
        return payor_name in excluded_payors

    def duplicate_window(self):
        url_without_filters = self.filtered_claims_url.split("&billingLabelIdIncluded=")[0].strip()
        self.browser.execute_javascript("window.open()")
        self.browser.switch_window(locator="NEW")
        self.browser.go_to(url_without_filters)
        tabs_dict["CentralReachClaim1"] = len(tabs_dict)
        tabs_dict["CentralReachClaim2"] = len(tabs_dict)

    def get_claims_result(self):
        log_message("Start - Get Claims Result")
        try:
            self.duplicate_window()
            self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["CentralReachMain"]])
            rows = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item")]', "find_elements")
        except Exception as e:
            capture_page_screenshot(OUTPUT_FOLDER, "Exception_centralreach_claims_result")
            raise Exception("Get claims result failed")

        log_message("Finish - Get Claims Result")
        return rows

    def view_claims(self, claim_result):
        print("claim_result", claim_result)
        act_on_element(claim_result.find_element_by_xpath('.//button[child::i[@class="fa fa-cog"]]'), "click_element")
        act_on_element(claim_result.find_element_by_xpath('.//div[@class="dropdown open"]/ul[position() = 1]/li[@data-title="Click to view claims generated"]/a'), "click_element")
        print(tabs_dict)
        self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["CentralReachClaim1"]])
        claim_id = act_on_element('//div[@id="content"]/table/tbody/tr[contains(@class, "row-item") and position() = 1]/td[3]', "find_element").text
        self.browser.switch_window(locator=self.browser.get_window_handles()[tabs_dict["CentralReachClaim3"]])
        self.browser.input_text_when_element_is_visible('//div[@class="module-search"]//input[@id="s2id_autogen2_search"]', claim_id)
        act_on_element('//div[@class="select2-result-label"][1]', 'click_element')