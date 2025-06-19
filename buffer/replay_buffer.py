import random
import numpy as np
from collections import deque

class ReplayBuffer:
    def __init__(self, capacity: int):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state):
        """
        buffer에 transition 저장
        :param state: 현재 상태
        :param action: 수행한 행동
        :param reward: 보상
        :param next_state: 다음 상태
        """
        self.buffer.append((state, action, reward, next_state))

    def sample(self, batch_size: int):
        """
        무작위로 batch_size 만큼 샘플링
        :return: (states, actions, rewards, next_states)
        """
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states = zip(*batch)
        return states, actions, rewards, next_states

    def __len__(self):
        return len(self.buffer)