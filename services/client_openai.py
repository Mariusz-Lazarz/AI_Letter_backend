from openai import OpenAI
from config import OPENAI_API_KEY
from prompts import generate_letter_prompt


client = OpenAI(api_key=OPENAI_API_KEY)


def generate_cover_letter(cv, job):
    response = client.responses.create(
        model="gpt-4o",
        instructions=generate_letter_prompt,
        input=f"<cv> {cv} </cv> <job> {job} </job>"
    )
    return response.output_text
