import os
import pandas as pd
import pymongo
import dask.dataframe as dd
from dotenv import load_dotenv


load_dotenv(".env")

def fetch_jobs_from_csv():

    df = dd.read_csv('D:/Eryn/Downloads/job_descriptions.csv')

    if len(df) == 0:
        print(f"No jobs found in {'D:/Eryn/Downloads/job_descriptions.csv'}.")
        return []

   
    return df.compute().to_dict(orient='records') 



