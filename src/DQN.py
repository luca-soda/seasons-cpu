import torch, os
import torch.nn as nn
from typing import List
from seasons_interface.status import state_dim


device = torch.device(os.getenv('DEVICE') or 'cpu')
MAX_STATE = state_dim

class FlexibleHierarchicalDQN(nn.Module):
    def __init__(self, num_states: int, num_action_groups: int, num_actions_per_group: List[int]):
        super(FlexibleHierarchicalDQN, self).__init__()
        self.state_reduction: nn.Linear = nn.Linear(num_states, MAX_STATE).to(device)
        self.action_group_decision: nn.Linear = nn.Linear(MAX_STATE, num_action_groups).to(device)
        self.action_decisions: nn.ModuleList = nn.ModuleList([
            nn.Linear(MAX_STATE, num_actions).to(device) for num_actions in num_actions_per_group
        ])

    def forward(self, tensor: torch.Tensor) -> tuple[torch.Tensor, List[torch.Tensor|None]]:
        x: torch.Tensor = torch.relu(self.state_reduction(tensor)).to(device)
        action_group_logits: torch.Tensor = self.action_group_decision(x)
        action_group: torch.Tensor = torch.argmax(action_group_logits, dim=-1).to(device)

        actions_logits: List[torch.Tensor|None] = list(map(lambda _: None, self.action_decisions))
        # Generate logits only for the selected action group
        for idx, linear in enumerate(self.action_decisions):
            if idx == action_group.item():  # Ensure action_group is a scalar
                actions_logits[idx] = linear(x)
        
        return action_group_logits, actions_logits