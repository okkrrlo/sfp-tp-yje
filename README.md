### 2025 스마트팩토리응용프로그래밍-termproject - 유주은, 이도윤

# 물류 설비 운영 최적화를 위한 강화학습-시뮬레이션 환경 구축


## 프로젝트 개요
강화학습(DQN) 에이전트와 Plant Simulation 연동 시뮬레이션 환경을 구성하여  
동적 스케줄링 최적화 환경을 구축합니다.

## 주요 개발 내용
- 강화학습(DQN) 에이전트  
- 강화학습 환경  
- Plant Simulation–강화학습 인터페이스  
- Plant Simulation 원격 제어용 COM 인터페이스  
- Tkinter 기반 학습 대시보드  

## 상세 모듈 요약
1. **agent/**  
   - `dqn_agent.py`  
   - 네트워크 정의, 행동 선택 정책, 파라미터 업데이트 로직 포함

2. **env/**  
   - `simulation_env.py`  
   - `reset()`, `step()`, 상태 추출, 보상 수집 등 학습 환경 제공

3. **buffer/**  
   - `pending_buffer.py`, `replay_buffer.py`  
   - 학습 시 필요한 데이터 저장 및 관리 버퍼

4. **interface/** & **plantsim/**  
   - Plant Simulation 원격 제어용 COM 인터페이스 래퍼  
   - 모델 파일 로드, 시뮬레이션 실행/중지, 변수 조회/설정 등 제어 기능

5. **gui/**  
   - `dashboard.py`  
   - Tkinter 기반 대시보드 (하이퍼파라미터 입력, 학습 시작, 보상 그래프 시각화)

6. **utils/**  
   - `logger.py`, `order_generator.py`  
   - 오더 생성기, 로거 등 부가 유틸리티

7. **train.py**  
   - 전체 학습 루프 실행 스크립트 (에피소드 순환, 오더 발생 주기 조절 등)

8. **main.py**  
   - GUI 애플리케이션 엔트리 포인트 (Tkinter 메인 루프 실행)

9. **config.py**  
   - 학습 하이퍼파라미터 (`DEFAULT_HYPERPARAMS`) 및 시뮬레이션 파라미터 (`DEFAULT_SIM_PARAMS`)

10. **data/**  
    - 오더 테이블(input_data) 보관

11. **results/**  
    - 학습 중 생성된 로그, 리워드 곡선, 학습된 모델 등 결과물 저장소

12. **.gitignore**  
    - `__pycache__/`, `.bak` 등 불필요 파일 제외 설정

## 사용방법

### 1. 학습 실행
```bash
python train.py --episodes 100 --interval 200
```
### 2. 대시보드 실행
```bash
python gui/dashboard.py
```
