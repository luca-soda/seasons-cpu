from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from yarg import get
from seasons_interface.pick_card import PickCard
from seasons_interface.general_action import GeneralAction
from seasons_interface.split_card import SplitCard
from seasons_interface.pick_die import PickDie
from dotenv import load_dotenv
from os import getenv
from time import sleep
from icecream import ic
import logging

from seasons_interface.status import Status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class SeasonsInterface(PickCard, GeneralAction, SplitCard, PickDie):
    services: list[Service] = []
    drivers: list[webdriver.Chrome] = []
    player: int = 0
    statuses: list[Status] = []

    def is_game_alive(self):
        return True

    def launch_browser(self):
        service = Service(getenv("CHROME_DRIVER_PATH")) # type: ignore
        service.start()
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)
        return service, driver
    
    def close_browsers(self):
        for driver in self.drivers:
            driver.quit()
        for service in self.services:
            service.stop()

    def login(self, driver: webdriver.Chrome, username: str, password: str):
        driver.get('https://en.boardgamearena.com/account')
        username_input = WebDriverWait(driver=driver, timeout=30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#username_input"))
        )
        username_input.send_keys(username)
        driver.find_element(by=By.CSS_SELECTOR, value="#password_input").send_keys(password)
        driver.find_element(by=By.CSS_SELECTOR, value="#submit_login_button").click()
        WebDriverWait(driver=driver, timeout=30).until(
            EC.url_changes('https://en.boardgamearena.com/account')
        )

    def __init__(self):
        if getenv("TRAINING_USERNAME") is None:
            logger.error("Single player mode not implemented yet. Exiting.")
            raise NotImplementedError()
        else:
            self.training_mode()

    def training_mode(self):
        usernames = [getenv("USERNAME"), getenv("TRAINING_USERNAME")]
        passwords = [getenv("PASSWORD"), getenv("TRAINING_PASSWORD")]
        for _ in range(len(usernames)):
            service, driver = self.launch_browser()
            self.services.append(service)
            self.drivers.append(driver)
        for i, driver in enumerate(self.drivers):
            self.login(driver, usernames[i], passwords[i]) # type: ignore
        if getenv('LOGIN_ONLY') != '':
            ic(getenv('LOGIN_ONLY'))
        elif getenv('GAME_URL') != '':
            ic(getenv('GAME_URL'))
            self.load_game(self.drivers[0], getenv('GAME_URL')) # type: ignore
            self.load_game(self.drivers[1], getenv('GAME_URL')) # type: ignore
        else:
            ic('Creating game')
            url = self.create_game(self.drivers[0])
            self.join_game(self.drivers[1], url)
            self.join_game(self.drivers[0], url)
        self.statuses.append(Status(self.drivers[0]))
        self.statuses.append(Status(self.drivers[1]))

    def create_game(self, driver: webdriver.Remote):
        TIME_BETWEEN_ACTIONS = 0.5
        driver.get('https://boardgamearena.com/lobby')
        driver.find_element(by=By.CSS_SELECTOR, value="#pageheader_mobile_switcher_gamemode").click()
        sleep(TIME_BETWEEN_ACTIONS)
        driver.find_element(by=By.CSS_SELECTOR, value="#pageheader_simple").click()
        sleep(TIME_BETWEEN_ACTIONS)
        driver.find_element(by=By.CSS_SELECTOR, value="#pageheader_mobile_switcher").click()
        sleep(TIME_BETWEEN_ACTIONS)
        driver.find_element(by=By.CSS_SELECTOR, value="#pageheader_async").click()
        sleep(TIME_BETWEEN_ACTIONS)
        driver.find_element(by=By.CSS_SELECTOR, value="#mobile_switcher_firstline_lobbymode").click()
        sleep(TIME_BETWEEN_ACTIONS)
        driver.find_element(by=By.CSS_SELECTOR, value="#pageheader_friends").click()
        sleep(TIME_BETWEEN_ACTIONS)
        driver.find_element(by=By.CSS_SELECTOR, value=".wannaplayauto_play_zone").click()
        WebDriverWait(driver=driver, timeout=30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#gameoption_100_input"))
        )
        driver.find_element(by=By.CSS_SELECTOR, value="#gameoption_100_input").click()
        driver.find_elements(by=By.CSS_SELECTOR, value="#gameoption_100_input option")[2].click()
        return driver.current_url
        
    def join_game(self, driver: webdriver.Remote, url: str):
        if (driver.current_url != url):
            driver.get(url)
            WebDriverWait(driver=driver, timeout=30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#join_game"))
            )
            driver.find_element(by=By.CSS_SELECTOR, value="#join_game").click()
            try: 
                WebDriverWait(driver=driver, timeout=5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#join_confirm"))
                )
                driver.find_element(by=By.CSS_SELECTOR, value="#join_confirm").click()
            except:
                pass
        WebDriverWait(driver=driver, timeout=30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#access_game_normal"))
        )
        driver.find_element(by=By.CSS_SELECTOR, value="#access_game_normal").click()

    def is_my_turn(self) -> bool:
        DELAY = 0.01
        try:
            WebDriverWait(driver=self.drivers[self.player], timeout=DELAY).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".player-board .avatar_active"))
            )
            return True
        except:
            return False
        
    def set_next_player(self):
        if not self.is_my_turn():
            self.player = self.player + 1 % 2
        return self.player
   
    def load_game(self, driver: webdriver.Remote, url: str):
        driver.get(url)

    def set_player(self, player: int):
        self.player = player
        return self
    
    def status(self):
        return self.statuses[self.player]
    
    def can_pick_card(self, action: int):
        return super().can_pick_card(self.drivers[self.player], action)
    
    def pick_card(self, action: int):
        return super().pick_card(self.drivers[self.player], action)
    
    def pickable_cards(self):
        return super().pickable_cards(self.drivers[self.player])
    
    def clickable_general_actions(self):
        return super().clickable_general_actions(self.drivers[self.player])
    
    def click_general_action(self, action: int):
        return super().click_general_action(self.drivers[self.player], action)
    
    def can_click_general_action(self, action: int):
        return super().can_click_general_action(self.drivers[self.player], action)
    
    def can_split_card(self, action: int):
        return super().can_split_card(self.drivers[self.player], action)
    
    def split_card(self, action: int):
        return super().split_card(self.drivers[self.player], action)
    
    def splitable_cards(self):
        return super().splittable_cards(self.drivers[self.player])
    
    def pickable_dice(self):
        return super().pickable_dice(self.drivers[self.player])
    
    def pick_die(self, action: int):
        return super().pick_die(self.drivers[self.player], action)
    
    def can_pick_die(self, action: int):
        return super().can_pick_die(self.drivers[self.player], action)
