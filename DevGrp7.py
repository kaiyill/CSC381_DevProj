import csv

def read_csv(file_path):
    data = {}  # Initialize an empty dictionary to store the data

    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        
        # Read the header row to get column names
        header = next(csvreader)
        
        # Initialize the dictionary with empty lists for each column
        for column_name in header:
            data[column_name] = []

        # Read the data and organize it by column
        for row in csvreader:
            for column_name, value in zip(header, row):
                data[column_name].append(value)

    return data

# Replace 'data.csv' with your CSV file path
file_path = 'kaiyill/CSC381_DevProj/someExampleData/NFLTeams2022.csv'
csv_data = read_csv(file_path)

# Print the organized data
for column_name, values in csv_data.items():
    print(f'{column_name}: {values}')
