import os
from datetime import datetime
import matplotlib.pyplot as plt

class Logger:
    def __init__(self, gui_callback=None):
        self.rewards = []
        self.logs = []
        self.gui_callback = gui_callback

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_dir = os.path.join("results", now)
        os.makedirs(self.save_dir, exist_ok=True)

        self.log_path = os.path.join(self.save_dir, "log.txt")
        with open(self.log_path, "w") as f:
            f.write("Episode,OrderID,Reward\n")

    def log(self, episode, order_id, reward):
        self.rewards.append(reward)

        with open(self.log_path, "a") as f:
            f.write(f"{episode},{order_id},{reward}\n")

    def log_text(self, message: str):
        print(message)
        if self.gui_callback:
            self.gui_callback(message)

    def save_graph(self):
        if not self.rewards:
            return

        filepath = os.path.join(self.save_dir, "reward_graph.png")
        plt.figure(figsize=(6, 3))
        plt.plot(self.rewards)
        plt.xlabel("Step")
        plt.ylabel("Reward")
        plt.title("Training Reward")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()

    def get_save_dir(self):
        return self.save_dir
