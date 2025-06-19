import os
import tkinter as tk
from gui.dashboard import TrainingDashboard

if __name__ == "__main__":
    root = tk.Tk()
    csv_path = "data/order_table_test.csv"
    app = TrainingDashboard(root, csv_path=csv_path)
    root.mainloop()