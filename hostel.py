from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import uuid
app=FastAPI()
campus_db={}
class Campus(BaseModel):
    campus_name:str
    location:str
    total_hostels:int
@app.post("/campus/add")
async def campus(campus:Campus):
    campus_id=str(uuid.uuid4())
    campus_db[campus_id]={

    "campus_id":campus_id,
        "campus_name":campus.campus_name,
        "location":campus.location,
        "total_hostels":campus.total_hostels
    }
    return{
        "message":"campus added successfully",
        "data":campus_db[campus_id]
    }
@app.get("/campus")
async def get_campus():
    return{
        "total_campus":len(campus_db),
        "campus":list(campus_db.values())
    }
@app.put("/campus/{campus_id}")
async def get_campus(campus_id:str):
    if campus_id not in campus_db:
        raise HTTPException(status_code=404,detail="campus not found")
    return campus_db[campus_id]
@app.put("/campus/update/{campus_id}")
async def update_campus(campus_id:str,campus:Campus):
    if campus_id not in campus_db:
        raise HTTPException(status_code=404,detail="campus not found")
    campus_db[campus_id]["campus_name"]=campus.campus_name
    campus_db[campus_id]["location"]=campus.location
    campus_db[campus_id]["total_hostels"]=campus.total_hostels
    return{
        "message":"campus updated successfully",
        "data":campus_db[campus_id]
    }
@app.delete("/campus/delete/{campus_id}")
async def delete_campus(campus_id: str):

    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")

    deleted = campus_db.pop(campus_id)

    return {
        "message": "campus deleted successfully",
        "data": deleted
    }