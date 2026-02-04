
import re

def generate_table():
    input_file = "verification_full_period.txt"
    
    print("| 分析基準日 | 翌日の実際の結果 | 予測結果 | 判定 |")
    print("| :--- | :--- | :--- | :--- |")
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(input_file, "r", encoding="cp932") as f:
             lines = f.readlines()
             
    # Regex to capture the table rows from the text output
    # Format: 2026-02-03   | +4.0% (Surge)        | 底堅い/反発                         | ⭕ Success
    row_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+\|\s+(.*?)\s+\|\s+(.*?)\s+\|\s+(.*)$")
    
    rows = []
    for line in lines:
        match = row_pattern.match(line.strip())
        if match:
            date, actual, pred, result = match.groups()
            
            # Formatting for Markdown
            # Highlight Significant Moves
            actual = actual.strip()
            pred = pred.strip()
            result = result.strip()
            
            is_surge_crash = "Surge" in actual or "Crash" in actual
            
            date_md = f"**{date}**" if is_surge_crash else date
            actual_md = f"**{actual}**" if is_surge_crash else actual
            
            # Highlight Prediction if it matches significantly
            pred_md = f"**{pred}**" if "加速" in pred or "反発" in pred and is_surge_crash else pred
            
            # Result Icon
            if "Success" in result:
                result_md = "⭕ **成功**"
                if "大成功" in result or is_surge_crash:
                     result_md = "⭕ **成功**"
                if "Quiet" in result:
                     result_md = "⭕ 成功 (静観)"
            elif "Missed" in result:
                result_md = "⚠️ 失敗 (検知漏れ)"
            elif "False Alarm" in result:
                result_md = "❌ 失敗 (ダマシ/過敏)"
            elif "Wrong Dir" in result:
                result_md = "❌ 失敗 (逆行)"
            else:
                result_md = result

            rows.append(f"| {date_md} | {actual_md} | {pred_md} | {result_md} |")

    # Sort by date descending (newest first)
    rows.sort(reverse=True)
    
    for row in rows:
        print(row)

if __name__ == "__main__":
    generate_table()
