import os
import pandas as pd
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

def fetch_jobs_from_csv(file_path):

   
    df = pd.read_csv(file_path)
    
    
    return df.to_dict(orient='records')

def store_jobs_in_mongodb(jobs, client, mongodb_database):
    db = client[mongodb_database]
    collection = db['jobs']  
    operations = []

    for job in jobs:
        job_document = {
            "_id": job['Job Id'],  
            "title": job.get('Job Title'),
            "description": job.get('Job Description'),
            "location": job.get('location'),
            "company": job.get('Company'),
            "date": job.get('Job Posting Date'),
            "skills": job.get('skills'), 
            "experience_level": job.get('Experience'),  
            "salary_range": job.get('Salary Range'), 
            "work_type": job.get('Work Type'), 
            "company_size": job.get('Company Size')  
        }
        operations.append(job_document)

    if operations:
        # Bulk write to MongoDB
        collection.bulk_write(
            [pymongo.UpdateOne({"_id": job["_id"]}, {"$set": job}, upsert=True) for job in operations],
            ordered=False
        )

def fetch_and_store_jobs(file_path, client, mongodb_database):
    jobs = fetch_jobs_from_csv(file_path)
    if jobs:
        store_jobs_in_mongodb(jobs, client, mongodb_database)
        print(f"Stored {len(jobs)} jobs in MongoDB.")
    else:
        print("No jobs found to store.")

