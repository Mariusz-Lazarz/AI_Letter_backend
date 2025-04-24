from pydantic import BaseModel, field_validator
import uuid


class JobDescriptionValidator:
    @field_validator("job_desc")
    def validate_job_description(cls, value):
        if len(value) < 50:
            raise ValueError("Job description must be at least 50 characters")
        if len(value) > 3000:
            raise ValueError(
                "Job description cannot be longer than 3000 characters long"
            )
        return value


class GenerateCoverLetter(BaseModel, JobDescriptionValidator):
    cv_id: uuid.UUID
    job_desc: str
