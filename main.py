from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
import PyPDF2
import io
import configparser
import google.generativeai as genai

app = FastAPI()

# Setup templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_prompt():
	config = configparser.ConfigParser()
	config.read('prompt.ini')
	prompt_text = config.get('prompt', 'text')
	return prompt_text


# Placeholder function for getting match score
def get_match_score(job_description, resume):
	# Mock implementation of match score calculation
	prompt = get_prompt() + "  ---Resume---  " + resume + "  ---Job Description---  " + job_description
	# Configure the API with your API key
	genai.configure(api_key="YOUR_API_KEY")
	
	# Initialize the Generative Model
	model = genai.GenerativeModel('gemini-1.5-flash')
	try:
		# Generate content based on the prompt
		response = model.generate_content(prompt)
		
		# Check if the response has the expected attribute
		if hasattr(response, 'text'):
			# Print the generated text
			print(response.text)
			return response.text
		else:
			print("Unexpected response format:", response)
	except Exception as e:
		print("An error occurred:", str(e))
	
	
	


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})


@app.post("/submit/")
async def handle_form(job_description: str = Form(...), resume: UploadFile = File(...)):
	resume_content = await resume.read()
	resume_file = io.BytesIO(resume_content)
	pdf_reader = PyPDF2.PdfReader(resume_file)
	num_pages = len(pdf_reader.pages)
	
	# Extract text from each page
	resume_text = ''
	for page_num in range(num_pages):
		page = pdf_reader.pages[page_num]
		resume_text += page.extract_text()
	
	score = get_match_score(job_description, resume_text)
	return templates.TemplateResponse("result.html", {"request": {}, "score": score})


if __name__ == "__main__":
	import uvicorn
	
	uvicorn.run(app, port=8001)
