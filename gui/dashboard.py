# gui/dashboard.py

import os
import glob
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from PIL import Image, ImageTk
from train import run_training
from config import DEFAULT_HYPERPARAMS, DEFAULT_SIM_PARAMS

class TrainingDashboard:
    def __init__(self, root, csv_path=None):
        self.root = root
        self.root.title("최적 물류 운영 시뮬레이션 컨트롤 패널")
        self.root.geometry("780x700")

        self.csv_path = csv_path
        self.build_hyperparam_section()
        self.build_simulation_section()  # 여기 수정됨
        self.build_log_section()
        self.build_button_section()

    def build_hyperparam_section(self):
        frame = tk.LabelFrame(self.root, text="Hyperparameter 설정")
        frame.pack(padx=10, pady=5, fill="x")

        self.param_entries = {}
        # 모든 하이퍼파라미터를 한 줄(row=0)에 배치
        for i, (key, default) in enumerate(DEFAULT_HYPERPARAMS.items()):
            tk.Label(frame, text=key).grid(row=0, column=i*2, padx=5, pady=5)
            entry = tk.Entry(frame, width=10)
            entry.insert(0, str(default))
            entry.grid(row=0, column=i*2 + 1, padx=5, pady=5)
            self.param_entries[key] = entry

    def build_simulation_section(self):
        frame = tk.LabelFrame(self.root, text="Simulation 설정")
        frame.pack(padx=10, pady=5, fill="x")

        default_interval = DEFAULT_SIM_PARAMS["OrderInterval"]
        tk.Label(frame, text="OrderInterval:").grid(row=0, column=0, padx=5, pady=5)
        entry = tk.Entry(frame, width=10)
        entry.insert(0, str(default_interval))
        entry.grid(row=0, column=1, padx=5, pady=5)
        self.sim_entries = {"OrderInterval": entry}

    def build_log_section(self):
        frame = tk.LabelFrame(self.root, text="Training Logs")
        frame.pack(padx=10, pady=5, fill="both", expand=False)

        self.log_text = tk.Text(frame, height=8)
        self.log_text.pack(fill="both", expand=True)

        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(frame, maximum=100, variable=self.progress_var)
        self.progress_bar.pack(fill="x", pady=5)

    def build_button_section(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Button(frame, text="학습 시작", bg="green", fg="white",
                  font=("Helvetica", 12, "bold"), command=self.start_training)\
            .grid(row=0, column=0, padx=10)
        tk.Button(frame, text="보상 그래프 보기", command=self.show_graph)\
            .grid(row=0, column=1, padx=10)
        tk.Button(frame, text="로그 다운로드", command=lambda: self.download_file("log.txt"))\
            .grid(row=0, column=2, padx=10)
        tk.Button(frame, text="모델 다운로드", command=lambda: self.download_file("model.pth"))\
            .grid(row=0, column=3, padx=10)

        self.graph_frame = tk.LabelFrame(self.root, text="Reward Graph", height=400)
        self.graph_frame.pack(padx=10, pady=5, fill="both", expand=True)

    def append_log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def start_training(self):
        params = {**DEFAULT_HYPERPARAMS, **DEFAULT_SIM_PARAMS}
        # 하이퍼파라미터 덮어쓰기
        for key, entry in self.param_entries.items():
            v = entry.get()
            params[key] = float(v) if "." in v else int(v)
        # 시뮬레이션 파라미터 덮어쓰기 (OrderInterval만)
        params["OrderInterval"] = int(self.sim_entries["OrderInterval"].get())

        self.append_log("학습을 시작합니다...\n")
        self.progress_var.set(0)
        self.log_text.delete("1.0", tk.END)

        Thread(
            target=lambda: run_training(params, log_callback=self.append_log, csv_path=self.csv_path),
            daemon=True
        ).start()

    def show_graph(self):
        for w in self.graph_frame.winfo_children():
            w.destroy()
        try:
            folders = sorted(glob.glob("results/*"), key=os.path.getmtime, reverse=True)
            for folder in folders:
                img_path = os.path.join(folder, "reward_graph.png")
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img = img.resize((600, 300), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    lbl = tk.Label(self.graph_frame, image=photo)
                    lbl.image = photo
                    lbl.pack(fill="both", expand=True)
                    return
            self.append_log("⚠ 그래프 이미지가 존재하지 않습니다.")
        except Exception as e:
            self.append_log(f"⚠ 그래프 표시 실패: {e}")

    def download_file(self, filename):
        try:
            folders = sorted(glob.glob("results/*"), key=os.path.getmtime, reverse=True)
            if not folders:
                self.append_log("⚠ 저장된 결과 폴더가 없습니다.")
                return
            src = os.path.join(folders[0], filename)
            if not os.path.exists(src):
                self.append_log(f"⚠ {filename} 파일이 존재하지 않습니다.")
                return
            dst = filedialog.asksaveasfilename(defaultextension=os.path.splitext(filename)[1],
                                               initialfile=filename)
            if dst:
                shutil.copy(src, dst)
                messagebox.showinfo("저장 완료", f"{filename} 저장 완료!")
        except Exception as e:
            self.append_log(f"⚠ 파일 저장 중 오류: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingDashboard(root, csv_path="data/order_table.csv")
    root.mainloop()
