let exerciseData = {};

function initializeExerciseData(data) {
    try {
        exerciseData = data;
        console.log('exerciseData loaded:', exerciseData);
    } catch (e) {
        console.error('Error parsing exerciseData:', e);
        exerciseData = {};
    }
}

function updateActions(select, index) {
    const actionSelect = document.getElementById(`action${index}`);
    const customInput = document.querySelector(`input[name="custom_action${index}"]`);
    const type = select.value;

    // Reset action dropdown
    actionSelect.innerHTML = '<option value="">選擇動作</option><option value="其他">其他（請自行輸入）</option>';

    // Populate actions if type exists in exerciseData
    if (type && exerciseData[type] && Array.isArray(exerciseData[type])) {
        exerciseData[type].forEach(action => {
            const option = document.createElement('option');
            option.value = action;
            option.textContent = action;
            actionSelect.appendChild(option);
        });
    } else {
        console.warn(`No actions found for type: ${type}`);
    }

    // Use arrow function for onchange to avoid linter issues
    actionSelect.onchange = () => {
        customInput.style.display = actionSelect.value === '其他' ? 'block' : 'none';
    };

    // Toggle sets/minutes input based on exercise type
    const isAerobic = type === '有氧運動';
    document.querySelector(`input[name="sets${index}"]`).style.display = isAerobic ? 'none' : 'block';
    document.querySelector(`input[name="minutes${index}"]`).style.display = isAerobic ? 'block' : 'none';
}

function addItem() {
    const itemCount = parseInt(document.getElementById('item_count').value) + 1;
    document.getElementById('item_count').value = itemCount;

    const itemDiv = document.createElement('div');
    itemDiv.className = 'card p-4 mb-3';
    itemDiv.innerHTML = `
        <h3>項目 ${itemCount}</h3>
        <div class="mb-3">
            <label class="form-label">運動類別</label>
            <select name="name${itemCount}" class="form-select exercise-type" onchange="updateActions(this, ${itemCount})">
                <option value="">選擇類別</option>
                ${Object.keys(exerciseData).map(type => {
                    return `<option value="${type}">${type}</option>`;
                }).join('')}
            </select>
        </div>
        <div class="mb-3">
            <label class="form-label">動作</label>
            <select name="action${itemCount}" id="action${itemCount}" class="form-select">
                <option value="">選擇動作</option>
                <option value="其他">其他（請自行輸入）</option>
            </select>
            <input type="text" name="custom_action${itemCount}" class="form-control mt-2" placeholder="輸入自訂動作（若選擇其他）" style="display: none;">
        </div>
        <div class="mb-3">
            <label class="form-label">訓練量</label>
            <input type="number" name="sets${itemCount}" class="form-control sets-input" placeholder="無氧：輸入組數" min="0">
            <input type="number" name="minutes${itemCount}" class="form-control mt-2 minutes-input" placeholder="有氧：輸入分鐘數" min="0">
        </div>
        <div class="mb-3">
            <label class="form-label">主觀用力程度 (RPE)</label>
            <select name="rpe${itemCount}" class="form-select">
                <option value="">選擇 RPE</option>
                ${Array.from({length: 10}, (_, i) => {
                    const value = i + 1;
                    return `<option value="${value}">${value}</option>`;
                }).join('')}
            </select>
            <small class="form-text text-muted">
                RPE 1-2: 非常輕鬆，可輕鬆對話<br>
                RPE 3-4: 稍有感覺，仍可輕鬆交談<br>
                RPE 5-6: 中等強度，說話稍有困難<br>
                RPE 7-8: 高強度，說話很吃力<br>
                RPE 9-10: 極限，無法說話
            </small>
        </div>
    `;
    document.getElementById('items').appendChild(itemDiv);
    console.log(`Added item ${itemCount}`);
}