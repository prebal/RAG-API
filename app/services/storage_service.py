import os
import uuid

import aiofiles
from fastapi import UploadFile

CHUNKSIZE = 1024 * 1024
LOCAL_STORAGE_PATH = "storage/"


class StorageService:
    async def save_document_storage(self, uploaded_file: UploadFile) -> None:
        file_format = str(uploaded_file.filename).split(".")[-1].lower()
        full_destination = LOCAL_STORAGE_PATH + str(uuid.uuid4()) + "." + file_format
        async with aiofiles.open(full_destination, "wb") as saved_file:
            while chunk := await uploaded_file.read(CHUNKSIZE):
                await saved_file.write(chunk)

        return full_destination

    def remove_document_storage(self, file_to_delete: str) -> None:
        os.remove(file_to_delete)
