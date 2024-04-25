from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import logging
from icecream import ic

logger = logging.getLogger(__name__)

class PickDie():
    def pick_die(self, driver: webdriver.Chrome, action: int):
        try: 
            dice = PickDie.pickable_dice(self,driver)
            webdriver.ActionChains(driver).move_to_element(dice[action]).click().perform()
        except Exception as e:
            logger.error(e)

    def pickable_dice(self, driver: webdriver.Chrome):
        DELAY = 0
        try:
            dice: list[WebElement] = []
            raw_dice = driver.find_elements(by=By.CSS_SELECTOR, value="#seasons_dices .die")
            for die in raw_dice:
                try:
                    WebDriverWait(driver, DELAY, 0.001).until(EC.element_to_be_clickable(die))
                    dice.append(die)
                except:
                    continue
            return dice
        except Exception as e:
            logger.error(e)
            return []
    
    def can_pick_die(self, driver: webdriver.Chrome, action: int):
        return len(PickDie.pickable_dice(self, driver)) > action