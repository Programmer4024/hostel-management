from fastapi import FastAPI,HTTPException,File,Upload_File
from fastapi.responses import FileResponse
import os
import boto3
app=FastAPI(title="upload and download the file")
AWS_ACCESS_KEY=""
AWS_SECRET_KEY=""
BUCKET_NAME=""
REGION=""
s3_client=boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)
@app.post("/upload")
async def UploadFile(file:UploadFile=File(...)):
    try:
        s3_client.fileobj(
            file.file,
            BUCKET_NAME,
            file.filename
        )
        return{
            "message":"file uploaded successfully",

        }
    except Exception as e:
       raise HTTPException(status_code=400,detail=str(e))
@app.get("/download file")
async def download_file(filename:str):
    local_file_path=f"temp_{filename}"
    try:
        s3_client.download_file(BUCKET_NAME,filename,local_file_path)
        return FileResponse(local_file_path,filename=filename)
    except s3_client.exception.NoSuchKey:
        raise HTTPException(status_code=404,detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
