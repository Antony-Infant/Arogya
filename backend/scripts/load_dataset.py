#!/usr/bin/env python3
"""Load and verify the 505+ disease dataset."""
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pandas as pd
from django.conf import settings

def main():
    path = settings.DISEASE_DATASET_PATH
    if not os.path.exists(path):
        print(f"ERROR: Dataset not found at {path}")
        print("Please place medical_disease_dataset.csv in backend/data/datasets/")
        return

    df = pd.read_csv(path)
    print(f"Dataset loaded successfully!")
    print(f"Total diseases: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Empty fields: {df.isna().sum().sum()}")
    print(f"\nCategory breakdown:")
    print(df['category'].value_counts().to_string())
    print(f"\nSample diseases: {', '.join(df['disease_name'].head(10).tolist())}")

if __name__ == '__main__':
    main()
