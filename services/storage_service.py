from fastapi import UploadFile
from models.document_model import Document
import aiofiles
import uuid
import os

CHUNKSIZE=1024*1024
LOCAL_STORAGE_PATH = "storage/"

class StorageService:
    async def save_file(self, uploaded_file: UploadFile, destination: str) -> None:
        full_destination = LOCAL_STORAGE_PATH + str(uuid.uuid4())
        async with aiofiles.open(full_destination, "wb") as saved_file:
            while chunk := await uploaded_file.read(CHUNKSIZE):
                await saved_file.write(chunk)

        return full_destination

    def delete_file(self, file_to_delete: str) -> None
        os.delete(file_to_delete)
