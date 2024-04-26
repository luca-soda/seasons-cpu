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

class PlayCard():
    def play_card(self, driver: webdriver.Chrome, action: int):
        try: 
            cards = PlayCard.playable_cards(self,driver)
            element = cards[action]
            webdriver.ActionChains(driver=driver).move_to_element(element).click().perform()
        except Exception as e:
            logger.error(e)

    def playable_cards(self, driver: webdriver.Chrome):
        return driver.find_elements(by=By.CSS_SELECTOR, value=".possibleCard .cardtitle")
    
    def can_play_card(self, driver: webdriver.Chrome, action: int):
        return len(PlayCard.playable_cards(self, driver)) > action