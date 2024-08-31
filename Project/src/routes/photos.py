from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import cloudinary
import cloudinary.uploader
import cloudinary.api

from Project.src.entity.models import Post
from Project.src.database.db import get_db

router = APIRouter()

@router.post("/upload_photo/")
async def upload_photo(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    try:
        result = cloudinary.uploader.upload(file.file)
        file_url = result.get("url")

        new_post = Post(description=file.filename, url=file_url)
        db.add(new_post)
        await db.commit()

        return {"filename": file.filename, "file_url": file_url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))