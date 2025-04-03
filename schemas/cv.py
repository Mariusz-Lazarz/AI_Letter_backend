from pydantic import BaseModel
from datetime import datetime
import uuid


class CvListItem(BaseModel):
    id: uuid.UUID
    original_name: str
    created_at: datetime
