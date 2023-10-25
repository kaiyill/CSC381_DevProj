from flask import Flask, render_template, request, redirect, send_from_directory, session
import csv
import os
import pandas as pd
from scipy import stats

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Define the folder for storing uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to sort a CSV file by a specific column
def sort_csv(input_file, column_index, ascending=True, output_file=None):
    with open(input_file, 'r') as input_csvfile:
        csvreader = csv.reader(input_csvfile)
        data = list(csvreader)
        
    header_row = data[0]
    data = data[1:]
    
    # Convert the values in the specified column to floats for proper numeric sorting
    data.sort(key=lambda row: float(row[column_index]), reverse=not ascending)
    
    data.insert(0, header_row)
    
    if output_file:
        with open(output_file, 'w', newline='') as output_csvfile:
            csvwriter = csv.writer(output_csvfile)
            csvwriter.writerows(data)
        return output_file
    else:
        return data

# Function to standardize a column and handle outliers
def standardize_column(data, column_name, method, lower_bound, upper_bound):
    # Select the column
    column = data[column_name]

    if method == "z-score":
        z_scores = stats.zscore(column)
        return z_scores
    else:
        if method == "0-10":
            lower_bound, upper_bound = 0, 10
        elif method == "1-10":
            lower_bound, upper_bound = 1, 10
        elif method == "0-1":
            lower_bound, upper_bound = 0, 1
        elif method == "-1-1":
            lower_bound, upper_bound = -1, 1

        # Clip values to the specified range and then normalize
        clipped = column.clip(lower=lower_bound, upper=upper_bound)
        normalized = (clipped - lower_bound) / (upper_bound - lower_bound)
        return normalized

@app.route('/', methods=['GET', 'POST'])
def index():
    sorted_data = None
    output_file = None

    # Check if the session contains the file path
    if 'input_file_path' in session:
        input_file = session['input_file_path']
    else:
        input_file = None

    if request.method == 'POST':
        column_index = int(request.form['column_index'])
        ascending = request.form['ascending'] == 'ascending'
        output_file_name = request.form['output_file']

        if not input_file:
            # Upload the file if it's not in the session
            input_file = os.path.join(app.config['UPLOAD_FOLDER'], request.files['input_file'].filename)
            request.files['input_file'].save(input_file)
            session['input_file_path'] = input_file  # Store the file path in the session

        # Standardization method
        standardization_method = request.form['standardization_method']

        # Standardize the data
        data = pd.read_csv(input_file)
        columns_to_standardize = [data.columns[column_index]]
        for column_name in columns_to_standardize:
            standardized_data = standardize_column(data, column_name, standardization_method, 0, 1 if standardization_method == "0-1" else 10)
            data[column_name] = standardized_data

        if output_file_name:  # If an output file is specified
            output_file = os.path.join(app.config['UPLOAD_FOLDER'], output_file_name)
            data.to_csv(output_file, index=False)
        else:  # If no output file is specified
            sorted_data = data.to_dict(orient='records')

    return render_template('index.html', sorted_data=sorted_data, output_file=output_file)

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
