from flask import Flask, render_template, request
import pandas as pd
import  google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import markdown2

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not found in .env file. AI features will be disabled.")
else:
    genai.configure(api_key=api_key)

app = Flask(__name__)

exercise_data = {
    '上肢肌力': ['啞鈴臥推', '啞鈴肩推', '啞鈴划船', '引體向上', '伏地挺身'],
    '上肢爆發': ['啞鈴推舉', '啞鈴快肩推', '藥球砸地', '擊掌伏地挺身'],
    '下肢肌力': ['啞鈴聖杯深蹲', '啞鈴硬舉', '槓鈴硬舉', '分腿蹲', '臀推'],
    '下肢爆發': ['深蹲跳', '箱跳', '抓舉跳', '立定跳遠'],
    '核心肌群': ['平板支撐', '俄羅斯轉體', '仰臥起坐', '捲腹'],
    '有氧運動': ['跑步機', '飛輪', '游泳', '跳繩', '橢圓機']
}
exercise_types = list(exercise_data.keys())

def calculate_training_metrics(items_with_load):
    # Filter items that have a valid 'item_load' and 'rpe' for monotony calculation
    valid_items_for_metrics = [
        item for item in items_with_load if item.get('item_load') is not None and item.get('rpe') is not None
    ]
    
    if not valid_items_for_metrics:
        return {
            'weekly_workout_summary': 0,
            'training_load': 0,
            'training_monotony': 0,
            'training_strain': 0,
            'analysis': '無有效數據可分析 (分鐘與RPE為必填)'
        }
    
    # NEW: Training Load (TL) is sum of individual item_loads (minutes * RPE)
    training_load = sum(item['item_load'] for item in valid_items_for_metrics)
    
    # Weekly Workout Summary (WWS)
    weekly_workout_summary = training_load / len(valid_items_for_metrics) if valid_items_for_metrics else 0
    
    # Training Monotony (TM) - still based on RPE
    rpe_values = [item['rpe'] for item in valid_items_for_metrics]
    mean_rpe = pd.Series(rpe_values).mean() if rpe_values else 0
    std_rpe = pd.Series(rpe_values).std() if rpe_values else 0
    training_monotony = std_rpe / mean_rpe if mean_rpe > 0 else 0
    
    # Training Strain (TS)
    training_strain = training_load * training_monotony
    
    analysis = []
    # Note: Thresholds for WWS and TS will need significant adjustment 
    # because the Training Load calculation has fundamentally changed.
    # The old TL was RPE * (sets or mins/5). New TL is RPE * total_minutes_for_exercise.
    # So, if an exercise took 30 mins with RPE 7, load is 210. Previously it might have been 7*6=42 or 7*3=21.
    # These thresholds are illustrative and NEED RECALIBRATION.
    if weekly_workout_summary > 100: # Example: if average item load is high
        analysis.append("週間平均單項訓練量高，若恢復良好可持續！")
    elif weekly_workout_summary > 0 and weekly_workout_summary < 30: 
        analysis.append("週間平均單項訓練量偏低，建議增加訓練強度(RPE)或時長。")
    
    if training_monotony > 0 and training_monotony < 0.8:
        analysis.append("訓練同質性良好，課表變化適中。")
    elif training_monotony > 1.5:
        analysis.append("訓練同質性偏高，建議調整課表增加變化以避免單調和潛在傷害風險。")
    
    if training_strain > 3000: # Example: TS can be much higher now
        analysis.append("訓練張力值偏高，注意避免過度訓練，確保充足休息與恢復。")
    elif training_strain > 0 and training_strain < 800: 
        analysis.append("訓練張力值偏低，若目標為提升，可考慮逐步提升總訓練量。")
    
    return {
        'weekly_workout_summary': round(weekly_workout_summary, 2),
        'training_load': round(training_load, 2),
        'training_monotony': round(training_monotony, 2),
        'training_strain': round(training_strain, 2),
        'analysis': " ".join(analysis) if analysis else "訓練數據正常，繼續保持！請結合自身感受調整。"
    }

def format_items_for_ai(items_with_details):
    log_entries = []
    for item in items_with_details:
        details_parts = [
            f"類別: {item['name']}",
            f"動作: {item['action']}",
            f"總時長: {item.get('minutes', 'N/A')} 分鐘",
            f"RPE: {item.get('rpe', 'N/A')}",
            f"單項訓練量(分鐘*RPE): {item.get('item_load', 'N/A')}"
        ]
        if item['type'] != '有氧運動':
            details_parts.extend([
                f"組數: {item.get('sets', 'N/A')}",
                f"次數: {item.get('reps', 'N/A')}",
                f"重量: {item.get('weight', 'N/A')}"
            ])
        log_entries.append("- " + ", ".join(details_parts))
    return "\n".join(log_entries)

def get_ai_recommendations(workout_log_str, original_items):
    if not api_key:
        return [], "AI服務未配置API金鑰，無法提供建議。"

    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    作為一名專業的健身教練，請分析以下這名使用者的訓練日誌。
    日誌中，「單項訓練量」的計算方式為「總時長 (分鐘) * RPE」。

    --- 訓練日誌開始 ---
    {workout_log_str}
    --- 訓練日誌結束 ---

    根據這份日誌，請提供一份調整後的訓練計畫和詳細的調整原因。
    你的目標是優化訓練效果、促進恢復、預防傷害，並使訓練更具多樣性或針對性。

    請以JSON格式回應，包含兩個頂層鍵：'adjusted_schedule' 和 'explanation'。

    1. 'adjusted_schedule' 應該是一個列表 (list)，每個元素是一個字典 (dict)，代表一個調整後的運動項目。
       每個運動項目字典應包含以下鍵：
       - 'name': (字串) 運動類別。
       - 'action': (字串) 具體動作。
       - 'is_aerobic': (布林值) true 代表有氧運動, false 代表無氧運動。
       - 'adjusted_sets': (字串) 調整後的組數。如果是非有氧運動且有調整，格式為 "新值 (原為: 舊值)"，否則為 "新值" 或 "N/A"。
       - 'adjusted_reps': (字串) 調整後的每組次數。如果是非有氧運動且有調整，格式為 "新值 (原為: 舊值)"，否則為 "新值" 或 "N/A"。
       - 'adjusted_weight': (字串) 調整後的重量。如果是非有氧運動且有調整，格式為 "新值 (原為: 舊值)"，否則為 "新值" 或 "N/A"。
       - 'adjusted_minutes': (字串) 調整後的總時長(分鐘)。如有調整，格式為 "新值 (原為: 舊值)"，否則為 "新值"。
       - 'adjusted_rpe': (字串) 調整後的RPE。如有調整，格式為 "新值 (原為: 舊值)"，否則為 "新值"。

    2. 'explanation': (字串) 對於為何進行這些調整的整體說明。請解釋你的思考過程。

    重要提示：
    - 對於有調整的欄位，請務必使用 "新值 (原為: 舊值)" 格式。如果無調整，只顯示新值。
    - 如果某個欄位不適用於該運動類型 (例如有氧運動的組數)，請填寫 "N/A"。
    - `original_items` 列表中的原始數據 (在 Python 端提供，這裡僅作概念說明) 可用於生成 "(原為: 舊值)"。
      模型應從 `workout_log_str` 推斷原始值。
    - 如果你決定新增或刪除項目，請在 'explanation' 中明確說明。'adjusted_schedule' 應反映最終的建議課表。

    範例 'adjusted_schedule' 項目 (非有氧):
    {{
        "name": "上肢肌力",
        "action": "啞鈴臥推",
        "is_aerobic": false,
        "adjusted_sets": "4 (原為: 3)",
        "adjusted_reps": "8-10 (原為: 10-12)",
        "adjusted_weight": "12kg (原為: 10kg)",
        "adjusted_minutes": "20 (原為: 15)",
        "adjusted_rpe": "7 (原為: 8)"
    }}
    範例 'adjusted_schedule' 項目 (有氧):
    {{
        "name": "有氧運動",
        "action": "跑步機",
        "is_aerobic": true,
        "adjusted_sets": "N/A",
        "adjusted_reps": "N/A",
        "adjusted_weight": "N/A",
        "adjusted_minutes": "35 (原為: 30)",
        "adjusted_rpe": "6 (原為: 7)"
    }}
    請確保 JSON 格式完全正確且可以直接解析。
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response_text = response.text.strip()
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]
        
        ai_data = json.loads(cleaned_response_text.strip())
        
        if not isinstance(ai_data, dict) or \
           'adjusted_schedule' not in ai_data or \
           'explanation' not in ai_data or \
           not isinstance(ai_data['adjusted_schedule'], list):
            print("AI response structure is invalid.")
            return [], "AI回應的資料結構不正確。"

        for item in ai_data['adjusted_schedule']:
            required_keys = ['name', 'action', 'is_aerobic', 'adjusted_sets', 'adjusted_reps', 
                             'adjusted_weight', 'adjusted_minutes', 'adjusted_rpe']
            if not all(k in item for k in required_keys):
                print(f"AI schedule item is missing keys: {item}")
                return [], "AI建議的課表項目缺少必要欄位。"
        
        return ai_data['adjusted_schedule'], markdown2.markdown(ai_data['explanation'])
    except json.JSONDecodeError as e:
        print(f"Error decoding AI JSON: {e}\nRaw response: {response.text if 'response' in locals() else 'No response'}")
        return [], f"AI回應JSON格式錯誤: {e}"
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        error_detail = str(e)
        if 'response' in locals() and hasattr(response, 'prompt_feedback') and response.prompt_feedback and response.prompt_feedback.block_reason:
             error_detail += f" | Blocked due to: {response.prompt_feedback.block_reason}"
        return [], f"AI服務錯誤: {error_detail}"

@app.route('/', methods=['GET', 'POST'])
def index():
    ai_adjusted_schedule = []
    ai_explanation = ""
    form_items_for_template = [] # To repopulate form if validation fails

    if request.method == 'POST':
        data = request.form
        processed_items = [] # Items with full details and calculated load
        item_count = int(data.get('item_count', 0))
        
        at_least_one_valid_for_calc = False

        for i in range(1, item_count + 1):
            name = data.get(f'name{i}')
            action_select = data.get(f'action{i}')
            custom_action = data.get(f'custom_action{i}')
            action = custom_action if action_select == '其他' and custom_action else action_select

            if not (name and action):
                # Add a placeholder or skip if you want to be strict
                # For repopulating form, it's better to keep a representation
                form_items_for_template.append({'original_index': i}) 
                continue

            exercise_type = '有氧運動' if name == '有氧運動' else '無氧運動'
            
            sets_str = data.get(f'sets{i}')
            reps_str = data.get(f'reps{i}')
            weight = data.get(f'weight{i}', '') # Weight can be text e.g. "BW"
            minutes_str = data.get(f'minutes{i}')
            rpe_str = data.get(f'rpe{i}')

            current_item = {
                'name': name,
                'action': action,
                'type': exercise_type,
                'sets': None, 'reps': None, 'weight': weight if weight else None,
                'minutes': None, 'rpe': None,
                'item_load': None, 'suggestion': '---',
                'original_index': i # For repopulating form
            }

            try:
                if exercise_type != '有氧運動':
                    if sets_str and sets_str.isdigit(): current_item['sets'] = int(sets_str)
                    if reps_str and reps_str.isdigit(): current_item['reps'] = int(reps_str)
                
                if minutes_str: current_item['minutes'] = float(minutes_str) # Allow decimals for minutes
                if rpe_str and rpe_str.isdigit():
                    rpe_val = int(rpe_str)
                    if 1 <= rpe_val <= 10:
                        current_item['rpe'] = rpe_val
                        if rpe_val >= 9: current_item['suggestion'] = '強度極高，注意恢復'
                        elif rpe_val >= 7: current_item['suggestion'] = '強度較高'
                        elif rpe_val <= 4: current_item['suggestion'] = '強度偏低，可考慮提升'
                        else: current_item['suggestion'] = '強度適中'
                    else:
                        current_item['suggestion'] = "RPE應為1-10"
                
                # Calculate item_load (Minutes * RPE)
                if current_item['minutes'] is not None and current_item['rpe'] is not None:
                    current_item['item_load'] = round(current_item['minutes'] * current_item['rpe'], 2)
                    at_least_one_valid_for_calc = True

            except ValueError:
                # Handle cases where conversion might fail, though isdigit checks help
                print(f"ValueError processing item {i}")
                current_item['suggestion'] = "輸入格式錯誤"

            processed_items.append(current_item)
            form_items_for_template.append(current_item) # Also use for repopulating form

        if not at_least_one_valid_for_calc:
            # Repopulate item_count for the template if it was dynamic
            # And pass back the items the user tried to fill
            return render_template('index.html', exercises=exercise_data, 
                                   item_count=max(3, item_count), # Ensure at least 3 items display
                                   error="請至少填寫一個包含「總時長」和「RPE」的完整項目！",
                                   submitted_items=form_items_for_template) # For repopulating form (needs template adjustment)
        
        metrics = calculate_training_metrics(processed_items)
        
        if api_key:
            workout_log_str = format_items_for_ai(processed_items)
            ai_adjusted_schedule, ai_explanation = get_ai_recommendations(workout_log_str, processed_items)
        else:
            ai_explanation = "AI建議功能未啟用 (缺少API金鑰)。"

        return render_template('result.html', 
                               items_with_details=processed_items, 
                               metrics=metrics,
                               ai_adjusted_schedule=ai_adjusted_schedule,
                               ai_explanation=ai_explanation)
    
    # GET request
    initial_item_count = request.args.get('item_count', 3, type=int)
    return render_template('index.html', exercises=exercise_data, item_count=initial_item_count)

if __name__ == '__main__':
    app.run(debug=True)