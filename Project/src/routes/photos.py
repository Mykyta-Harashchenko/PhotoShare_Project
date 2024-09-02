import os
import qrcode
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader
import cloudinary.api
import io
from sqlalchemy import select

from Project.src.entity.models import Post, Role, User, Tag
from Project.src.database.db import get_db
from Project.src.schemas.photos import PostCreate
from Project.src.services.roles import RoleChecker
from Project.src.services.dependencies import get_current_user


router = APIRouter(tags=['photos'])

cloudinary.config(
    cloud_name=os.environ.get("CLD_NAME"),
    api_key=os.environ.get("CLD_API_KEY"),
    api_secret=os.environ.get("CLD_API_SECRET")
)

@router.post("/upload/",
             dependencies=[Depends(RoleChecker([Role.user, Role.admin, Role.moderator]))],
             response_model=PostCreate,)
async def upload_file(description: str,
                      file: UploadFile = File(...),
                      tags: list[str] = Query(...),
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

        for tag_name in tags:
            existing_tag = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = existing_tag.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)
            db_file.tags.append(tag)

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


@router.post("/resize_image/{post_id}")
async def resize_image(
    post_id: int,
    width: int,
    height: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Resize an image associated with a given post ID and create a new post with the resized image and a QR code.

    This endpoint resizes an existing image from a specified post to the given width and height using Cloudinary.
    It then generates a QR code for the resized image URL and uploads both the resized image and the QR code to Cloudinary.
    A new post is created in the database with the resized image URL and the QR code URL.

    Parameters:
    - post_id (int): The ID of the post containing the image to be resized.
    - width (int): The new width for the image.
    - height (int): The new height for the image.
    - db (AsyncSession): The database session for executing queries.
    - current_user (User): The currently authenticated user making the request.

    Returns:
    - dict: A dictionary containing the URLs of the resized image and its QR code.

    Raises:
    - HTTPException: If the post is not found, returns a 404 error.
    - HTTPException: If an error occurs during the processing, returns a 500 error.
    """
    try:
        query = select(Post).where(Post.id == post_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        resized_result = cloudinary.uploader.upload(post.url, folder=current_user.email, transformation=[
            {"width": width, "height": height, "crop": "fill"}
        ])
        resized_url = resized_result["secure_url"]

        qr_buffer = io.BytesIO()
        qrcode.make(resized_url).save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_result = cloudinary.uploader.upload(qr_buffer, folder=current_user.email + "/qr_codes")
        qr_secure_url = qr_result["secure_url"]

        new_post = Post(
            url=resized_url,
            description="origin: " + post.url,
            qr_code=qr_secure_url,
            owner_id=post.owner_id
        )

        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)

        return {"url": resized_url, "qr_url": qr_secure_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crop_image/{post_id}")
async def crop_image(
    post_id: int,
    width: int,
    height: int,
    x: int,
    y: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crop an image associated with a given post ID and create a new post with the cropped image and a QR code.

    This endpoint crops an existing image from a specified post to the given width and height starting from (x, y) coordinates using Cloudinary.
    It then generates a QR code for the cropped image URL and uploads both the cropped image and the QR code to Cloudinary.
    A new post is created in the database with the cropped image URL and the QR code URL.

    Parameters:
    - post_id (int): The ID of the post containing the image to be cropped.
    - width (int): The width for the cropped image.
    - height (int): The height for the cropped image.
    - x (int): The x-coordinate for the cropping starting point.
    - y (int): The y-coordinate for the cropping starting point.
    - db (AsyncSession): The database session for executing queries.
    - current_user (User): The currently authenticated user making the request.

    Returns:
    - dict: A dictionary containing the URLs of the cropped image and its QR code.

    Raises:
    - HTTPException: If the post is not found, returns a 404 error.
    - HTTPException: If an error occurs during the processing, returns a 500 error.
    """
    try:
        query = select(Post).where(Post.id == post_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        cropped_result = cloudinary.uploader.upload(post.url, folder=current_user.email, transformation=[
            {"width": width, "height": height, "crop": "crop", "x": x, "y": y}
        ])
        cropped_url = cropped_result["secure_url"]

        qr_buffer = io.BytesIO()
        qrcode.make(cropped_url).save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_result = cloudinary.uploader.upload(qr_buffer, folder=current_user.email + "/qr_codes")
        qr_secure_url = qr_result["secure_url"]

        new_post = Post(
            url=cropped_url,
            description="cropped from: " + post.url,
            qr_code=qr_secure_url,
            owner_id=post.owner_id
        )

        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)

        return {"url": cropped_url, "qr_url": qr_secure_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rotate_image/{post_id}")
async def rotate_image(
    post_id: int,
    angle: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rotate an image associated with a given post ID and create a new post with the rotated image and a QR code.

    This endpoint rotates an existing image from a specified post by the given angle using Cloudinary.
    It then generates a QR code for the rotated image URL and uploads both the rotated image and the QR code to Cloudinary.
    A new post is created in the database with the rotated image URL and the QR code URL.

    Parameters:
    - post_id (int): The ID of the post containing the image to be rotated.
    - angle (int): The angle in degrees to rotate the image.
    - db (AsyncSession): The database session for executing queries.
    - current_user (User): The currently authenticated user making the request.

    Returns:
    - dict: A dictionary containing the URLs of the rotated image and its QR code.

    Raises:
    - HTTPException: If the post is not found, returns a 404 error.
    - HTTPException: If an error occurs during the processing, returns a 500 error.
    """
    try:
        query = select(Post).where(Post.id == post_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        rotated_result = cloudinary.uploader.upload(post.url, folder=current_user.email, transformation=[
            {"angle": angle}
        ])
        rotated_url = rotated_result["secure_url"]

        qr_buffer = io.BytesIO()
        qrcode.make(rotated_url).save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_result = cloudinary.uploader.upload(qr_buffer, folder=current_user.email + "/qr_codes")
        qr_secure_url = qr_result["secure_url"]

        new_post = Post(
            url=rotated_url,
            description="rotated from: " + post.url,
            qr_code=qr_secure_url,
            owner_id=post.owner_id
        )

        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)

        return {"url": rotated_url, "qr_url": qr_secure_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply_effect/{post_id}")
async def apply_effect(
    post_id: int,
    effect: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apply an effect to an image associated with a given post ID and create a new post with the modified image and a QR code.

    This endpoint applies a specified effect to an existing image from a specified post using Cloudinary.
    It then generates a QR code for the modified image URL and uploads both the modified image and the QR code to Cloudinary.
    A new post is created in the database with the modified image URL and the QR code URL.

    Parameters:
    - post_id (int): The ID of the post containing the image to which the effect will be applied.
    - effect (str): The effect to apply to the image (e.g., "sepia", "grayscale", "blur:300").
    - db (AsyncSession): The database session for executing queries.
    - current_user (User): The currently authenticated user making the request.

    Returns:
    - dict: A dictionary containing the URLs of the modified image and its QR code.

    Raises:
    - HTTPException: If the post is not found, returns a 404 error.
    - HTTPException: If an error occurs during the processing, returns a 500 error.
    """
    try:
        query = select(Post).where(Post.id == post_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        effect_result = cloudinary.uploader.upload(post.url, folder=current_user.email, transformation=[
            {"effect": effect}
        ])
        effect_url = effect_result["secure_url"]

        qr_buffer = io.BytesIO()
        qrcode.make(effect_url).save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_result = cloudinary.uploader.upload(qr_buffer, folder=current_user.email + "/qr_codes")
        qr_secure_url = qr_result["secure_url"]

        new_post = Post(
            url=effect_url,
            description=f"effect ({effect}) applied to: " + post.url,
            qr_code=qr_secure_url,
            owner_id=post.owner_id
        )

        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)

        return {"url": effect_url, "qr_url": qr_secure_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))