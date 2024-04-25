from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import logging

logger = logging.getLogger(__name__)

class PickCard():
    def pick_card(self, driver: webdriver.Chrome, action: int):
        try: 
            cards = PickCard.pickable_cards(self,driver)
            element = cards[action]
            webdriver.ActionChains(driver=driver).move_to_element(element).click().perform()
        except Exception as e:
            logger.error(e)

    def pickable_cards(self, driver: webdriver.Chrome):
        return driver.find_elements(by=By.CSS_SELECTOR, value="#choiceCards #choiceCardsStock .stockitem")
    
    def can_pick_card(self, driver: webdriver.Chrome, action: int):
        return len(PickCard.pickable_cards(self, driver)) > action