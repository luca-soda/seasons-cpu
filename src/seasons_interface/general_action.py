from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import logging
from icecream import ic

logger = logging.getLogger(__name__)

blacklisted_actions = ['resetPlayerTurn', 'transmute', 'undo']

class GeneralAction():
    def click_general_action(self, driver: webdriver.Chrome, action: int):
        try: 
            action_buttons = GeneralAction.clickable_general_actions(self, driver)
            webdriver.ActionChains(driver).move_to_element(action_buttons[action]).click().perform()
        except Exception as e:
            logger.error(e)

    def clickable_general_actions(self, driver: webdriver.Chrome):
        general_actions = driver.find_element(by=By.CSS_SELECTOR, value="#generalactions")
        action_buttons = general_actions.find_elements(by=By.CSS_SELECTOR, value=".action-button")
        f_action_buttons = list(filter(lambda button: button.get_dom_attribute('id') not in blacklisted_actions, action_buttons))
        return f_action_buttons

    def can_click_general_action(self, driver: webdriver.Chrome, action: int):
        return len(GeneralAction.clickable_general_actions(self,driver)) > action