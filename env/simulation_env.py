import time

class SimulationEnvironment:
    """
    Plant Simulation 연동 환경 클래스
    - AMS 상태 조회 및 오더 등록
    - 시뮬레이터 실행 제어
    - 완료된 작업 보상 계산 등 내부 후처리 포함
    """
    def __init__(self, plsimInterface):
        self.plsim = plsimInterface
        self.node_grid = self._create_node_grid()

    def _create_node_grid(self):
        return [
            [None, None, None, "rack1_0", "rack1_1", "rack1_2", "rack1_3", "rack1_4", "rack1_5", "rack1_6", "rack1_7", "rack1_8", "rack1_9", None],
            [None, "home1", "Via13", "via_10", "via_11", "via_12", "via_13", "via_14", "via_15", "via_16", "via_17", "via_18", "via_19", "via_1_12"],
            [None, None, None, "rack2_0", "rack2_1", "rack2_2", "rack2_3", "rack2_4", "rack2_5", "rack2_6", "rack2_7", "rack2_8", "rack2_9",  None],
            ["out", "via15", "via", "rack3_0", "rack3_1", "rack3_2", "rack3_3", "rack3_4", "rack3_5", "rack3_6", "rack3_7", "rack3_8", "rack3_9", "via1"],
            [None, "home2", "via17", "via_20", "via_21", "via_22", "via_23", "via_24", "via_25", "via_26", "via_27", "via_28", "via_29", "via_2_12"],
            [None, None, None, "rack4_0", "rack4_1", "rack4_2", "rack4_3", "rack4_4", "rack4_5", "rack4_6", "rack4_7", "rack4_8", "rack4_9", None]
        ]
    
    def find_node_position_by_name(self, node_name):
        for row in range(len(self.node_grid)):
            for col in range(len(self.node_grid[row])):
                if self.node_grid[row][col] == node_name:
                    return row, col
        return None
    
    def ams_table_to_vector(self, ams_table):
        """AMS 테이블을 벡터 형태로 변환"""
        vector = []
        for (pos, dest, order_num) in ams_table:
            row, col = self.find_node_position_by_name(pos) if pos else (-1, -1)
            dest_row, dest_col = self.find_node_position_by_name(dest) if dest else (-1, -1)
            vector.extend([row, col, dest_row, dest_col, order_num])
        return vector
    
    def order_to_vector(self, order):
        """오더를 벡터로 변환"""
        vector = []
        position_name = f"{order['order_rack']}_{order['order_pos'] % 10}"

        try:
            result = self.find_node_position_by_name(position_name)
            if result is None:
                raise ValueError(f"Position name '{position_name}' not found in map.")
            pos_row, pos_col = result
        except Exception as e:
            raise ValueError(f"Failed to convert order position '{position_name}' to vector: {e}")

        vector.extend([pos_row, pos_col])
        return vector


    def reset_and_initialize(self, T=200):
        """시뮬레이터 초기화"""
        self.plsim.reset_simulation()
        self.plsim.set_T(T)
        self.plsim.start_simulation()
        while not self.plsim.check_simulation_ready():
            time.sleep(1)  # 시뮬레이터가 준비될 때까지 대기
        time.sleep(1)

    def get_state_dim(self):
        """상태 벡터 차원 반환"""
        return self.plsim.get_ams_state_dimension() + 2  # AMS 상태 + 오더 정보 (3개 추가)  

    def get_action_dim(self):
        """행동 공간 크기 반환"""
        return self.plsim.get_action_dimension()

    def register_order(self, order: dict):
        """
        다음 할당을 위해 주문 정보를 내부에 저장
        :param order: {'order_id', 'order_rack', 'order_pos', ...}
        """
        self.current_order = order

    def get_state(self, order):
        """
        AMS 상태와 현재 오더를 모두 벡터 형태로 반환
        """
        ams_table = self.plsim.read_ams_table()
        ams_vec = self.ams_table_to_vector(ams_table)
        if order is None:
            order_vec = self.order_to_vector(self.current_order)
        else:
            order_vec = self.order_to_vector(order)
        return ams_vec + order_vec

    def is_terminal(self) -> bool:
        """시뮬레이션 종료 여부"""
        return self.plsim.check_simulation_ended()

    def start_simulation(self):
        """시뮬레이션 시작"""
        self.plsim.start_simulation()

    def stop_simulation(self):
        """시뮬레이션 종료"""
        self.plsim.stop_simulation()

    def run_simulation_for_T(self, T: float):
        """T초 동안 시뮬레이션 실행"""
        self.plsim.run_simulation_for_T(T)

    def has_idle_ams(self) -> bool:
        """대기 중인 AMS 존재 여부"""
        return self.plsim.check_idle_ams()

    def assign_order(self, ams_index: int):
        """
        저장된 current_order를 AMS에 할당
        :param ams_index: 할당할 AMS 인덱스 (1~num_ams)
        """
        if self.current_order is None:
            raise ValueError("먼저 register_order로 주문을 설정하세요.")
        self.plsim.assign_order(self.current_order, ams_index)
        self.plsim.start_simulation()
        # 할당했으므로 current_order 초기화
        self.current_order = None

    def get_completed_rewards(self, pending_ids) -> list:
        """
        완료된 오더들의 보상 계산 및 반환
        :return: list of tuples (order_id, reward)
        """
        completed = self.plsim.get_completed_orders(pending_ids)  # [(order_id, leadtime), ...]
        rewards = []
        for order_id, leadtime in completed:
            # leadtime이 짧을수록 높은 보상
            reward = -leadtime
            rewards.append((order_id, reward))
        return rewards
