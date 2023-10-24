from flask import Flask, render_template, request, redirect, send_from_directory
import csv
import os

app = Flask(__name__)

# Define the folder for storing uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to sort a CSV file by a specific column
def sort_csv(input_file, output_file, column_index, ascending=True):
    with open(input_file, 'r') as input_csvfile:
        csvreader = csv.reader(input_csvfile)
        data = list(csvreader)
    
    data.sort(key=lambda row: row[column_index], reverse=not ascending)
    
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    sorted_data = None
    if request.method == 'POST':
        input_file = os.path.join(app.config['UPLOAD_FOLDER'], request.files['input_file'].filename)
        column_index = int(request.form['column_index'])
        ascending = request.form['ascending'] == 'ascending'
        
        request.files['input_file'].save(input_file)
        sorted_data = sort_csv(input_file, column_index, ascending)
    
    return render_template('index.html', sorted_data=sorted_data)

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
    app.template_folder = 'templates'