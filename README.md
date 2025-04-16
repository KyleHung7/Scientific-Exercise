# Scientific Training Load Analysis Website

**Members** [@KyleHung7](https://github.com/KyleHung7)
[https://youtu.be/v52GLI_23dg](https://youtu.be/v52GLI_23dg)


## Project Introduction
This project presents a streamlined and science-based **training load analysis website**, designed for athletes, fitness enthusiasts, and beginners. It provides professional, user-friendly tools for analyzing training impulses and making data-driven decisions to avoid overtraining and optimize performance.

## Workflow
![image](https://github.com/user-attachments/assets/42066ec1-50ed-46c3-b759-cc78d9f5ff12)

### **Problems Addressed**
1. **Overtraining and insufficient recovery**  
   Users often don’t know when to rest, increasing injury risk due to continuous intense training.

2. **Lack of structured training plans**  
   Many rely on intuition when planning workouts, leading to stagnation or inefficiency.

3. **No consistent tracking or data accumulation**  
   Without long-term data tracking, it's hard to measure progress or detect warning signs.

4. **Information overload and poor readability**  
   Complex data is hard to interpret, making it challenging to understand what actions to take.

### **Solutions**
- **Daily input interface** for logging training sessions.
- **Automatic calculation of Training Load** using RPE and time.
- **Fatigue analysis using ACWR (Acute:Chronic Workload Ratio)**.
- **Personalized suggestions and risk alerts** based on data.
- **Interactive visual dashboards** for better understanding.
- **Report export functionality** for personalized recommendations.

---

## User Input
Users are guided to enter the following daily:

- **Activity Name** (dropdown or custom)
- **Duration (minutes)**
- **RPE (Rate of Perceived Exertion, scale 1–10)**

**Optional fields**: sleep duration, notes, fitness habits  
**Automatic calculation**:  
📌 `Training Load = RPE × Duration`

---

## Dashboard Features: Personalized Training Suggestions

### 🔹 **Daily Status Card**  
Indicates whether to rest or train. Suggests training intensity: Easy / Moderate / High-Risk.

### 📊 **Training Load Chart**  
Bar chart for recent 7 days / 4 weeks. Line chart for weekly average & total.

### ⚠️ **ACWR Calculation**  
Displays current workload risk level, e.g., “Training load too high, consider resting one day.”

---

## Reports and Recommendations

- 📄 Export **PDF training analysis reports**  
- 🔍 Include **summary suggestions** and compiled notes  
- 📈 Trend-based **personalized training plans**

---

## User Workflow: Simplified Process

1. **Add a New Record**  
   Open the website → Click “Add Record”

2. **Input Training Data**  
   Fill in activity, duration, and RPE

3. **Instant Calculation**  
   Training Load is computed and stored

4. **View Trends and Analysis**  
   Dashboard displays personalized advice, charts, and trends

---

## Technical Architecture & Development Timeline

### **Tools & Technologies**
- **UI Interface**: Gradio (for fast and clean user interface)
- **Visualization**: Matplotlib / Plotly (to render training charts)
- **Data Storage**: CSV / Pandas (simple, local-first data management)
- **Code Integration**: Combines modules from Assignments 1, 2, and 4

---

### **Development Timeline**

- **Weeks 9 - 10**: System Foundations  
  - Finalize project scope and feature set  
  - Build input form (Gradio)  
  - Implement CSV-based data storage and Training Load logic

- **Weeks 11 - 12**: Core Functionality  
  - Develop initial dashboard (daily suggestions + risk indicators)  
  - Implement ACWR calculation logic  
  - Visualize training loads with charts  
  - Integrate analysis with UI

- **Weeks 13 - 14**: Reporting Features  
  - Add PDF export functionality  
  - Display insights and warning messages  
  - Conduct system integration testing  
  - Draft user guide and presentation materials

- **Weeks 15 - 16**: Finalization and Demo  
  - Polish features, fix bugs, finalize UI  
  - Prepare for project presentation

