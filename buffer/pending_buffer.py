from typing import Optional, Dict

class PendingBuffer:
    """
    SMDP 지연 보상 처리를 위한 버퍼 클래스.
    작업(order_id)이 완료될 때까지 관련 정보를 저장하며,
    완료 시 보상 학습에 활용됩니다.
    """
    def __init__(self):
        # order_id를 키로, 값은 dict(state, action, start_time 등)
        self._buffer: dict[str, dict] = {}

    def add(self, order_id: str, state: list[float], action: int, next_state: list[float]):
        """
        작업 시작 시 상태 및 행동을 버퍼에 추가합니다.

        :param order_id: 작업 식별자
        :param state: 상태 벡터 (수치형 리스트)
        :param action: 선택된 행동 인덱스
        :param start_time: 작업 시작 시각 (선택적)
        """
        self._buffer[order_id] = {
            "state": state,
            "action": action,
            "next_state": next_state
        }

    # def pop(self, order_id: str) -> dict | None:
    #     """
    #     완료된 작업에 대한 정보를 반환하고 버퍼에서 제거합니다.

    #     :param order_id: 완료된 작업 식별자
    #     :return: {"state": ..., "action": ..., "start_time": ...} or None
    #     """
    #     return self._buffer.pop(order_id, None)
    
    
    def pop(self, order_id: str) -> Optional[Dict]:
        return self._buffer.pop(order_id, None)

    def clear(self) -> None:
        """
        버퍼를 모두 초기화합니다. (에피소드 재시작 시 사용)
        """
        self._buffer.clear()

    def __len__(self) -> int:
        """
        현재 버퍼에 남아 있는 작업 수를 반환합니다.
        """
        return len(self._buffer)
    
    def keys(self):
        return self._buffer.keys()