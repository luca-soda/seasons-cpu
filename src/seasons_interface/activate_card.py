from typing import Optional
from typing import TypeVar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')
def not_none(obj: Optional[T]) -> T:
    assert obj is not None
    return obj

class ActivateCard():
    def activate_card(self, driver: webdriver.Chrome, action: int):
        try: 
            cards = ActivateCard.activable_cards(self,driver)
            element = cards[action]
            webdriver.ActionChains(driver=driver).move_to_element(element).click().perform()
        except Exception as e:
            logger.error(e)

    def activable_cards(self, driver: webdriver.Chrome):
        elements = driver.find_element(by=By.CSS_SELECTOR, value='#currentPlayerTablea').find_elements(by=By.CSS_SELECTOR, value=".cardactivation")
        elements = list(map(lambda element: element.find_element(by=By.XPATH, value="./../.."), elements))
        elements = list(filter(lambda element: "activated" not in not_none(element.get_attribute('class')).split(), elements))
        return elements
    
    def can_pick_card(self, driver: webdriver.Chrome, action: int):
        return len(ActivateCard.activable_cards(self, driver)) > action