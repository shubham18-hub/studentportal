from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models.task import (
    Task, TaskCreate, TaskUpdate, WorkflowStage,
    Submission, SubmissionCreate, SubmissionGrade, SubmissionStatus
)
from app.models.auth import TokenData
from app.security import verify_token, verify_admin_token
from app.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# ====================
# Task Management (Admin)
# ====================

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    token_data: TokenData = Depends(verify_admin_token),
    db=Depends(get_db)
):
    """Create a new task (admin only)."""
    tasks_collection = db["tasks"]
    
    task_doc = {
        **task.model_dump(),
        "stage": task.stage.value,
        "created_by": token_data.email,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await tasks_collection.insert_one(task_doc)
    task_doc["_id"] = str(result.inserted_id)
    
    return {"id": str(result.inserted_id), "message": "Task created successfully"}

@router.get("/admin/all", response_model=List[dict])
async def get_all_tasks(
    stage: Optional[WorkflowStage] = Query(None),
    token_data: TokenData = Depends(verify_admin_token),
    db=Depends(get_db)
):
    """Get all tasks (admin only)."""
    tasks_collection = db["tasks"]
    
    query = {}
    if stage:
        query["stage"] = stage.value
    
    tasks = []
    async for task in tasks_collection.find(query).sort("deadline", 1):
        task["_id"] = str(task["_id"])
        task["id"] = task["_id"]
        tasks.append(task)
    
    return tasks

@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: str, token_data: TokenData = Depends(verify_token), db=Depends(get_db)):
    """Get task details."""
    tasks_collection = db["tasks"]
    
    try:
        task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    task["_id"] = str(task["_id"])
    task["id"] = task["_id"]
    return task

@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    token_data: TokenData = Depends(verify_admin_token),
    db=Depends(get_db)
):
    """Update a task (admin only)."""
    tasks_collection = db["tasks"]
    
    try:
        task_oid = ObjectId(task_id)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    result = await tasks_collection.update_one(
        {"_id": task_oid},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return {"message": "Task updated successfully"}

@router.delete("/{task_id}", response_model=dict)
async def delete_task(
    task_id: str,
    token_data: TokenData = Depends(verify_admin_token),
    db=Depends(get_db)
):
    """Delete a task (admin only)."""
    tasks_collection = db["tasks"]
    
    try:
        task_oid = ObjectId(task_id)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    result = await tasks_collection.delete_one({"_id": task_oid})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return {"message": "Task deleted successfully"}

# ====================
# Task Browsing (Participants)
# ====================

@router.get("/participant/by-stage/{stage}", response_model=List[dict])
async def get_tasks_by_stage(
    stage: WorkflowStage,
    token_data: TokenData = Depends(verify_token),
    db=Depends(get_db)
):
    """Get tasks for a specific workflow stage."""
    tasks_collection = db["tasks"]
    
    tasks = []
    async for task in tasks_collection.find({"stage": stage.value}).sort("deadline", 1):
        task["_id"] = str(task["_id"])
        task["id"] = task["_id"]
        tasks.append(task)
    
    return tasks

@router.get("/participant/all", response_model=List[dict])
async def get_all_participant_tasks(
    token_data: TokenData = Depends(verify_token),
    db=Depends(get_db)
):
    """Get all tasks for participant with submission status."""
    tasks_collection = db["tasks"]
    submissions_collection = db["submissions"]
    
    user_id = token_data.user_id
    tasks = []
    
    async for task in tasks_collection.find().sort("deadline", 1):
        task["_id"] = str(task["_id"])
        task["id"] = task["_id"]
        
        # Get submission status for this user
        submission = await submissions_collection.find_one({
            "task_id": task["_id"],
            "user_id": user_id
        })
        
        if submission:
            task["submission_status"] = submission.get("status", "Not Submitted")
            task["submission_id"] = str(submission["_id"])
        else:
            task["submission_status"] = "Not Submitted"
            task["submission_id"] = None
        
        tasks.append(task)
    
    return tasks

# ====================
# Submissions
# ====================

@router.post("/submissions/{task_id}", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_submission(
    task_id: str,
    submission: SubmissionCreate,
    token_data: TokenData = Depends(verify_token),
    db=Depends(get_db)
):
    """Create or update a submission."""
    try:
        task_oid = ObjectId(task_id)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    tasks_collection = db["tasks"]
    submissions_collection = db["submissions"]
    
    # Verify task exists
    task = await tasks_collection.find_one({"_id": task_oid})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    user_id = token_data.user_id
    
    # Check if submission already exists
    existing = await submissions_collection.find_one({
        "task_id": task_id,
        "user_id": user_id
    })
    
    submission_doc = {
        "task_id": task_id,
        "user_id": user_id,
        "file_name": submission.file_name,
        "status": SubmissionStatus.SUBMITTED.value,
        "submitted_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    if existing:
        # Update existing submission
        result = await submissions_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": submission_doc}
        )
        submission_id = str(existing["_id"])
    else:
        submission_doc["created_at"] = datetime.utcnow()
        result = await submissions_collection.insert_one(submission_doc)
        submission_id = str(result.inserted_id)
    
    return {
        "id": submission_id,
        "message": "Submission created successfully"
    }

@router.get("/submissions/{task_id}", response_model=Optional[dict])
async def get_submission(
    task_id: str,
    token_data: TokenData = Depends(verify_token),
    db=Depends(get_db)
):
    """Get submission for current user on a task."""
    submissions_collection = db["submissions"]
    user_id = token_data.user_id
    
    submission = await submissions_collection.find_one({
        "task_id": task_id,
        "user_id": user_id
    })
    
    if submission:
        submission["_id"] = str(submission["_id"])
        submission["id"] = submission["_id"]
    
    return submission

@router.get("/admin/submissions/{task_id}", response_model=List[dict])
async def get_task_submissions(
    task_id: str,
    token_data: TokenData = Depends(verify_admin_token),
    db=Depends(get_db)
):
    """Get all submissions for a task (admin only)."""
    submissions_collection = db["submissions"]
    
    submissions = []
    async for submission in submissions_collection.find({"task_id": task_id}):
        submission["_id"] = str(submission["_id"])
        submission["id"] = submission["_id"]
        submissions.append(submission)
    
    return submissions

@router.post("/submissions/{submission_id}/grade", response_model=dict)
async def grade_submission(
    submission_id: str,
    grade: SubmissionGrade,
    token_data: TokenData = Depends(verify_admin_token),
    db=Depends(get_db)
):
    """Grade a submission (admin only)."""
    submissions_collection = db["submissions"]
    
    try:
        submission_oid = ObjectId(submission_id)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    
    update_data = {
        "status": SubmissionStatus.GRADED.value,
        "points": grade.points,
        "feedback": grade.feedback,
        "graded_by": token_data.email,
        "graded_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await submissions_collection.update_one(
        {"_id": submission_oid},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    
    return {"message": "Submission graded successfully"}

@router.get("/admin/analytics", response_model=dict)
async def get_analytics(
    token_data: TokenData = Depends(verify_admin_token),
    db=Depends(get_db)
):
    """Get task and submission analytics (admin only)."""
    tasks_collection = db["tasks"]
    submissions_collection = db["submissions"]
    
    total_tasks = await tasks_collection.count_documents({})
    total_submissions = await submissions_collection.count_documents({})
    graded_submissions = await submissions_collection.count_documents(
        {"status": SubmissionStatus.GRADED.value}
    )
    
    # Get submissions by status
    status_counts = {}
    for status_value in [s.value for s in SubmissionStatus]:
        count = await submissions_collection.count_documents({"status": status_value})
        status_counts[status_value] = count
    
    return {
        "total_tasks": total_tasks,
        "total_submissions": total_submissions,
        "graded_submissions": graded_submissions,
        "pending_grading": total_submissions - graded_submissions,
        "submission_status_breakdown": status_counts
    }
