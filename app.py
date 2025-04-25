from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# 定義運動項目及其動作
exercise_data = {
    '上肢肌力': ['啞鈴臥推', '啞鈴肩推', '啞鈴划船'],
    '上肢爆發': ['啞鈴推舉', '啞鈴快肩推', '藥球砸地'],
    '下肢肌力': ['啞鈴聖杯深蹲', '啞鈴硬舉', '槓鈴硬舉'],
    '下肢爆發': ['深蹲跳', '箱跳', '抓舉跳'],
    '有氧運動': ['跑步機', '飛輪', '游泳']
}
exercise_types = list(exercise_data.keys())

def calculate_training_metrics(items):
    # 過濾有效項目
    valid_items = [item for item in items if item['name'] and item['action'] and item['rpe'] is not None]
    
    if not valid_items:
        return {
            'weekly_workout_summary': 0,
            'training_load': 0,
            'training_monotony': 0,
            'training_strain': 0,
            'analysis': '無有效數據可分析'
        }
    
    # 計算週間訓練量變化 (WWS) 和 運動訓練量 (TL)
    total_load = sum(item['rpe'] * (item['sets'] if item['type'] != '有氧運動' else item['minutes'] / 5) for item in valid_items)
    weekly_workout_summary = total_load / len(valid_items)
    training_load = total_load
    
    # 計算訓練同質性 (TM)
    rpe_values = [item['rpe'] for item in valid_items]
    training_monotony = pd.Series(rpe_values).std() / pd.Series(rpe_values).mean() if rpe_values else 0
    
    # 計算訓練張力值 (TS)
    training_strain = training_load * training_monotony if training_monotony else 0
    
    # 分析建議
    analysis = []
    if weekly_workout_summary > 10:
        analysis.append("週間訓練量顯示肌力進步顯著，持續保持！")
    elif weekly_workout_summary < 5:
        analysis.append("週間訓練量偏低，建議增加訓練強度或頻率。")
    
    if training_monotony < 0.5:
        analysis.append("訓練同質性穩定，課表執行良好。")
    elif training_monotony > 1.0:
        analysis.append("訓練同質性偏高，建議調整課表增加變化。")
    
    if training_strain > 100:
        analysis.append("訓練張力值偏高，注意避免過度訓練，建議增加休息。")
    elif training_strain < 50:
        analysis.append("訓練張力值偏低，可考慮提升訓練量。")
    
    return {
        'weekly_workout_summary': round(weekly_workout_summary, 2),
        'training_load': round(training_load, 2),
        'training_monotony': round(training_monotony, 2),
        'training_strain': round(training_strain, 2),
        'analysis': " ".join(analysis) if analysis else "訓練數據正常，繼續保持！"
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form
        items = []
        item_count = int(data.get('item_count', 3))
        
        for i in range(1, item_count + 1):
            name = data.get(f'name{i}')
            action = data.get(f'action{i}')
            if not (name and action):
                continue
            type_ = '有氧運動' if name == '有氧運動' else '無氧運動'
            sets = data.get(f'sets{i}')
            minutes = data.get(f'minutes{i}')
            rpe = data.get(f'rpe{i}')
            
            if rpe:
                rpe = int(rpe)
                suggestion = '適當'
                if rpe >= 9:
                    suggestion = '建議減量或休息'
                elif rpe <= 6:
                    suggestion = '建議提升強度'
                
                items.append({
                    'name': name,
                    'action': action,
                    'rpe': rpe,
                    'type': type_,
                    'sets': int(sets) if sets and type_ != '有氧運動' else None,
                    'minutes': int(minutes) if minutes and type_ == '有氧運動' else None,
                    'suggestion': suggestion
                })
        
        if not items:
            return render_template('index.html', exercises=exercise_data, item_count=3, error="請至少填寫一個完整項目！")
        
        metrics = calculate_training_metrics(items)
        return render_template('result.html', items=items, metrics=metrics)
    
    return render_template('index.html', exercises=exercise_data, item_count=3)

if __name__ == '__main__':
    app.run(debug=True)