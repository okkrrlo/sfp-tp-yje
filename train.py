# train.py

import os
import time
import pythoncom

from agent.dqn_agent import DQNAgent
from env.simulation_env import SimulationEnvironment
from buffer.pending_buffer import PendingBuffer
from utils.order_generator import OrderGenerator
from interface.plantsim_interface import PlantsimInterface
from utils.logger import Logger
from config import DEFAULT_HYPERPARAMS, DEFAULT_SIM_PARAMS


def run_training(params, log_callback=None, csv_path=None):
    """
    학습 실행 함수
    :param params: dict 형태의 하이퍼파라미터 설정
    :param log_callback: 로그 출력 함수 (GUI용)
    """
    pythoncom.CoInitialize()  # COM 객체 초기화 (GUI 쓰레드에서 필수)
    
    # 기본값 초기화
    full_params = {**DEFAULT_HYPERPARAMS, **DEFAULT_SIM_PARAMS}
    if params:
        full_params.update(params)

    logger = Logger(gui_callback=log_callback)

    # 인터페이스 및 환경 초기화
    plsim = PlantsimInterface()
    model_file = "tp_v11.spp"
    model_path = os.path.abspath(model_file)
    plsim.initialize_model(model_path)

    env = SimulationEnvironment(plsim)
    state_dim = env.get_state_dim()
    action_dim = env.get_action_dim()

    # DQN 에이전트 초기화
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        gamma=full_params["Gamma"],
        epsilon=full_params["Epsilon"],
        lr=full_params["LearningRate"],
        batch_size=full_params["BatchSize"]
    )

    order_gen = OrderGenerator(csv_path=csv_path) if csv_path else OrderGenerator()
    buffer = PendingBuffer()

    num_episodes = full_params["Episode"]
    T = full_params["OrderInterval"]

    current_order = order_gen.generate_order()
    next_order = order_gen.generate_order()

    for episode in range(num_episodes):
        logger.log_text(f"[Episode {episode + 1}]")

        env.reset_and_initialize(T)
        buffer.clear()
        order_gen.reset()

        while not env.is_terminal() and order_gen.has_next():
            env.register_order(current_order)

            if not env.has_idle_ams():
                env.start_simulation()
                while not env.has_idle_ams() and not env.is_terminal():
                    time.sleep(1)
                env.stop_simulation()

            if env.has_idle_ams():
                state = env.get_state(current_order)
                next_state = env.get_state(next_order)

                action = agent.select_action(state)
                ams_index = action + 1
                env.assign_order(ams_index)

                buffer.add(current_order["order_id"], state, action, next_state)

            env.run_simulation_for_T(T)

            for order_id, reward in env.get_completed_rewards(buffer.keys()):
                item = buffer.pop(order_id)
                if item:
                    agent.remember(item["state"], item["action"], reward, item["next_state"])
                    agent.update()
                    logger.log(episode + 1, order_id, reward)

            current_order = next_order
            if order_gen.has_next():
                next_order = order_gen.generate_order()
            else:
                break  # 다음 오더가 없으면 루프 종료

        agent.update_target()
        logger.log_text(f"  Episode {episode + 1} completed\n")

    # 결과 저장
    model_path = os.path.join(logger.get_save_dir(), "model.pth")
    agent.save_model(model_path)
    logger.save_graph()
    logger.log_text(f"📁 결과 저장 완료 → {logger.get_save_dir()}")

    # 시뮬레이터 종료
    plsim.quit()
