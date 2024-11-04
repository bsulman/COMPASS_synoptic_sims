

import pandas as pd
import glob

# Define the directory and pattern
dirpat = '../../../data/buoys/GoodwinIsland_CH019.38/*.csv'

# Find all files matching the pattern
files = glob.glob(dirpat)

# Initialize an empty DataFrame
all_data = pd.DataFrame()

# Loop through the files and append to the DataFrame
for file in files:
    df = pd.read_csv(file)
    all_data = all_data.append(df, ignore_index=True)

# Save the resulting DataFrame to a CSV file
all_data.to_csv('/path/to/save/combined.csv', index=False)
