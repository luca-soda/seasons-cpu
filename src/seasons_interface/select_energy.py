from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from .utils import not_none
import logging, re

logger = logging.getLogger(__name__)

class SelectEnergy():
    def select_energy(self, driver: webdriver.Chrome, action: int):
        try: 
            elements = SelectEnergy.selectable_energies(self,driver)
            element = elements[action]
            webdriver.ActionChains(driver=driver).move_to_element(element).click().perform()
        except Exception as e:
            logger.error(e)

    def selectable_energies(self, driver: webdriver.Chrome):
        raw_elements = driver.find_element(by=By.CSS_SELECTOR, value=".tableau .energywrapper").find_elements(by=By.CSS_SELECTOR, value='.stockitem')
        elements = []
        for raw_element in raw_elements:
            classes = not_none(raw_element.get_attribute("class")).split()
            if "stockitem_unselectable" not in classes:
                elements.append(raw_element)
        return elements
    
    def can_select_energy(self, driver: webdriver.Chrome, action: int):
        return len(SelectEnergy.selectable_energies(self, driver)) > action
    
    def detect_energies_to_discard(self, driver: webdriver.Chrome):
        raw_text = driver.find_element(by=By.CSS_SELECTOR, value="#pagemaintitletext").text
        regex = r".*?([0-9]+).*"
        m = re.match(regex, raw_text)
        if m is None:
            return 1
        else:
            return int(m.group(1))
        
    def selected_energies(self, driver: webdriver.Chrome):
        return driver.find_elements(by=By.CSS_SELECTOR, value='.tableau .energywrapper .stockitem[style*=\"border-width: 3px;\"]')
    
    def unselect_energies(self, driver: webdriver.Chrome):
        driver.execute_script("document.querySelectorAll('.tableau .energywrapper .stockitem[style*=\"border-width: 3px;\"]').forEach(e => e.click())")
    
    def should_select_energy(self, driver: webdriver.Chrome):
        if len(SelectEnergy.selected_energies(self, driver)) > SelectEnergy.detect_energies_to_discard(self, driver):
            SelectEnergy.unselect_energies(self, driver)
        return SelectEnergy.detect_energies_to_discard(self, driver) > len(SelectEnergy.selected_energies(self, driver))