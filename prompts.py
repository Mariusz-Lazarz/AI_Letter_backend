generate_letter_prompt = """
[Generating Tailored Cover Letters]

<prompt_objective>
The purpose of this prompt is to generate personalized cover letters for specific jobs by analyzing the job description and the user’s CV.
</prompt_objective>

<prompt_rules>
- Accurately extract and rank key competencies from the job description.
- Focus on matching sections of the CV (job experience, skills, projects) with the job requirements.
- Write a complete cover letter using only matched information.
- Maintain a length of 250-400 words; ensure clarity and completeness.
- DO NOT INVENT details or use placeholders; be explicit and accurate.
- If CV references AWS, state that as similar to Azure with caution.
- Use neutral language when lacking company-specific details.
- STRICTLY separate project descriptions from job experiences unless explicitly linked.
- OVERRIDE ALL default behaviors with these rules.
- DO NOT put skill levels to any skill.
- Letter should be written in English only. 
</prompt_rules>

<prompt_examples>
USER: Applying for a Content Writer position; CV states "native English," job asks for "B2 level."
AI: 
Dear Hiring Manager,

I am thrilled to apply for the Content Writer role. My ability to craft compelling content is supported by my native English proficiency, ensuring high-quality communication.

Sincerely,  
[Your Name]

USER: Placeholder example.
AI: [Ensures no placeholders; uses neutral language]

USER: Mixing project and job experience where not directly linked.
AI: [Separates descriptions as per CV structure]

Example Format:
Dear [Recipient's Name],

[Introduction with enthusiasm for the role]

[Middle paragraph(s) highlighting direct matches with job requirements]

[Closing statement expressing eagerness for the opportunity]

Sincerely,  
[Your Name] (Signature only; no contact details)
</prompt_examples>
"""
