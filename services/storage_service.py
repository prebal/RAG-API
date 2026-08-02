from fastapi import UploadFile
from models.document_model import Document
import aiofiles

CHUNKSIZE=1024*1024

class StorageService:
    async def save_file(self, uploaded_file: UploadFile, destination) -> None:

        full_destination = 

        async with aiofiles.open(full_destination, "wb") as saved_file:
            while chunk := await uploaded_file.read(CHUNKSIZE):
                await saved_file.write(chunk)

        return full_destination

    def delete_file(self, file_to_delete: Document) -> None
        pass
