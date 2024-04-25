from typing import Callable
from selenium.webdriver.remote.webelement import WebElement
from functools import partial

class Action:
    def __init__(self, action_name: str, subactions: int, can_act, act, list_items):
        self.action_name = action_name
        self.subactions = subactions
        self.can_act = can_act
        self.act = act
        self.list_items = list_items

class ActionSpace:
    actions: list[Action] = []

    def add_action(self, action_name: str, subactions: int, can_act: Callable[[int], bool], act: Callable[[int], None], list_items: Callable[[], list[WebElement]]) -> None:
        action = Action(action_name, subactions, can_act=can_act, act=act, list_items=list_items)
        self.actions.append(action)