from tenacity import retry, wait_random_exponential, stop_after_attempt

import time
import json

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(10))
def generateEmbeddings(text, embeddings_deployment, AzureOpenAIClient):
    
    # Generate embeddings from the input text
    response = AzureOpenAIClient.embeddings.create(
        input=text,
        model=embeddings_deployment
    )

    # Parse the response into a json object
    embeddings = json.loads(response.model_dump_json(indent=2))

    # Small delay to avoid rate limiting (adjust if needed)
    time.sleep(0.01)

    return embeddings["data"][0]["embedding"]


def generateJobEmbedding(job, embeddings_deployment, AzureOpenAIClient):
    # Extracting fields from the job dictionary
    job_id = job.get("Job Id", "")
    experience_level = job.get("Experience", "")
    qualifications = job.get("Qualifications", "")
    salary_range = job.get("Salary Range", "")
    location = job.get("location", "")
    country = job.get("Country", "")
    latitude = job.get("latitude", "")
    longitude = job.get("longitude", "")
    work_type = job.get("Work Type", "")
    company_size = job.get("Company Size", "")
    job_posting_date = job.get("Job Posting Date", "")
    preference = job.get("Preference", "")
    contact_person = job.get("Contact Person", "")
    contact = job.get("Contact", "")
    title = job.get("Job Title", "")
    role = job.get("Role", "")
    job_portal = job.get("Job Portal", "")
    description = job.get("Job Description", "")
    benefits = job.get("Benefits", "")
    skills = job.get("skills", "")
    responsibilities = job.get("Responsibilities", "")
    company = job.get("Company", "")
    company_profile = job.get("Company Profile", "")

    # Combine all relevant fields for embedding
    textToEmbed = f"""
    Job Id: {job_id}
    Job Title: {title}
    Role: {role}
    Description: {description}
    Skills: {skills}
    Experience Level: {experience_level}
    Qualifications: {qualifications}
    Salary Range: {salary_range}
    Location: {location}
    Country: {country}
    Latitude: {latitude}
    Longitude: {longitude}
    Work Type: {work_type}
    Company Size: {company_size}
    Job Posting Date: {job_posting_date}
    Preference: {preference}
    Contact Person: {contact_person}
    Contact: {contact}
    Benefits: {benefits}
    Responsibilities: {responsibilities}
    Company: {company}
    Company Profile: {company_profile}
    """
    
    # Generate embeddings
    job["jobVector"] = generateEmbeddings(textToEmbed, embeddings_deployment, AzureOpenAIClient)
    
    return job
