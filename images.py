import os
import uuid
from pathlib import Path
from fastapi import UploadFile

STORE_IMG = "upload"

Path(STORE_IMG).mkdir(parents=True, exist_ok=True)

async def upload_file(file: UploadFile):
    content = await file.read()
    filename_org = file.filename
    filename = f"{uuid.uuid4()}_{filename_org}"
    file_path = os.path.join(STORE_IMG, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": filename_org,
        "url": f"{os.getcwd()}{file_path}",
        "original name": filename_org,
        "size": os.path.getsize(file_path),
    }