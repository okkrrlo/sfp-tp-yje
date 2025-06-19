class BaseAgent:
    def select_action(self, state):
        """현재 상태에서 액션을 선택하는 함수"""
        raise NotImplementedError

    def update(self, state, action, reward, next_state):
        """학습 업데이트 함수 (보상이 도착했을 때 호출됨)"""
        raise NotImplementedError

    def update_target(self):
        """(선택적) 타겟 네트워크 갱신이 필요한 경우 오버라이드"""
        pass

    def set_params(self, **kwargs):
        """(선택적) 하이퍼파라미터를 설정하는 함수"""
        pass
