from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime
from enum import Enum

class WorkflowStage(str, Enum):
    PRELIMINARY = "Preliminary"
    IGNITE_PROPEL = "Ignite Propel"
    COMPREHENSIVE = "Comprehensive"

class SubmissionStatus(str, Enum):
    NOT_SUBMITTED = "Not Submitted"
    SUBMITTED = "Submitted"
    GRADED = "Graded"

class TaskBase(BaseModel):
    title: str
    description: str
    guidelines: str
    stage: WorkflowStage
    deadline: datetime
    max_points: int
    file_required: bool = True
    
class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    guidelines: Optional[str] = None
    deadline: Optional[datetime] = None
    max_points: Optional[int] = None

class Task(TaskBase):
    id: Optional[str] = None
    created_by: str  # Admin user ID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskInDB(Task):
    pass

class Submission(BaseModel):
    id: Optional[str] = None
    task_id: str
    user_id: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    status: SubmissionStatus = SubmissionStatus.NOT_SUBMITTED
    submitted_at: Optional[datetime] = None
    points: Optional[int] = None
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    graded_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    task_id: str
    file_name: str

class SubmissionUpdate(BaseModel):
    status: Optional[SubmissionStatus] = None
    points: Optional[int] = None
    feedback: Optional[str] = None

class SubmissionGrade(BaseModel):
    points: int
    feedback: Optional[str] = None
