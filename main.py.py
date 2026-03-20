from fastapi import FastAPI
from pydantic import BaseModel
import uuid
from mangum import Mangum   # ✅ NEW

app = FastAPI()

campus_db = {}

class Campus(BaseModel):
    campus_name: str
    location: str
    total_hostels: int


@app.post("/campus/add")
async def add_campus(campus: Campus):
    campus_id = str(uuid.uuid4())

    campus_db[campus_id] = {
        "campus_id": campus_id,
        "campus_name": campus.campus_name,
        "location": campus.location,
        "total_hostels": campus.total_hostels,
        "hostels": {}
    }

    return {
        "message": "Campus added",
        "data": campus_db[campus_id]
    }

handler = Mangum(app)