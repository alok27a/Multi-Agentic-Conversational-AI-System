from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.text_to_sql_service import text_to_sql_service
import os
import shutil

router = APIRouter()

@router.post("/upload-docs", status_code=status.HTTP_200_OK, tags=["Documents"])
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        success = text_to_sql_service.load_csv_to_sql(file_path)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process and load CSV into database.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"message": f"Successfully uploaded and loaded {file.filename} into the SQL knowledge base."}

