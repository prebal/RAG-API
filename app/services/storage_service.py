import os
import uuid

import aiofiles
from fastapi import UploadFile

from app.settings import get_settings

CHUNKSIZE = 1024 * 1024


class StorageService:
    async def save_document_storage(self, uploaded_file: UploadFile) -> str:
        file_format = str(uploaded_file.filename).split(".")[-1].lower()
        full_destination = (
            f"{get_settings().storage}/{uuid.uuid4()}.{file_format}"
        )
        async with aiofiles.open(full_destination, "wb") as saved_file:
            while chunk := await uploaded_file.read(CHUNKSIZE):
                await saved_file.write(chunk)

        return full_destination

    def remove_document_storage(self, file_to_delete: str) -> None:
        os.remove(file_to_delete)
