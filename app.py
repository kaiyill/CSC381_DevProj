from flask import Flask, render_template, request, redirect, send_from_directory, session
import csv
import os
import pandas as pd  

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

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

#Function to standarize data by a certain column index
def standardize_csv(input_file, column_index, method, output_file=None):
    df = pd.read_csv(input_file)
    column_name = df.columns[column_index]

    #For the different methods (0-10 was giving me trouble)
    if method == '1-10':
        df[column_name] = (df[column_name] - df[column_name].min()) / (df[column_name].max() - df[column_name].min()) * 9 + 1
    elif method == '0-1':
        df[column_name] = (df[column_name] - df[column_name].min()) / (df[column_name].max() - df[column_name].min())
    elif method == '-1-1':
        df[column_name] = (df[column_name] - df[column_name].mean()) / df[column_name].std()
    elif method == 'z-score':
        df[column_name] = (df[column_name] - df[column_name].mean()) / df[column_name].std()

    # Round the values to the second decimal place
    df[column_name] = df[column_name].round(2)

    if output_file:
        df.to_csv(output_file, index=False)
        return output_file
    else:
        return df

#Index
@app.route('/', methods=['GET', 'POST'])
def index():
    sorted_data = None
    standardized_data = None  

    if 'input_file_path' in session:
        input_file = session['input_file_path']
    else:
        input_file = None

    if request.method == 'POST':
        column_index = int(request.form['column_index'])
        ascending = request.form['ascending'] == 'ascending'
        output_file_name = request.form['output_file']

        if not input_file:
            input_file = os.path.join(app.config['UPLOAD_FOLDER'], request.files['input_file'].filename)
            request.files['input_file'].save(input_file)
            session['input_file_path'] = input_file

        if request.form['submit_button'] == 'Sort':
            if output_file_name:
                output_file = os.path.join(app.config['UPLOAD_FOLDER'], output_file_name)
                output_file = sort_csv(input_file, column_index, ascending, output_file)
            else:
                sorted_data = sort_csv(input_file, column_index, ascending)
        elif request.form['submit_button'] == 'Standardize':
            method = request.form['standardization_method']
            if output_file_name:
                output_file = os.path.join(app.config['UPLOAD_FOLDER'], output_file_name)
                output_file = standardize_csv(input_file, column_index, method, output_file)
            else:
                standardized_data = standardize_csv(input_file, column_index, method)  # Store the standardized data

    return render_template('index.html', sorted_data=sorted_data, standardized_data=standardized_data)  # Pass standardized_data to the template

@app.route("/color")
def color():
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file uploaded'})
    
    df = pd.read_csv(file)
    return render_template('color.html')
    

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)