from flask import Flask, render_template, request, jsonify, send_file
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
import io

app = Flask(__name__)

# In-memory database for demo
EMPLOYEES = [
    {"experience": 2, "actual": 55000, "predicted": 52800},
    {"experience": 5, "actual": 62000, "predicted": 58900},
    {"experience": 8, "actual": 95000, "predicted": 92300},
    {"experience": 10, "actual": 78000, "predicted": 81200},
    {"experience": 12, "actual": 88000, "predicted": 91500},
    {"experience": 15, "actual": 125000, "predicted": 122500},
    {"experience": 18, "actual": 132000, "predicted": 128900},
    {"experience": 20, "actual": 165000, "predicted": 168200},
    {"experience": 25, "actual": 195000, "predicted": 189500},
]

def predict_salary(data):
    base = 40000
    edu = {"Bachelor": 1.0, "Master": 1.3, "PhD": 1.8, "PostDoc": 1.6}
    dept = {"Engineering": 1.4, "Medicine": 1.6, "Business": 1.3,
            "Science": 1.2, "Arts": 1.0, "Social": 1.1, "Administration": 0.8}
    pos = {"Research Assistant": 0.8, "Lecturer": 1.0, "Assistant Professor": 1.2,
           "Associate Professor": 1.5, "Full Professor": 2.0, "Research Scientist": 1.3,
           "Department Head": 2.2, "Dean": 2.8, "Administrative Staff": 0.7}
    loc = {"Urban": 1.2, "Suburban": 1.0, "Rural": 0.85}
    salary = base
    salary *= edu.get(data.get("education"), 1.0)
    salary *= dept.get(data.get("department"), 1.0)
    salary *= pos.get(data.get("position"), 1.0)
    salary += int(data.get("experience", 0)) * 1800
    salary *= loc.get(data.get("location"), 1.0)
    salary += int(data.get("research", 0)) * 500
    salary += int(data.get("grants", 0)) * 0.05
    if int(data.get("age", 0)) > 40:
        salary *= 1.1
    return int(round(salary))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        predicted_salary = predict_salary(data)
        EMPLOYEES.append({
            "experience": int(data.get("experience", 0)),
            "actual": None,
            "predicted": predicted_salary
        })
        return jsonify({"predicted_salary": predicted_salary})
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/plot.png')
def plot_png():
    print("Plot route called")  # Debug
    try:
        # Clear any existing plots
        plt.clf()
        
        # Create a simple plot
        plt.figure(figsize=(8, 6))
        
        # Get data
        experiences = []
        predictions = []
        actual_exp = []
        actual_sal = []
        
        for emp in EMPLOYEES:
            if emp.get("predicted") is not None:
                experiences.append(emp["experience"])
                predictions.append(emp["predicted"])
            if emp.get("actual") is not None:
                actual_exp.append(emp["experience"])
                actual_sal.append(emp["actual"])
        
        print(f"Data points - Predicted: {len(predictions)}, Actual: {len(actual_sal)}")  # Debug
        
        # Plot data
        if actual_sal:
            plt.scatter(actual_exp, actual_sal, color='blue', label='Actual Salary', s=50, alpha=0.7)
        
        if predictions:
            plt.scatter(experiences, predictions, color='red', label='Predicted Salary', s=50, alpha=0.7)
        
        # Formatting
        plt.xlabel('Years of Experience')
        plt.ylabel('Salary ($)')
        plt.title('Salary vs Experience')
        plt.grid(True, alpha=0.3)
        
        if actual_sal or predictions:
            plt.legend()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        
        # Clean up
        plt.close()
        
        print("Plot generated successfully")  # Debug
        return send_file(buffer, mimetype='image/png')
        
    except Exception as e:
        print(f"Plot generation error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a simple text response instead of trying to create another plot
        return f"Plot error: {str(e)}", 500

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, port=5000)