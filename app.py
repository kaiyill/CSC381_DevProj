import csv
from flask import Flask, render_template, request

app = Flask(__name__)

def read_csv(file_path):
    # The same read_csv function as before

    @app.route('/', methods=['GET', 'POST'])
    def display_data():
        data = None

    if request.method == 'POST':
        uploaded_file = request.files['csv_file']

        if uploaded_file.filename != '':
            # Save the uploaded file temporarily
            file_path = 'temp.csv'
            uploaded_file.save(file_path)

            # Read and organize the data
            data = read_csv(file_path)

    return render_template('data.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)

