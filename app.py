from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)


