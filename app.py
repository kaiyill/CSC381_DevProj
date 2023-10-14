from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__, template_folder= 'template')

# Set the folder to store uploaded CSV files
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    if request.method == 'POST':
            # Check if a file is uploaded
            if 'file' not in request.files:
                return render_template('upload.html', msg='No file uploaded')

            file = request.files['file']

            # Check if the file is empty
            if file.filename == '':
                return render_template('upload.html', msg='No file selected')

            # Check if the file is a CSV file
            if file and file.filename.rsplit('.', 1)[1].lower() == 'csv':
                # Read the file contents
                file.seek(0)
                data = file.read()

                # Process the file contents (e.g., save the file, parse the CSV data, etc.)

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

if __name__ == '__main__':
    app.run(debug=True)


