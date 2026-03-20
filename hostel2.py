from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()

campus_db = {}

# -----------------------------
# Models
# -----------------------------

class Campus(BaseModel):
    campus_name: str
    location: str
    total_hostels: int


class Hostel(BaseModel):
    hostel_name: str


# -----------------------------
# Campus APIs
# -----------------------------

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
        "message": "Campus added successfully",
        "data": campus_db[campus_id]
    }


@app.get("/campus")
async def get_all_campus():

    return {
        "total_campus": len(campus_db),
        "campus": list(campus_db.values())
    }


@app.get("/campus/{campus_id}")
async def get_campus(campus_id: str):

    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")

    return campus_db[campus_id]


@app.put("/campus/update/{campus_id}")
async def update_campus(campus_id: str, campus: Campus):

    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")

    campus_db[campus_id]["campus_name"] = campus.campus_name
    campus_db[campus_id]["location"] = campus.location
    campus_db[campus_id]["total_hostels"] = campus.total_hostels

    return {
        "message": "Campus updated successfully",
        "data": campus_db[campus_id]
    }


@app.delete("/campus/delete/{campus_id}")
async def delete_campus(campus_id: str):

    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")

    deleted = campus_db.pop(campus_id)

    return {
        "message": "Campus deleted successfully",
        "data": deleted
    }


# -----------------------------
# Hostel APIs
# -----------------------------

@app.post("/campus/{campus_id}/hostel/add")
async def add_hostel(campus_id: str, hostel: Hostel):

    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")

    hostel_id = str(uuid.uuid4())

    campus_db[campus_id]["hostels"][hostel_id] = {
        "hostel_id": hostel_id,
        "hostel_name": hostel.hostel_name
    }

    return {
        "message": "Hostel added successfully",
        "data": campus_db[campus_id]["hostels"][hostel_id]
    }


@app.get("/campus/{campus_id}/hostels")
async def get_hostels(campus_id: str):

    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")

    hostels = campus_db[campus_id]["hostels"]

    return {
        "total_hostels": len(hostels),
        "hostels": list(hostels.values())
    }


@app.put("/campus/{campus_id}/hostel/{hostel_id}")
async def update_hostel(campus_id: str, hostel_id: str, hostel: Hostel):

    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")

    if hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")

    campus_db[campus_id]["hostels"][hostel_id]["hostel_name"] = hostel.hostel_name

    return {
        "message": "Hostel updated successfully",
        "data": campus_db[campus_id]["hostels"][hostel_id]
    }


@app.delete("/campus/{campus_id}/hostel/{hostel_id}")
async def delete_hostel(campus_id: str, hostel_id: str):

    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")

    if hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")

    deleted = campus_db[campus_id]["hostels"].pop(hostel_id)

    return {
        "message": "Hostel deleted successfully",
        "data": deleted
    }
@app.get("/hostels")
async def get_all_hostels():

    all_hostels = []

    for campus in campus_db.values():
        for hostel in campus["hostels"].values():
            all_hostels.append(hostel)

    return {
        "total_hostels": len(all_hostels),
        "hostels": all_hostels
    }