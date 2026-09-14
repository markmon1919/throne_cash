#!/usr/bin/env .venv/bin/python


import os, pyautogui, time, subprocess
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

colors = {}
for key, value in os.environ.items():
    if key.isupper() and not key.startswith("DB_") and not key.startswith("PROVIDER_"):
        colors[key] = value.encode("utf-8").decode("unicode_escape")

APP_PATH = os.getenv("APP_PATH")
APP_NAME = Path(__file__).resolve().parent.name.replace("_", " ").title()
CRON_USER = os.getenv("USER")
CRON_LOG = os.getenv("CRON_LOG")
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SCREEN_POS = {
    "center_x": SCREEN_WIDTH // 2,
    "center_y": SCREEN_HEIGHT // 2,
    "right_x": SCREEN_WIDTH - 1,
    "bottom_y": SCREEN_HEIGHT - 1
}
CENTER_X, CENTER_Y = SCREEN_POS.get("center_x"), SCREEN_POS.get("center_y")
LEFT_X, RIGHT_X, TOP_Y, BTM_Y = 0, SCREEN_POS.get("right_x"), 0, SCREEN_POS.get("bottom_y")


def launch_app():
    # Open app
    subprocess.run(["open", APP_PATH])
    time.sleep(10)
    # Fullscreen
    subprocess.run([
        "osascript",
        "-e",
        'tell application "System Events" to keystroke "f" using {control down, command down}'
    ])
    time.sleep(5)

def collect_gems():
    # Click location
    pyautogui.click(CENTER_X, BTM_Y - 40)
    time.sleep(2)
    # Click game
    pyautogui.click(CENTER_X - 100, BTM_Y - 300)
    time.sleep(1)
    # Collect gems
    pyautogui.click(CENTER_X + 140, TOP_Y + 365)
    time.sleep(1)

def set_cronjob():
    # Schedule next run 60 minutes from when this script starts
    next_run = datetime.now() + timedelta(minutes=61)
    cron_line = (
        f"{next_run.minute} {next_run.hour} * * * "
        f"cd {Path(__file__).resolve().parent} && ./{Path(__file__).resolve().name} >> {CRON_LOG} 2>&1"
        f"\t# {APP_NAME} Job"
    )

    # Get existing cron jobs
    result = subprocess.run(
        ["sudo", "crontab", "-u", CRON_USER, "-l"],
        capture_output=True,
        text=True
    )
    existing_cron = result.stdout if result.returncode == 0 else ""
    # Remove our previous Throne Cash job
    existing_lines = [
        line for line in existing_cron.splitlines()
        if APP_NAME not in line
    ]
    # Add the new schedule
    existing_lines.append(cron_line)
    new_cron = "\n".join(existing_lines) + "\n"
    # Install updated crontab
    subprocess.run(
        ["sudo", "crontab", "-u", CRON_USER, "-"],
        input=new_cron,
        text=True,
        check=True
    )

    print(
        f"\n{colors['LCYN']}Cron         {colors['WHTE']}:\t{colors['RES']} "
        f"{colors['DGRY']}{cron_line.split('#')[0].rstrip()}\t{colors['RED']}# {APP_NAME}{colors['RES']}\n"
    )
    print(f"{colors['LGRE']}Current time {colors['WHTE']}:\t{colors['RES']} {colors['BYEL']}{datetime.now().strftime('%I')}{colors['BDGRY']}:{colors['BYEL']}{datetime.now().strftime('%M')} {colors['LBLU']}{datetime.now().strftime('%p')} {colors['MAG']}{datetime.now().strftime('%a')}{colors['RES']}")
    print(f"{colors['ORA']}Next run     {colors['WHTE']}:\t{colors['RES']} {colors['BYEL']}{next_run.strftime('%I')}{colors['BDGRY']}:{colors['BYEL']}{next_run.strftime('%M')} {colors['LBLU']}{next_run.strftime('%p')} {colors['MAG']}{next_run.strftime('%a')}{colors['RES']}\n")


if __name__ == "__main__":
    launch_app()
    collect_gems()
    set_cronjob()

    # Close app
    subprocess.run([
        "osascript",
        "-e",
        f'tell application "{APP_NAME}" to quit'
    ])
    