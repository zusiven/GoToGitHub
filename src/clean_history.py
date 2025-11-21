import datetime as dt
from pathlib import Path


def clean_history_data():
    save_dir = "data"
    current_time = dt.datetime.now()
    history_time = current_time - dt.timedelta(days=7)
    # 防止程序运行失败，遗漏删除
    for i in range(299):
        clean_time_str = (history_time - dt.timedelta(days=i)).strftime("%Y_%m_%d")
        clean_path = Path(save_dir, f"{clean_time_str}.txt")
        if clean_path.exists():
            clean_path.unlink()
