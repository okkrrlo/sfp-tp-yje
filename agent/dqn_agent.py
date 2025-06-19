from config import DEFAULT_HYPERPARAMS
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random
from buffer.replay_buffer import ReplayBuffer

# QNetwork: Q값을 추정하는 심층 신경망
class QNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.out = nn.Linear(128, action_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.out(x)

# DQN 에이전트 정의
class DQNAgent:
    def __init__(self, state_dim, action_dim,
                 gamma=DEFAULT_HYPERPARAMS["Gamma"],
                 epsilon=DEFAULT_HYPERPARAMS["Epsilon"],
                 lr=DEFAULT_HYPERPARAMS["LearningRate"],
                 memory_capacity=10000, batch_size=DEFAULT_HYPERPARAMS["BatchSize"],
                 target_update_freq=1000):
        """
        :param state_dim: 상태 벡터 차원
        :param action_dim: 행동 공간 크기
        :param gamma: 할인율
        :param epsilon: 탐험 확률
        :param lr: 학습률
        :param memory_capacity: replay buffer 용량
        :param batch_size: 배치 학습 크기
        :param target_update_freq: 타겟 네트워크 업데이트 주기 (스텝 기준)
        """
        # 네트워크 및 옵티마이저 초기화
        self.q_net = QNetwork(state_dim, action_dim)
        self.target_net = QNetwork(state_dim, action_dim)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)

        # Replay Buffer
        self.memory = ReplayBuffer(memory_capacity)
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.learn_step_counter = 0

        # 하이퍼파라미터
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon

    def set_params(self, gamma=None, epsilon=None, lr=None):
        """하이퍼파라미터 동적 설정"""
        if gamma is not None:
            self.gamma = gamma
        if epsilon is not None:
            self.epsilon = epsilon
        if lr is not None:
            self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)

    def select_action(self, state):
        """
        ε-greedy로 행동 선택
        :param state: 상태 벡터 (list or np.array)
        :return: 선택된 행동 인덱스
        """
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q_values = self.q_net(state_tensor)
        return q_values.argmax().item()

    def remember(self, state, action, reward, next_state):
        """replay buffer에 transition 저장"""
        self.memory.push(state, action, reward, next_state)

    def update(self):
        """batch 학습: replay buffer에서 샘플링 후 네트워크 업데이트"""
        if len(self.memory) < self.batch_size:
            return
        states, actions, rewards, next_states = self.memory.sample(self.batch_size)
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions).unsqueeze(1)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)

        # 현재 Q값
        q_values = self.q_net(states).gather(1, actions).squeeze()
        # 타겟 Q값
        with torch.no_grad():
            max_next_q = self.target_net(next_states).max(1)[0]
            target_q = rewards + self.gamma * max_next_q

        loss = F.mse_loss(q_values, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # 타겟 네트워크 동기화
        self.learn_step_counter += 1
        if self.learn_step_counter % self.target_update_freq == 0:
            self.update_target()

    def update_target(self):
        """타겟 네트워크 파라미터 동기화"""
        self.target_net.load_state_dict(self.q_net.state_dict())

    def save_model(self, filepath):
        torch.save(self.q_net.state_dict(), filepath)
