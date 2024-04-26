from collections import deque
from functools import reduce

import numpy as np
import torch, os, math, random
from action_space import ActionSpace
from seasons_interface.seasons_interface import SeasonsInterface
from icecream import ic
from time import sleep
from DQN import FlexibleHierarchicalDQN
from seasons_interface.status import state_dim
import traceback

device = torch.device(os.getenv('DEVICE') or 'cpu')
torch.device(device)

if __name__ == '__main__':
    game = SeasonsInterface()
    action_space = ActionSpace()
    action_space.add_action('general_action', 5, can_act=game.can_click_general_action, act=game.click_general_action, list_items=game.clickable_general_actions)
    action_space.add_action('pick_card', 9, can_act=game.can_pick_card, act=game.pick_card, list_items=game.pickable_cards)
    action_space.add_action('split_card', 9, can_act=game.can_split_card, act=game.split_card, list_items=game.splitable_cards)
    action_space.add_action('pick_die', 3, can_act=game.can_pick_die, act=game.pick_die, list_items=game.pickable_dice)
    action_space.add_action('play_card', 15, can_act=game.can_play_card, act=game.play_card, list_items=game.playable_cards)
    actions_per_group = list(map(lambda action: action.subactions, action_space.actions))
    models = [FlexibleHierarchicalDQN(state_dim, len(action_space.actions), actions_per_group) for _ in range(2)]
    models = [model.to(device) for model in models]
    target_models = [FlexibleHierarchicalDQN(state_dim, len(action_space.actions), actions_per_group) for _ in models]
    optimizers = [torch.optim.Adam(model.parameters()) for model in models]
    replay_buffers = [deque(maxlen=10000) for _ in models]
    epsilon = [1.0 for _ in models]
    min_epsilon = [0.01 for _ in models]
    gamma = [0.999 for _ in models]
    batch_sizes = [32 for _ in models]
    epsilon_decays = [0.999 for _ in models]
    for i in range(2):
        if os.path.exists(os.path.join('models',f'model_{i}.pth')):
            checkpoint = torch.load(os.path.join('models',f'model_{i}.pth'), device) 
            models[i].load_state_dict(checkpoint['model_state_dict'])
            optimizers[i].load_state_dict(checkpoint['optimizer_state_dict'])
        models[i].eval()
    input("Press enter to start the game")
    ic("Game is always alive")
    try:
        while game.is_game_alive():
            player = game.set_next_player()
            state = game.status().state()
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)

            action_group_logits, actions_logits = models[player](state_tensor)
            specific_action_logits = list(filter(lambda action_logit: action_logit is not None, actions_logits))[0]
            if np.random.rand() < epsilon[player]:
                specific_actions_filtered = []
                action_group = 1
                while len(specific_actions_filtered) == 0:
                    action_group = np.random.randint(0, len(action_space.actions))
                    specific_actions_filtered = [sa for sa in range(action_space.actions[action_group].subactions) if action_space.actions[action_group].can_act(sa)]
                specific_action = random.choice(specific_actions_filtered)
            else: 
                action_group = torch.argmax(action_group_logits, dim=-1).to(device).item()
                specific_action = torch.argmax(specific_action_logits, dim=-1).to(device).item()
            prestige_points = game.status().prestige_points()
            crystals = game.status().crystals()
            can_act = action_space.actions[math.floor(action_group)].can_act(math.floor(specific_action))
            ic(action_group, specific_action, can_act)
            if can_act:
                action_space.actions[math.floor(action_group)].act(math.floor(specific_action))
                sleep(0.5)
            else:
                ic("Action not possible")
                continue
            diff_prestige_points = game.status().prestige_points() - prestige_points
            diff_crystals = game.status().crystals() - crystals
            reward = diff_prestige_points + diff_crystals
            if (not can_act):
                reward = -100
            loss_1 = torch.nn.functional.cross_entropy(action_group_logits, torch.tensor([action_group]).to(device))
            loss_2 = torch.nn.functional.cross_entropy(specific_action_logits, torch.tensor([specific_action]).to(device))
            loss = loss_1 + loss_2
            optimizers[player].zero_grad()
            loss.backward()
            optimizers[player].step()
            epsilon[player] = max(min_epsilon[player], epsilon[player] * epsilon_decays[player])
    except Exception as e:
        ic(e)
        traceback.print_exc()
    input("Press enter to close the browser")
    game.close_browsers()