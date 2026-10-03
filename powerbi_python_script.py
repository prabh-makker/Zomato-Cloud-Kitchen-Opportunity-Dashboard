import pandas as pd

DATA = "C:/Users/khalo/New folder/data"

# Already cleaned by prep_data.py (mojibake fix, dedup, locality join) — this step just hands that data to Power BI.
restaurants_clean = pd.read_csv(f"{DATA}/restaurants_clean.csv")
locality_clean = pd.read_csv(f"{DATA}/locality_clean.csv")
