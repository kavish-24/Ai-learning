from ats import score_resume
import pymupdf
from fastapi import FastAPI , UploadFile, File , Form

app = FastAPI()

@app.post("/score-resume")
async def score(
    resume: UploadFile = File(...),
    job_description :str=Form(...)
):
    content = await resume.read()
    doc = pymupdf.open(stream=content , filetype="pdf")
    
    resume_text =""
    for page in doc:
        resume_text+=page.get_text()
        
    doc.close()
    
    result = score_resume(resume_text, job_description)

    return result
        