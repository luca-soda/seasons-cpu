import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import logging

logger = logging.getLogger(__name__)
blacklisted_actions = ['resetPlayerTurn', 'transmute', 'undo', 'discardEnergy']

MAX_ENERGIES=40
MAX_CARDS_IN_GAME=17
MAX_DICE=3
MAX_GENERAL_ACTIONS=5
MAX_ACTIVABLE_CARDS=17
MAX_PLAYABLE_CARDS=15
MAX_PICKABLE_CARDS=9
MAX_SPLITABLE_CARDS=9
MAX_CRYSTAL=1
MAX_INVOCATION_LEVEL=1
GENERAL_MESSAGE=1
SEASONS=12

state_dim = MAX_CRYSTAL + MAX_INVOCATION_LEVEL + MAX_ENERGIES + MAX_CARDS_IN_GAME + MAX_DICE + MAX_GENERAL_ACTIONS + MAX_ACTIVABLE_CARDS + MAX_PLAYABLE_CARDS + MAX_PICKABLE_CARDS + MAX_SPLITABLE_CARDS + GENERAL_MESSAGE

class Status():
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver

    def energies(self) -> list[str]:
        try: 
            energies = self.driver.find_element(by=By.CSS_SELECTOR, value='.energies').find_elements(by=By.CSS_SELECTOR, value=".stockitem")
            return list(map(lambda energy: energy.value_of_css_property('background-position'), energies))
        except Exception as e:
            logger.error(e)
            return []
    
    def invocation_level(self) -> int:
        try:
            invocation_level = self.driver.find_elements(by=By.CSS_SELECTOR, value=".tinvocationlevel")[1]
            return int(invocation_level.text)
        except Exception as e:
            logger.error(e)
            return 0
    
    def cards_in_game(self) -> list[str]:
        try: 
            cards = self.driver.find_element(by=By.CSS_SELECTOR, value='.underlayer-tableau ~ div').find_elements(by=By.CSS_SELECTOR, value='.tooltipable')
            return list(map(lambda card: card.value_of_css_property('background-position'), cards))
        except Exception as e:
            logger.error(e)
            return []
    
    def dice(self) -> list[str]:
        try: 
            dice = self.driver.find_elements(by=By.CSS_SELECTOR, value="#seasons_dices .die")
            return list(map(lambda die: die.value_of_css_property('background-position'), dice))
        except Exception as e:
            logger.error(e)
            return []
    
    def is_my_turn(self) -> bool:
        DELAY=0.01
        try:
            WebDriverWait(driver=self.driver, timeout=DELAY).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".player-board .avatar_active"))
            )
            return True
        except:
            return False
        
    def general_actions(self) -> list[str]:
        try:
            general_actions = self.driver.find_element(by=By.CSS_SELECTOR, value="#generalactions")
            action_buttons = general_actions.find_elements(by=By.CSS_SELECTOR, value=".action-button")
            f_action_buttons = list(map(lambda button: button.get_dom_attribute('id'), filter(lambda button: button.get_dom_attribute('id') not in blacklisted_actions, action_buttons)))
            return f_action_buttons
        except Exception as e:
            logger.error(e)
            return []
    
    def activable_cards(self) -> list[str]:
        try: 
            cards = self.driver.find_elements(by=By.CSS_SELECTOR, value=".stock-wrapper")[0].find_elements(by=By.CSS_SELECTOR, value=".stockitem")
            activable_cards: list[WebElement] = []
            for card in cards:
                try:
                    card.find_element(by=By.CSS_SELECTOR, value=".cardactivation")
                    activable_cards.append(card)
                except:
                    pass
            return list(map(lambda card: card.value_of_css_property('background-position'), activable_cards))
        except Exception as e:
            logger.error(e)
            return []
        
    def playable_cards(self) -> list[str]:
        try:
            cards = self.driver.find_elements(by=By.CSS_SELECTOR, value=".possibleCard .cardtitle") or []
            return list(map(lambda card: card.value_of_css_property('background-position'), cards))
        except Exception as e:
            logger.error(e)
            return []
        
    def pickable_cards(self) -> list[str]:
        try:
            cards = self.driver.find_elements(by=By.CSS_SELECTOR, value="#choiceCards #choiceCardsStock .stockitem")
            return list(map(lambda card: card.value_of_css_property('background-position'), cards))
        except Exception as e:
            logger.error(e)
            return []
        
    def crystals(self) -> float:
        try:
            crystal = self.driver.find_element(by=By.CSS_SELECTOR, value=".player_score_value")
            return float(crystal.text)
        except Exception as e:
            logger.error(e)
            return 0
        
    def prestige_points(self): 
        try:
            prestige_points = self.driver.find_element(by=By.CSS_SELECTOR, value='.prestige.counter')
            return float(prestige_points.text)
        except Exception as e:
            logger.error(e)
            return 0
        
    def splitable_cards(self) -> list[str]:
        try:
            cards = self.driver.find_elements(by=By.CSS_SELECTOR, value="#player_hand .tooltipable")
            return list(map(lambda card: card.value_of_css_property('background-position'), cards))
        except Exception as e:
            logger.error(e)
            return []
    
    def _background_to_float(self, background: str) -> float: # why not an hash?
        background = background.replace('%','')
        coords = background.split(' ')
        bgtf = float(f'{coords[0].replace('00','')}.{0 if float(coords[1]) > 0 else 1}{coords[1].replace('-','')}')
        return bgtf
    
    def state_padding(self, state_like: list[float], padding: int) -> list[float]:
        for _ in range(padding):
            state_like.append(-99)
        return state_like
    
    def same_state(self, state) -> bool:
        current_state = self.state()
        for i in range(len(state)):
            if state[i] != current_state[i]:
                return False
        return True
    
    def general_message(self) -> str:
        try:
            message = self.driver.find_element(by=By.CSS_SELECTOR, value="#pagemaintitletext")
            return message.text
        except Exception as e:
            return ''
        
    def _general_message_to_hash(self, message: str) -> int:
        return hash(message)
        
    def state(self) -> list[float]:
        energies = self.energies()
        invocation_level = self.invocation_level()
        cards_in_game = self.cards_in_game()
        dice = self.dice()
        general_actions = self.general_actions()
        activable_cards = self.activable_cards()
        playable_cards = self.playable_cards()
        pickable_cards = self.pickable_cards()
        splitable_cards = self.splitable_cards()
        crystals = self.crystals()
        message = self._general_message_to_hash(self.general_message())

        state = []
        state.append(invocation_level)
        state.append(crystals)
        state.append(message)
        for energy in energies[:MAX_ENERGIES]:
            state.append(self._background_to_float(energy))
        state = self.state_padding(state, MAX_ENERGIES - len(energies))
        for card in cards_in_game[:MAX_CARDS_IN_GAME]:
            state.append(self._background_to_float(card))
        state = self.state_padding(state, MAX_CARDS_IN_GAME - len(cards_in_game))
        for die in dice[:3]:
            state.append(self._background_to_float(die))
        state = self.state_padding(state, MAX_DICE - len(dice))
        for action in general_actions[:MAX_GENERAL_ACTIONS]:
            state.append(hash(action))
        state = self.state_padding(state, MAX_GENERAL_ACTIONS - len(general_actions))
        for card in activable_cards[:MAX_ACTIVABLE_CARDS]:
            state.append(self._background_to_float(card))
        state = self.state_padding(state, MAX_ACTIVABLE_CARDS - len(activable_cards))
        for card in playable_cards[:MAX_PLAYABLE_CARDS]:
            state.append(self._background_to_float(card))
        state = self.state_padding(state, MAX_PLAYABLE_CARDS - len(playable_cards))
        for card in pickable_cards[:MAX_PICKABLE_CARDS]:
            state.append(self._background_to_float(card))
        state = self.state_padding(state, MAX_PICKABLE_CARDS - len(pickable_cards))
        for card in splitable_cards[:MAX_SPLITABLE_CARDS]:
            state.append(self._background_to_float(card))
        state = self.state_padding(state, MAX_SPLITABLE_CARDS - len(splitable_cards))
        return state