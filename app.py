from flask import Flask, jsonify, render_template, request, redirect, session
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

# Function to standardize data by a certain column index
def standardize_csv(input_file, column_index, method, output_file=None):
    df = pd.read_csv(input_file)
    column_name = df.columns[column_index]

    # For the different methods (0-10 was giving me trouble)
    if method == '1-10':
        df[column_name] = (df[column_name] - df[column_name].min()) / (
                df[column_name].max() - df[column_name].min()) * 9 + 1
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

# Index
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

    return render_template('index.html', sorted_data=sorted_data, standardized_data=standardized_data)

@app.route("/color", methods=['GET', 'POST'])
def color():
    return render_template('color.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file uploaded'})
    
    df = pd.read_csv(file)
    return jsonify({'data': df.to_html(classes='table table-striped table-bordered')})
    

def get_columns(input_file):
    df = pd.read_csv(input_file)
    columns = df.columns.tolist()
    return columns

@app.route('/io', methods=['GET', 'POST'], endpoint='IO')
def io():
    csv_data = None
    input_columns = []

    if request.method == 'POST':
        file = request.files['csv_file']

        if file and file.filename.endswith('.csv'):
            session['input_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(session['input_file_path'])

            # Get the columns from the uploaded CSV file
            input_columns = get_columns(session['input_file_path'])

    return render_template('IO.html', csv_data=csv_data, columns=input_columns, input_columns=input_columns)

@app.route('/display_io', methods=['POST'])
def display_io():
    input_columns = request.form.getlist('input_columns')

    if not input_columns:
        return redirect('/io')

    df = pd.read_csv(session['input_file_path'])
    df_selected = df[input_columns]
    csv_data = df_selected.to_html(classes='table table-striped table-bordered')

    # Additional code for row comparison
    selected_row_index = int(request.form.get('selected_row_index', 0))
    selected_row = df_selected.iloc[selected_row_index]

    # Exclude the selected row for comparison
    df_for_comparison = df_selected.drop(index=selected_row_index)

    # Calculate similarity based on all comparison columns
    similarity_comparison = df_for_comparison.apply(lambda row: sum(row == selected_row), axis=1)
    most_similar_index_comparison = similarity_comparison.idxmax()
    most_similar_row_comparison = df_selected.iloc[most_similar_index_comparison]

    # Calculate similarity based on all numerics
    numeric_columns = df_for_comparison.select_dtypes(include='number').columns
    similarity_numerics = df_for_comparison[numeric_columns].apply(lambda row: sum(row == selected_row[numeric_columns]), axis=1)
    most_similar_index_numerics = similarity_numerics.idxmax()
    most_similar_row_numerics = df_selected.iloc[most_similar_index_numerics]

    # Calculate similarity based on all input columns
    similarity_inputs = df_for_comparison[input_columns].apply(lambda row: sum(row == selected_row[input_columns]), axis=1)
    most_similar_index_inputs = similarity_inputs.idxmax()
    most_similar_row_inputs = df_selected.iloc[most_similar_index_inputs]

    # Calculate similarity based on all output columns
    output_columns = [col for col in df_selected.columns if col not in input_columns]
    similarity_outputs = df_for_comparison[output_columns].apply(lambda row: sum(row == selected_row[output_columns]), axis=1)
    most_similar_index_outputs = similarity_outputs.idxmax()
    most_similar_row_outputs = df_selected.iloc[most_similar_index_outputs]

    # Prepare data for display
    selected_row_html = selected_row.to_frame().to_html(classes='table table-striped table-bordered')
    most_similar_row_comparison_html = most_similar_row_comparison.to_frame().to_html(classes='table table-striped table-bordered')
    most_similar_row_numerics_html = most_similar_row_numerics.to_frame().to_html(classes='table table-striped table-bordered')
    most_similar_row_inputs_html = most_similar_row_inputs.to_frame().to_html(classes='table table-striped table-bordered')
    most_similar_row_outputs_html = most_similar_row_outputs.to_frame().to_html(classes='table table-striped table-bordered')

    return render_template('IO.html', csv_data=csv_data, columns=get_columns(session['input_file_path']),
                           input_columns=input_columns, selected_row_html=selected_row_html,
                           most_similar_row_comparison_html=most_similar_row_comparison_html,
                           most_similar_row_numerics_html=most_similar_row_numerics_html,
                           most_similar_row_inputs_html=most_similar_row_inputs_html,
                           most_similar_row_outputs_html=most_similar_row_outputs_html)

if __name__ == '__main__':
    app.run(debug=True)
