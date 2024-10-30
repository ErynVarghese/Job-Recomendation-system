import os
import pandas as pd
import pymongo
import dask.dataframe as dd
from dotenv import load_dotenv


load_dotenv(".env")

def fetch_jobs_from_csv():

    df = dd.read_csv(r'D:\Eryn\Downloads\job_descriptions.csv\job_descriptions.csv')

    #debug-start
    test_df = pd.read_csv(r'D:\Eryn\Downloads\job_descriptions.csv\job_descriptions.csv')
    print(test_df.head())
    #debug-end

    if len(df) == 0:
        print(f"No jobs found in {r'D:\Eryn\Downloads\job_descriptions.csv\job_descriptions.csv'}.")
        return []

   
    return df.compute().to_dict(orient='records') 



