import subprocess
import os
import sys

work_dir = r"e:\作\比赛\计算机设计大赛\career-planner（ai+职测）\career-planner"
python_path = os.path.join(work_dir, ".venv", "Scripts", "python.exe")
app_path = os.path.join(work_dir, "app.py")

os.chdir(work_dir)

proc = subprocess.Popen(
    [python_path, "-m", "streamlit", "run", "app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

for line in proc.stdout:
    print(line, end='')