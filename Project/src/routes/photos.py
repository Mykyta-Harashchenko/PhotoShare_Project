import os
import qrcode
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader
import cloudinary.api
import io
from sqlalchemy import select

from Project.src.entity.models import Post, Role, User
from Project.src.database.db import get_db
from Project.src.services.roles import RoleChecker
from Project.src.services.dependencies import get_current_user


router = APIRouter()

cloudinary.config(
    cloud_name=os.environ.get("CLD_NAME"),
    api_key=os.environ.get("CLD_API_KEY"),
    api_secret=os.environ.get("CLD_API_SECRET")
)

@router.post("/upload/",
             dependencies=[Depends(RoleChecker([Role.user, Role.admin, Role.moderator]))])
async def upload_file(description: str = Form(...),
                      file: UploadFile = File(...),
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)) -> dict:
    """
    Uploads a file to Cloudinary and generates a QR code for the uploaded file's URL.

    This endpoint allows users with specific roles (user, admin, moderator) to upload a file to Cloudinary.
    After uploading the file, a QR code is generated for the file's URL and also uploaded to Cloudinary.
    The URLs of both the original file and the QR code are saved in the database.

    :param description: A description for the uploaded file.
    :type description: str
    :param file: The file to be uploaded.
    :type file: UploadFile
    :param folder: The folder in Cloudinary where the file will be uploaded.
    :type folder: str, optional
    :param db: The database session to use for database operations.
    :type db: AsyncSession
    :param current_user: The current user making the request.
    :type current_user: User
    :return: A dictionary containing the URLs of the uploaded file and its QR code.
    :rtype: dict
    :raises HTTPException: If there is an error during file upload or database operations, an HTTPException with status 500 is raised.
    """
    try:
        result = cloudinary.uploader.upload(file.file, folder=current_user.email)
        secure_url = result["secure_url"]

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(secure_url)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        qr_buffer = io.BytesIO()
        qr_image.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_result = cloudinary.uploader.upload(qr_buffer, folder=current_user.email + "/qr_codes")
        qr_secure_url = qr_result["secure_url"]

        db_file = Post(url=secure_url,
                       description=description,
                       qr_code=qr_secure_url,
                       owner_id=current_user.id)

        db.add(db_file)
        await db.commit()
        await db.refresh(db_file)

        return {"url": secure_url, "qr_url": qr_secure_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_qr_code/{post_id}")
async def get_qr_code(post_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    """
    Retrieves the QR code URL for a specific post by its ID.

    This endpoint fetches a post from the database by its ID and returns the URL of the associated QR code.

    :param post_id: The ID of the post to retrieve the QR code for.
    :type post_id: int
    :param db: The database session to use for database operations.
    :type db: AsyncSession
    :return: A dictionary containing the URL of the QR code.
    :rtype: dict
    :raises HTTPException: If the post with the given ID is not found, an HTTPException with status 404 is raised.
                           If there is any other error, an HTTPException with status 500 is raised.
    """
    try:
        query = select(Post).where(Post.id == post_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"qr_code_url": post.qr_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))