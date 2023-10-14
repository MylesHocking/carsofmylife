import pandas as pd
from app.app import db, app

# Path to the CSV file
csv_file_path = 'data/CQA_Premium.csv'

# Read the CSV into a DataFrame
df = pd.read_csv(csv_file_path)

# Create the table and populate it
with app.app_context():
    df.to_sql('car_data', con=db.engine, if_exists='replace', index=False)
