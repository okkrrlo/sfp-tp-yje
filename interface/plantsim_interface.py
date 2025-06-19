from plantsim.plantsim import Plantsim
import time
from config import DEFAULT_SIM_PARAMS

class PlantsimInterface:
    def __init__(self, version='24.4', visible=True, trust_model=True, license_type='Educational'):
        self.plantsim = Plantsim(version=version, visible=True, license_type=license_type)

    # ─── Initialization ───

    def initialize_model(self, model_path):
        self.plantsim.load_model(model_path)
        self.plantsim.set_path_context(".Models.Model")
        self.plantsim.set_event_controller()
        self.plantsim.set_value("Eventcontroller.RealtimeScale", DEFAULT_SIM_PARAMS.get("RealtimeScale"))
        self.plantsim.reset_simulation()
        self.num_ams = self.plantsim.get_value("AGVPool.Amount")

    def set_T(self, T):
        self.plantsim.set_value("T", T)
        self.plantsim.execute_simtalk("set_T")

    # ─── Simulation Control ───
    def check_simulation_ready(self):
        return self.plantsim.get_value("simul_ready") == True

    def reset_simulation(self):
        if not self.plantsim.event_controller:
            raise Exception('Event controller not set.')
        self.plantsim.reset_simulation()

    def start_simulation(self):
        if not self.plantsim.event_controller:
            raise Exception('Event controller not set.')
        self.plantsim.start_simulation()

    def run_simulation_for_T(self, T=200):
        if not self.plantsim.event_controller:
            raise Exception('Event controller not set.')
        self.plantsim.set_value("plsim_ready", True)
        while self.plantsim.get_value("request_order") != True:
            time.sleep(1)  # 잠시 대기하여 값이 반영되도록 함        
        time.sleep(1)  # 시뮬레이션이 시작되기 전에 잠시 대기

    def quit(self):
        self.plantsim.quit()

    def stop_simulation(self):
        self.plantsim.execute_simtalk("eventcontroller.stop")

    # ─── State & Action Interface ───

    def get_ams_state_dimension(self):
        return self.num_ams * 5  # pos_row, pos_col, order_num, dest_row, dest_col

    def get_action_dimension(self):
        return self.num_ams

    def read_ams_table(self):
        result = []
        self.plantsim.execute_simtalk("get_state")
        for i in range(1, self.num_ams + 1):
            pos = self.plantsim.get_value(f'AMS_tbl["current_pos", {i}]')
            dest = self.plantsim.get_value(f'AMS_tbl["destination", {i}]')
            order_num = self.plantsim.get_value(f'AMS_tbl["order_num", {i}]')
            result.append((pos, dest, order_num))
        return result

    def assign_order(self, order, ams_index):
        rack = order["order_rack"]
        pos = order["order_pos"]
        self.plantsim.set_value("OrderRack", rack)
        self.plantsim.set_value("OrderPos", pos)
        self.plantsim.set_value("AMSID", ams_index)
        self.plantsim.execute_simtalk("assign_order")

    def check_idle_ams(self):
        self.plantsim.execute_simtalk("get_state")
        for i in range(1, self.num_ams + 1):
            order_num = self.plantsim.get_value(f'AMS_tbl["order_num", {i}]')
            if order_num < 1:
                return True
        return False

    def check_simulation_ended(self):
        return self.plantsim.get_value("isDone") == True

    def get_completed_orders(self, pending_ids: list) -> list:
        completed = []
        for order_id in pending_ids:
            self.plantsim.set_value("orderID_B", order_id)
            leadtime = self.plantsim.execute_simtalk("get_result")
            while self.plantsim.get_value("leadtime") == 0:
                time.sleep(1)
            leadtime = self.plantsim.get_value("leadtime")
            if leadtime != -1:
                completed.append((order_id, leadtime))
            self.plantsim.set_value("leadtime", 0)
        return completed
