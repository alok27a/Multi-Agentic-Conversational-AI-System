from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.rag_service import rag_service
import os
import shutil

router = APIRouter()

@router.post("/upload-docs", status_code=status.HTTP_200_OK, tags=["Documents"])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a CSV file to populate the RAG knowledge base.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only CSV files are accepted.",
        )
    
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        await rag_service.load_and_index_csv(file_path)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {e}",
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"message": f"Successfully uploaded and indexed {file.filename}."}

