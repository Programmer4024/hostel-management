from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()

campus_db = {}

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
    return {"message": "Campus added successfully", "data": campus_db[campus_id]}

@app.get("/campus")
async def get_all_campus():
    return {"total_campus": len(campus_db), "campus": list(campus_db.values())}

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
    return {"message": "Campus updated successfully", "data": campus_db[campus_id]}

@app.delete("/campus/delete/{campus_id}")
async def delete_campus(campus_id: str):
    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")
    deleted = campus_db.pop(campus_id)
    return {"message": "Campus deleted successfully", "data": deleted}


@app.post("/campus/{campus_id}/hostel/add")
async def add_hostel(campus_id: str, hostel: Hostel):
    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")
    hostel_id = str(uuid.uuid4())
    campus_db[campus_id]["hostels"][hostel_id] = {
        "hostel_id": hostel_id,
        "hostel_name": hostel.hostel_name,
        "blocks": {}
    }
    return {"message": "Hostel added successfully", "data": campus_db[campus_id]["hostels"][hostel_id]}

@app.get("/campus/{campus_id}/hostels")
async def get_hostels(campus_id: str):
    if campus_id not in campus_db:
        raise HTTPException(status_code=404, detail="Campus not found")
    hostels = campus_db[campus_id]["hostels"]
    return {"total_hostels": len(hostels), "hostels": list(hostels.values())}

@app.get("/campus/{campus_id}/hostel/{hostel_id}")
async def get_hostel_by_id(campus_id: str, hostel_id: str):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")
    return campus_db[campus_id]["hostels"][hostel_id]

@app.put("/campus/{campus_id}/hostel/{hostel_id}")
async def update_hostel(campus_id: str, hostel_id: str, hostel: Hostel):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")
    campus_db[campus_id]["hostels"][hostel_id]["hostel_name"] = hostel.hostel_name
    return {"message": "Hostel updated successfully", "data": campus_db[campus_id]["hostels"][hostel_id]}

@app.delete("/campus/{campus_id}/hostel/{hostel_id}")
async def delete_hostel(campus_id: str, hostel_id: str):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")
    deleted = campus_db[campus_id]["hostels"].pop(hostel_id)
    return {"message": "Hostel deleted successfully", "data": deleted}


@app.post("/campus/{campus_id}/hostel/{hostel_id}/block/add")
async def add_block(campus_id: str, hostel_id: str, block: Block):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")
    block_id = str(uuid.uuid4())
    campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id] = {
        "block_id": block_id,
        "block_name": block.block_name,
        "rooms": {}
    }
    return {"message": "Block added successfully", "data": campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]}

@app.get("/campus/{campus_id}/hostel/{hostel_id}/blocks")
async def get_blocks(campus_id: str, hostel_id: str):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"]:
        raise HTTPException(status_code=404, detail="Hostel not found")
    blocks = campus_db[campus_id]["hostels"][hostel_id]["blocks"]
    return {"total_blocks": len(blocks), "blocks": list(blocks.values())}

@app.put("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}")
async def update_block(campus_id: str, hostel_id: str, block_id: str, block: Block):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"] or block_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"]:
        raise HTTPException(status_code=404, detail="Block not found")
    campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["block_name"] = block.block_name
    return {"message": "Block updated successfully", "data": campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]}

@app.delete("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}")
async def delete_block(campus_id: str, hostel_id: str, block_id: str):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"] or block_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"]:
        raise HTTPException(status_code=404, detail="Block not found")
    deleted = campus_db[campus_id]["hostels"][hostel_id]["blocks"].pop(block_id)
    return {"message": "Block deleted successfully", "data": deleted}


@app.post("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}/room/add")
async def add_room(campus_id: str, hostel_id: str, block_id: str, room: Room):
    # Check hierarchy
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"] or block_id not in \
            campus_db[campus_id]["hostels"][hostel_id]["blocks"]:
        raise HTTPException(status_code=404, detail="Block not found")

    room_id = str(uuid.uuid4())


    existing_rooms = campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id].get("rooms", {})
    room_no = f"Room {len(existing_rooms) + 1}"  # Room 1, Room 2, ...

    # Add room
    campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id].setdefault("rooms", {})
    campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"][room_id] = {
        "room_id": room_id,
        "room_no": room_no,
        "capacity": room.capacity
    }

    return {
        "message": "Room added successfully",
        "data": campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"][room_id]
    }

@app.get("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}/room/{room_id}")
async def get_room_by_id(campus_id: str, hostel_id: str, block_id: str, room_id: str):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"] or block_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"] or room_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"]:
        raise HTTPException(status_code=404, detail="Room not found")
    return campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"][room_id]

@app.put("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}/room/{room_id}")
async def update_room(campus_id: str, hostel_id: str, block_id: str, room_id: str, room: Room):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"] or block_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"] or room_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"]:
        raise HTTPException(status_code=404, detail="Room not found")
    campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"][room_id]["room_name"] = room.room_name
    campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"][room_id]["capacity"] = room.capacity
    return {"message": "Room updated successfully", "data": campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"][room_id]}

@app.delete("/campus/{campus_id}/hostel/{hostel_id}/block/{block_id}/room/{room_id}")
async def delete_room(campus_id: str, hostel_id: str, block_id: str, room_id: str):
    if campus_id not in campus_db or hostel_id not in campus_db[campus_id]["hostels"] or block_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"] or room_id not in campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"]:
        raise HTTPException(status_code=404, detail="Room not found")
    deleted = campus_db[campus_id]["hostels"][hostel_id]["blocks"][block_id]["rooms"].pop(room_id)
    return {"message": "Room deleted successfully", "data": deleted}