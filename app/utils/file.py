import io
import os
import shutil
import uuid
from datetime import datetime

import numpy as np  # type: ignore
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError  # type: ignore

# ALLOWED_MIME = {
#     "image/jpeg": ".jpg",
#     "image/png": ".png",
#     "application/pdf": ".pdf"
# }
MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB


async def generate_file_path(file_name: str, file_type: str = "images") -> str:
    root_dir = os.path.abspath(".")

    now = datetime.now()
    re_path = "{}/{}/{}/{}/{}/".format("static/media", file_type, now.year, now.month, now.day)

    path = os.path.join(root_dir, re_path)
    os.makedirs(path, exist_ok=True)

    return f"{re_path}{file_name}"


async def save_resize_image(im, filename: str):
    file_name, ext = os.path.splitext(filename)
    # print(file_name)
    # print(ext)
    # print(im.size)

    width, height = im.size

    if width >= 1280:
        size_defined = 1280, 720
    elif width >= 640:
        size_defined = 640, 480
    else:
        size_defined = im.size

    f_name = await generate_file_path(f"{str(uuid.uuid4())}{ext}")
    im.thumbnail(size_defined)
    # im.save(f_name, 'JPEG', quality=70)
    im.save(f_name, 'JPEG', optimize=True)

    return f_name


async def save_center_crop(image: Image.Image, size: int, filename: str) -> Image.Image:
    file_name, ext = os.path.splitext(filename)

    # Resize gambar proporsional agar sisi terpendek >= target size
    width, height = image.size
    scale = size / min(width, height)
    new_size = (int(width * scale), int(height * scale))
    image = image.resize(new_size, Image.LANCZOS)

    # Hitung crop box dari tengah
    left = (image.width - size) // 2
    top = (image.height - size) // 2
    right = left + size
    bottom = top + size

    # Crop tengah
    cropped_image = image.crop((left, top, right, bottom))

    f_name = await generate_file_path(f"{str(uuid.uuid4())}{ext}")
    cropped_image.save(f_name, 'JPEG', optimize=True)

    return f_name


async def upload_image_crop(
    file: UploadFile
) -> str:
    try:
        im = Image.open(io.BytesIO(await file.read())).convert("RGB")

        f_name = await save_center_crop(im, 256, file.filename)

        return f_name
    except Exception as e:
        # raise Exception(str(e))
        raise Exception("Please make sure the file is an image file")


async def upload_image(
    file: UploadFile
) -> str:
    try:
        im = Image.open(io.BytesIO(await file.read())).convert("RGB")
        # with Image.open(file.file) as im:
        #     if im.mode in ("RGBA", "P", "L"):
        #         im = im.convert("RGB")

        f_name = await save_resize_image(im, file.filename)

        return f_name
    except Exception as e:
        # raise Exception(str(e))
        raise Exception("Please make sure the file is an image file")


async def upload_file(
    file: UploadFile
) -> str:
    content_type = file.content_type
    contents = await file.read()
    _, ext = os.path.splitext(file.filename)

    # Validasi ukuran file
    if len(contents) > MAX_FILE_SIZE:
        raise Exception("File size exceeds 30MB limit.")

    # Cek apakah file adalah image
    if "image" in content_type:
        im = Image.open(io.BytesIO(contents)).convert("RGB")
        file_location = await save_resize_image(im, file.filename)
    else:
        file_location = await generate_file_path(f"{str(uuid.uuid4())}{ext}", "files")
        # Kalau bukan image → simpan apa adanya
        with open(file_location, "wb") as f:
            f.write(contents)

    return file_location
