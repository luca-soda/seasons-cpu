from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import logging

logger = logging.getLogger(__name__)
DELAY = 0.01

class SplitCard():
    def split_card(self, driver: webdriver.Chrome, action: int):
        try: 
            cards = SplitCard.splittable_cards(self,driver)
            webdriver.ActionChains(driver).move_to_element(cards[action]).click().perform()
        except Exception as e:
            logger.error(e)

    def splittable_cards(self, driver: webdriver.Chrome):
        return driver.find_elements(by=By.CSS_SELECTOR, value="#player_hand .tooltipable")
    
    def can_split_card(self, driver: webdriver.Chrome, action: int):
        try:
            WebDriverWait(driver=driver, timeout=DELAY).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".library_build_wrap"))
            )
            return len(SplitCard.splittable_cards(self,driver)) > action
        except Exception as e:
            return False