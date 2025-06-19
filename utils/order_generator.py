import pandas as pd
import random

class OrderGenerator:
    def __init__(self, csv_path="data/order_table.csv", seed=None):
        self.order_table = pd.read_csv(csv_path)
        self.available_indices = list(self.order_table.index)

        if seed is not None:
            random.seed(seed)

        random.shuffle(self.available_indices)

    def generate_order(self):
        if not self.available_indices:
            raise Exception("All orders have been used.")

        idx = self.available_indices.pop()
        row = self.order_table.loc[idx]

        return {
            "order_id": row["wip_id"],
            "order_rack": row["order_rack"],       # 문자열 그대로 사용
            "order_pos": row["order_pos"]     # 정수 그대로 사용
        }

    def reset(self):
        self.available_indices = list(self.order_table.index)
        random.shuffle(self.available_indices)

    def has_next(self):
        return bool(self.available_indices)