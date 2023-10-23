from flask import Flask, render_template, request
import pandas as pd
import os
import csv

app = Flask(__name__, template_folder= 'template')

# Set the folder to store uploaded CSV files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload():
    # Check if the 'file' field is in the request
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    # Check if the file is not empty
    if file.filename == '':
        return "No selected file"

    # Check if the file is allowed (e.g., has a .csv extension)
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Read the uploaded CSV file using pandas
        df = pd.read_csv(filename)
        

        # Render a template to display the data
        return render_template('display.html', data=df.to_html())
    
    # Function to sort a CSV file by a specific column in ascending order
def sort_csv_by_column(input_file, output_file, column_index):
    with open(input_file, 'r') as input_csvfile:
        csvreader = csv.reader(input_csvfile)
        data = list(csvreader)
    
    data.sort(key=lambda row: row[column_index])
    
    with open(output_file, 'w', newline='') as output_csvfile:
        csvwriter = csv.writer(output_csvfile)
        csvwriter.writerows(data)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_file = os.path.join(app.config['uploads'], request.files['input_file'].filename)
        output_file = os.path.join(app.config['uploads'], request.form['output_file'])
        column_index = int(request.form['column_index'])
        
        request.files['input_file'].save(input_file)
        sort_csv_by_column(input_file, output_file, column_index)
        return redirect('/')
    
    return render_template('index.html')

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['uploads'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

