from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
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

class Block(BaseModel):
    block_name: str

class Room(BaseModel):
    room_name: str
    capacity: int

class Student(BaseModel):
    name: str
    subjects: List[str]


# -----------------------------
# Campus APIs
# -----------------------------

@app.post("/campus/add",tags=["Campus"])
async def add_campus(campus: Campus):
    campus_id = str(uuid.uuid4())
    campus_db[campus_id] = {
        "campus_id": campus_id,
        "campus_name": campus.campus_name,
        "location": campus.location,
        "total_hostels": campus.total_hostels,
        "hostels": {}
    }
    return {"message": "Campus added", "data": campus_db[campus_id]}


@app.get("/campus",tags=["Campus"])
async def get_all_campus():
    return {"total": len(campus_db), "data": list(campus_db.values())}





@app.put("/campus/update/{campus_id}",tags=["Campus"])
async def update_campus(campus_id: str, campus: Campus):
    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")
    campus_db[campus_id].update(campus.dict())
    return {"message": "Updated", "data": campus_db[campus_id]}


@app.delete("/campus/delete/{campus_id}",tags=["Campus"])
async def delete_campus(campus_id: str):
    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")
    return {"message": "Deleted", "data": campus_db.pop(campus_id)}


# -----------------------------
# Hostel APIs
# -----------------------------


@app.get("/campus/{campus_id}/hostels",tags=["Hostel"])
async def get_hostels(campus_id: str):
    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")
    return list(campus_db[campus_id]["hostels"].values())




@app.put("/campus/{campus_id}/hostel/{hostel_id}",tags=["Hostel"])
async def update_hostel(campus_id: str, hostel_id: str, hostel: Hostel):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")

    campus_db[campus_id]["hostels"][hostel_id]["hostel_name"] = hostel.hostel_name
    return {"message": "Hostel updated", "data": campus_db[campus_id]["hostels"][hostel_id]}


@app.delete("/campus/{campus_id}/hostel/{hostel_id}",tags=["Hostel"])
async def delete_hostel(campus_id: str, hostel_id: str):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")

    return {"message": "Deleted", "data": campus_db[campus_id]["hostels"].pop(hostel_id)}


# -----------------------------
# Block APIs
# -----------------------------

@app.post("/campus/{campus_id}/hostel/{hostel_id}/block/add",tags=["Blocks"])
async def add_block(campus_id: str, hostel_id: str, block: Block):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")

    block_id = str(uuid.uuid4())

    campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id] = {
        "block_id": block_id,
        "block_name": block.block_name,
        "rooms": {}
    }

    return {"message": "Block added", "data": campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]}


@app.get("/campus/{campus_id}/hostel/{hostel_id}/blocks",tags=["Blocks"])
async def get_blocks(campus_id: str, hostel_id: str):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")

    blocks = campus_db[campus_id]["hostels"][hostel_id]["blocks"]
    return {"total": len(blocks), "data": list(blocks.values())}


@app.put("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}",tags=["Blocks"])
async def update_block(campus_id: str, hostel_id: str, block_id: str, block: Block):

    campus = campus_db.get(campus_id)
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")

    hostel = campus["hostels"].get(hostel_id)
    if not hostel:
        raise HTTPException(status_code=404, detail="Hostel not found")

    block_data = hostel["blocks"].get(block_id)
    if not block_data:
        raise HTTPException(status_code=404, detail="Block not found")

    block_data["block_name"] = block.block_name

    return {"message": "Block updated", "data": block_data}
@app.delete("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}",tags=["Blocks"])
async def delete_block(campus_id: str, hostel_id: str, block_id: str):

    # Check campus
    campus = campus_db.get(campus_id)
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")

    # Check hostel
    hostel = campus["hostels"].get(hostel_id)
    if not hostel:
        raise HTTPException(status_code=404, detail="Hostel not found")

    # Check block
    block = hostel["blocks"].get(block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")

    # Delete block
    del hostel["blocks"][block_id]

    return {"message": "Block deleted successfully"}

# -----------------------------
# Room APIs
# -----------------------------

@app.post("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}/room/add",tags=["room"])
async def add_room(campus_id: str, hostel_id: str, block_id: str, room: Room):

    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"] \
            or block_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"]:
        raise HTTPException(status_code=404, detail="Block not found")

    room_id = str(uuid.uuid4())
    existing_rooms = campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"]

    room_no = f"Room {len(existing_rooms) + 1}"

    existing_rooms[room_id] = {
        "room_id": room_id,
        "room_no": room_no,
        "capacity": room.capacity,
        "students": []
    }

    return {"message": "Room added", "data": existing_rooms[room_id]}


@app.get("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}/room/{room_id}",tags=["room"])
async def get_room_by_id(campus_id: str, hostel_id: str, block_id: str, room_id: str):

    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"] \
            or block_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"] \
            or room_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"]:
        raise HTTPException(status_code=404, detail="Room not found")

    return campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"][room_id]


@app.put("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}/room/{room_id}",tags=["room"])
async def update_room(campus_id: str, hostel_id: str, block_id: str, room_id: str, room: Room):
    if campus_id not in campus_db \
            or hostel_id not in campus_db[campus_id]["hostels"] \
            or block_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"] \
            or room_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"]:
        raise HTTPException(status_code=404, detail="Room not found")

    room_data = campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"][room_id]

    room_data["capacity"] = room.capacity

    return {"message": "Room updated", "data": room_data}


@app.delete("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}/room/{room_id}",tags=["room"])
async def delete_room(campus_id: str, hostel_id: str, block_id: str, room_id: str):

    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"] \
            or block_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"] \
            or room_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"]:
        raise HTTPException(status_code=404, detail="Room not found")

    return {"message": "Deleted", "data": campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"].pop(room_id)}


# -----------------------------
# Student + Waitlist
# -----------------------------
@app.post("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}/room/{room_id}/student/add")
async def add_student(campus_id: str, hostel_id: str, block_id: str, room_id: str, student: Student):

    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")

    hostel = campus_db[campus_id]["hostels"][hostel_id]

    if block_id not in hostel["blocks"] or room_id not in hostel["blocks"][block_id]["rooms"]:
        raise HTTPException(status_code=404, detail="Room not found")

    room = hostel["blocks"][block_id]["rooms"][room_id]

    student_id = str(uuid.uuid4())

    student_data = {
        "student_id": student_id,
        "name": student.name,
        "subjects": student.subjects
    }

    # ✅ Check ROOM capacity (IMPORTANT FIX)
    if len(room["students"]) >= room["capacity"]:
        hostel["waitlist"].append(student_data)

        return {
            "message": "Room full → added to waitlist",
            "data": student_data
        }

    @app.post("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}/room/{room_id}/student/add")
    async def add_student(campus_id: str, hostel_id: str, block_id: str, room_id: str, student: Student):

        # ✅ Validate hierarchy
        if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
            raise HTTPException(status_code=404, detail="Hostel not found")

        hostel = campus_db[campus_id]["hostels"][hostel_id]

        if block_id not in hostel["blocks"] or room_id not in hostel["blocks"][block_id]["rooms"]:
            raise HTTPException(status_code=404, detail="Room not found")

        room = hostel["blocks"][block_id]["rooms"][room_id]

        # ✅ Create student
        student_id = str(uuid.uuid4())

        student_data = {
            "student_id": student_id,
            "name": student.name,
            "subjects": student.subjects
        }

        # ✅ Check ROOM capacity
        if len(room["students"]) >= room["capacity"]:
            hostel["waitlist"].append(student_data)

            return {
                "message": "Room full → added to waitlist",
                "data": student_data
            }

        # ✅ Add student to room
        room["students"].append(student_data)
        hostel["total_students"] += 1

        return {
            "message": "Student added to room",
            "data": student_data
        }
    # ✅ Add to room
    room["students"].append(student_data)
    hostel["total_students"] += 1

    return {
        "message": "Student added to room",
        "data": student_data
    }


@app.get("/campus/{campus_id}/hostel/{hostel_id}/waitlist")
async def get_waitlist(campus_id: str, hostel_id: str):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")

    hostel = campus_db[campus_id]["hostels"][hostel_id]
    return {"total": len(hostel["waitlist"]), "waitlist": hostel["waitlist"]}


