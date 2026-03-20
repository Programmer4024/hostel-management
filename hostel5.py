from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from boto3.dynamodb.conditions import Key
from typing import List
from uuid import uuid4
import boto3
table = boto3.resource("dynamodb").Table("Campus")

app = FastAPI()


dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table("Campus")  # Make sure table name is correct



class Campus(BaseModel):
    campus_name: str
    location: str
    total_hostels: int
class Hostel(BaseModel):
    hostel_name: str

class Block(BaseModel):
    block_name: str
class Room(BaseModel):
    capacity: int
class Student(BaseModel):
    name: str
    subjects: List[str]

@app.post("/campus/add", tags=["Campus"])
async def add_campus(campus: Campus):
    try:
        campus_name = campus.campus_name.strip().lower()


        response = table.get_item(
            Key={"PK": "CAMPUS", "SK": campus_name}
        )

        if "Item" in response:
            raise HTTPException(status_code=400, detail="Campus already exists")

        item = {
            "PK": "CAMPUS",
            "SK": campus_name,
            "campus_name": campus.campus_name,
            "location": campus.location,
            "total_hostels": campus.total_hostels
        }

        table.put_item(Item=item)

        return {"message": "Campus added", "data": item}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/campus", tags=["Campus"])
async def get_all_campus():
    try:
        response = table.query(
            KeyConditionExpression=Key("PK").eq("CAMPUS")
        )

        return {
            "total": len(response.get("Items", [])),
            "data": response.get("Items", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/campus/{campus_name}", tags=["Campus"])
async def get_campus(campus_name: str):
    try:
        campus_name = campus_name.strip().lower()

        response = table.get_item(
            Key={"PK": "CAMPUS", "SK": campus_name}
        )

        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Campus not found")

        return response["Item"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.put("/campus/update/{campus_name}", tags=["Campus"])
async def update_campus(campus_name: str, campus: Campus):
    try:
        campus_name = campus_name.strip().lower()

        response = table.get_item(
            Key={"PK": "CAMPUS", "SK": campus_name}
        )

        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Campus not found")

        table.update_item(
            Key={"PK": "CAMPUS", "SK": campus_name},
            UpdateExpression="SET location = :loc, total_hostels = :th",
            ExpressionAttributeValues={
                ":loc": campus.location,
                ":th": campus.total_hostels
            }
        )

        return {"message": "Campus updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/campus/delete/{campus_name}", tags=["Campus"])
async def delete_campus(campus_name: str):
    try:
        campus_name = campus_name.strip().lower()

        response = table.get_item(
            Key={"PK": "CAMPUS", "SK": campus_name}
        )

        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Campus not found")

        table.delete_item(
            Key={"PK": "CAMPUS", "SK": campus_name}
        )

        return {"message": "Campus deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from boto3.dynamodb.conditions import Key, Attr

@app.post("/campus/{campus_name}/hostel/add", tags=["Hostel"])
async def add_hostel(campus_name: str, hostel: Hostel):

    campus_name = campus_name.strip().lower()
    hostel_name = hostel.hostel_name.strip().lower()

    # ✅ Check campus exists
    campus_res = table.get_item(
        Key={"PK": "CAMPUS", "SK": campus_name}
    )

    if "Item" not in campus_res:
        raise HTTPException(status_code=404, detail="Campus not found")

    campus_data = campus_res["Item"]

    # ✅ Check hostel already exists
    existing = table.get_item(
        Key={"PK": "HOSTEL", "SK": hostel_name}
    )

    if "Item" in existing:
        raise HTTPException(status_code=400, detail="Hostel already exists")


    response = table.query(
        KeyConditionExpression=Key("PK").eq("HOSTEL"),
        FilterExpression=Attr("campus_name").eq(campus_name)
    )

    current_count = len(response.get("Items", []))


    if current_count >= campus_data["total_hostels"]:
        raise HTTPException(status_code=400, detail="Hostel limit reached")

    item = {
        "PK": "HOSTEL",
        "SK": hostel_name,
        "campus_name": campus_name,
        "hostel_name": hostel.hostel_name,
        "total_students": 0,
        "waitlist": []
    }

    table.put_item(Item=item)

    return {
        "message": "Hostel added",
        "data": item,
        "current_hostels_count": current_count + 1
    }
from boto3.dynamodb.conditions import Key, Attr

@app.get("/campus/{campus_name}/hostels", tags=["Hostel"])
async def get_hostels(campus_name: str):

    campus_name = campus_name.strip().lower()


    campus_res = table.get_item(
        Key={"PK": "CAMPUS", "SK": campus_name}
    )

    if "Item" not in campus_res:
        raise HTTPException(status_code=404, detail="Campus not found")

    response = table.query(
        KeyConditionExpression=Key("PK").eq("HOSTEL"),
        FilterExpression=Attr("campus_name").eq(campus_name)
    )

    return {
        "total": len(response.get("Items", [])),
        "data": response.get("Items", [])
    }
@app.put("/campus/{campus_name}/hostel/{hostel_name}", tags=["Hostel"])
async def update_hostel(campus_name: str, hostel_name: str, hostel: Hostel):

    campus_name = campus_name.strip().lower()
    old_hostel = hostel_name.strip().lower()
    new_hostel = hostel.hostel_name.strip().lower()


    response = table.get_item(
        Key={"PK": "HOSTEL", "SK": old_hostel}
    )

    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Hostel not found")

    old_data = response["Item"]


    table.delete_item(
        Key={"PK": "HOSTEL", "SK": old_hostel}
    )


    new_item = {
        "PK": "HOSTEL",
        "SK": new_hostel,
        "campus_name": campus_name,
        "hostel_name": hostel.hostel_name,
        "total_students": old_data.get("total_students", 0),
        "waitlist": old_data.get("waitlist", [])
    }

    table.put_item(Item=new_item)

    return {"message": "Hostel updated", "data": new_item}
@app.delete("/campus/{campus_name}/hostel/{hostel_name}", tags=["Hostel"])
async def delete_hostel(campus_name: str, hostel_name: str):

    hostel_name = hostel_name.strip().lower()

    response = table.get_item(
        Key={"PK": "HOSTEL", "SK": hostel_name}
    )

    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Hostel not found")

    table.delete_item(
        Key={"PK": "HOSTEL", "SK": hostel_name}
    )

    return {"message": "Hostel deleted"}

@app.post("/campus/{campus_name}/hostel/{hostel_name}/block/add", tags=["Blocks"])
async def add_block(campus_name: str, hostel_name: str, block: Block):

    campus_key = campus_name.strip().lower()
    hostel_key = hostel_name.strip().lower()
    block_key = block.block_name.strip().lower()


    hostel_res = table.get_item(
        Key={"PK": "HOSTEL", "SK": hostel_key}
    )

    if "Item" not in hostel_res:
        raise HTTPException(status_code=404, detail="Hostel not found")


    existing = table.get_item(
        Key={"PK": "BLOCK", "SK": block_key}
    )

    if "Item" in existing:
        raise HTTPException(status_code=400, detail="Block already exists")

    item = {
        "PK": "BLOCK",
        "SK": block_key,
        "campus_name": campus_name,   # original
        "hostel_name": hostel_name,   # original
        "block_name": block.block_name
    }

    table.put_item(Item=item)

    return {"message": "Block added", "data": item}
@app.get("/campus/{campus_name}/hostel/{hostel_name}/blocks", tags=["Blocks"])
async def get_blocks(campus_name: str, hostel_name: str):

    campus_key = campus_name.strip().lower()
    hostel_key = hostel_name.strip().lower()

    response = table.query(
        KeyConditionExpression=Key("PK").eq("BLOCK"),
        FilterExpression=Attr("campus_name").eq(campus_key) &
                         Attr("hostel_name").eq(hostel_key)
    )

    return {
        "total": len(response.get("Items", [])),
        "data": response.get("Items", [])
    }
@app.put("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}", tags=["Blocks"])
async def update_block(campus_name: str, hostel_name: str, block_name: str, block: Block):

    old_block = block_name.strip().lower()
    new_block = block.block_name.strip().lower()

    response = table.get_item(
        Key={"PK": "BLOCK", "SK": old_block}
    )

    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Block not found")

    old_data = response["Item"]


    table.delete_item(
        Key={"PK": "BLOCK", "SK": old_block}
    )


    new_item = {
        "PK": "BLOCK",
        "SK": new_block,
        "campus_name": old_data["campus_name"],
        "hostel_name": old_data["hostel_name"],
        "block_name": block.block_name
    }

    table.put_item(Item=new_item)

    return {"message": "Block updated", "data": new_item}
@app.delete("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}", tags=["Blocks"])
async def delete_block(campus_name: str, hostel_name: str, block_name: str):

    block_key = block_name.strip().lower()

    response = table.get_item(
        Key={"PK": "BLOCK", "SK": block_key}
    )

    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Block not found")

    table.delete_item(
        Key={"PK": "BLOCK", "SK": block_key}
    )

    return {"message": "Block deleted successfully"}


@app.post("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}/room/add", tags=["Room"])
async def add_room(campus_name: str, hostel_name: str, block_name: str, room: Room):

    campus_key = campus_name.strip().lower()
    hostel_key = hostel_name.strip().lower()
    block_key = block_name.strip().lower()

    pk = f"BLOCK#{campus_key}#{hostel_key}#{block_key}"


    response = table.query(
        KeyConditionExpression=Key("PK").eq(pk)
    )

    room_count = len(response.get("Items", []))
    room_no = f"room{room_count + 1}"

    sk = f"ROOM#{room_no}"


    existing = table.get_item(
        Key={"PK": pk, "SK": sk}
    )

    if "Item" in existing:
        raise HTTPException(status_code=400, detail="Room already exists")

    item = {
        "PK": pk,
        "SK": sk,
        "campus_name": campus_name,
        "hostel_name": hostel_name,
        "block_name": block_name,
        "room_no": room_no,
        "capacity": room.capacity,
        "students": []
    }

    table.put_item(Item=item)

    return {
        "message": "Room added",
        "data": item
    }
from boto3.dynamodb.conditions import Key

@app.get("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}/rooms", tags=["Room"])
async def get_all_rooms(campus_name: str, hostel_name: str, block_name: str):

    campus_key = campus_name.strip().lower()
    hostel_key = hostel_name.strip().lower()
    block_key = block_name.strip().lower()

    pk = f"BLOCK#{campus_key}#{hostel_key}#{block_key}"

    response = table.query(
        KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with("ROOM#")
    )

    rooms = response.get("Items", [])

    if not rooms:
        raise HTTPException(status_code=404, detail="No rooms found")

    return {
        "total_rooms": len(rooms),
        "rooms": rooms
    }
@app.put("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}/room/{room_no}", tags=["Room"])
async def update_room(campus_name: str, hostel_name: str, block_name: str, room_no: str, room: Room):

    try:
        room_key = room_no.strip().lower()


        response = table.get_item(
            Key={"PK": "ROOM", "SK": room_key}
        )

        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Room not found")

        table.update_item(
            Key={"PK": "ROOM", "SK": room_key},
            UpdateExpression="SET #cap = :c",
            ExpressionAttributeNames={
                "#cap": "capacity"
            },
            ExpressionAttributeValues={
                ":c": int(room.capacity)
            }
        )

        return {
            "message": "Room updated successfully",
            "room_no": room_key,
            "new_capacity": room.capacity
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.delete("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}/room/{room_no}", tags=["Room"])
async def delete_room(campus_name: str, hostel_name: str, block_name: str, room_no: str):

    campus_key = campus_name.strip().lower()
    hostel_key = hostel_name.strip().lower()
    block_key = block_name.strip().lower()
    room_key = room_no.strip().lower()

    pk = f"BLOCK#{campus_key}#{hostel_key}#{block_key}"
    sk = f"ROOM#{room_key}"

    response = table.get_item(
        Key={"PK": pk, "SK": sk}
    )

    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Room not found")


    table.delete_item(
        Key={"PK": pk, "SK": sk}
    )

    return {"message": "Room deleted successfully"}
from uuid import uuid4

@app.post("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}/room/{room_no}/student/add", tags=["Student"])
async def add_student(campus_name: str, hostel_name: str, block_name: str, room_no: str, student: Student):
    try:
        campus_key = campus_name.strip().lower()
        hostel_key = hostel_name.strip().lower()
        block_key = block_name.strip().lower()
        room_key = room_no.strip().lower()

        pk = f"BLOCK#{campus_key}#{hostel_key}#{block_key}"
        sk = f"ROOM#{room_key}"

        # ✅ Get Room
        room_res = table.get_item(Key={"PK": pk, "SK": sk})
        if "Item" not in room_res:
            raise HTTPException(status_code=404, detail="Room not found")

        room = room_res["Item"]

        # ✅ Get Hostel (for waitlist)
        hostel_res = table.get_item(
            Key={"PK": "HOSTEL", "SK": hostel_key}
        )
        if "Item" not in hostel_res:
            raise HTTPException(status_code=404, detail="Hostel not found")

        # Student Data
        student_data = {
            "student_id": str(uuid4()),
            "name": student.name,
            "subjects": student.subjects
        }

        students = room.get("students", [])
        capacity = room.get("capacity", 0)

        # 🚧 1. If room under maintenance → send to waitlist
        if room.get("maintenance", False):
            table.update_item(
                Key={"PK": "HOSTEL", "SK": hostel_key},
                UpdateExpression="SET #wl = list_append(if_not_exists(#wl, :empty), :s)",
                ExpressionAttributeNames={"#wl": "waitlist"},
                ExpressionAttributeValues={
                    ":s": [student_data],
                    ":empty": []
                }
            )

            return {
                "message": "Room under maintenance → student added to waitlist",
                "student": student_data
            }

        # ❌ 2. If room full → waitlist
        if len(students) >= capacity:
            table.update_item(
                Key={"PK": "HOSTEL", "SK": hostel_key},
                UpdateExpression="SET #wl = list_append(if_not_exists(#wl, :empty), :s)",
                ExpressionAttributeNames={"#wl": "waitlist"},
                ExpressionAttributeValues={
                    ":s": [student_data],
                    ":empty": []
                }
            )

            return {
                "message": "Room full → student added to waitlist",
                "student": student_data
            }

        # ✅ 3. Add student to room
        table.update_item(
            Key={"PK": pk, "SK": sk},
            UpdateExpression="SET #st = list_append(if_not_exists(#st, :empty), :s)",
            ExpressionAttributeNames={"#st": "students"},
            ExpressionAttributeValues={
                ":s": [student_data],
                ":empty": []
            }
        )

        return {
            "message": "Student added to room",
            "student": student_data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/campus/{campus_name}/hostel/{hostel_name}/waitlist", tags=["Waitlist"])
async def get_waitlist(campus_name: str, hostel_name: str):

    campus_key = campus_name.strip().lower()
    hostel_key = hostel_name.strip().lower()


    response = table.get_item(
        Key={"PK": "HOSTEL", "SK": hostel_key}
    )

    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Hostel not found")

    hostel = response["Item"]

    waitlist = hostel.get("waitlist", [])

    return {
        "total_waitlist_students": len(waitlist),
        "waitlist_students": waitlist
    }

# ✅ Helper function (VERY IMPORTANT → use everywhere)
def get_room_keys(campus_name, hostel_name, block_name, room_no):
    campus_key = campus_name.strip().lower()
    hostel_key = hostel_name.strip().lower()
    block_key = block_name.strip().lower()
    room_key = room_no.strip().lower()

    pk = f"BLOCK#{campus_key}#{hostel_key}#{block_key}"
    sk = f"ROOM#{room_key}"

    return pk, sk


@app.put("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}/room/{room_no}/maintenance/add", tags=["Maintenance"])
async def add_maintenance(campus_name: str, hostel_name: str, block_name: str, room_no: str):

    try:
        # ✅ Get consistent keys
        pk, sk = get_room_keys(campus_name, hostel_name, block_name, room_no)

        # 🔍 Debug (remove later if not needed)
        print("PK:", pk)
        print("SK:", sk)

        # ✅ Fetch room
        response = table.get_item(Key={"PK": pk, "SK": sk})

        if "Item" not in response:
            raise HTTPException(
                status_code=404,
                detail=f"Room not found with PK={pk} and SK={sk}"
            )

        room = response["Item"]

        # 🚧 Already under maintenance
        if room.get("maintenance", False):
            raise HTTPException(
                status_code=400,
                detail=f"Room {room_no} is already under maintenance"
            )

        # ❗ Optional: prevent maintenance if students present
        if room.get("students"):
            raise HTTPException(
                status_code=400,
                detail="Cannot enable maintenance: students are still in the room"
            )

        # ✅ Update maintenance
        table.update_item(
            Key={"PK": pk, "SK": sk},
            UpdateExpression="SET #m = :true",
            ExpressionAttributeNames={
                "#m": "maintenance"
            },
            ExpressionAttributeValues={
                ":true": True
            }
        )

        return {
            "message": f"Room {room_no} is now under maintenance",
            "PK": pk,
            "SK": sk
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.put("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}/room/{room_no}/maintenance/remove", tags=["Maintenance"])
async def remove_maintenance(campus_name: str, hostel_name: str, block_name: str, room_no: str):

    campus_key = campus_name.strip().lower()
    hostel_key = hostel_name.strip().lower()
    block_key = block_name.strip().lower()
    room_key = room_no.strip().lower()

    pk = f"BLOCK#{campus_key}#{hostel_key}#{block_key}"
    sk = f"ROOM#{room_key}"

    response = table.get_item(Key={"PK": pk, "SK": sk})

    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Room not found")

    room = response["Item"]

    # ✅ Not under maintenance check
    if not room.get("maintenance", False):
        raise HTTPException(status_code=400, detail="Room is not under maintenance")

    table.update_item(
        Key={"PK": pk, "SK": sk},
        UpdateExpression="SET #m = :false",
        ExpressionAttributeNames={"#m": "maintenance"},
        ExpressionAttributeValues={":false": False}
    )

    return {"message": "Room is now available"}
@app.post("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}/room/{room_no}/student/add", tags=["Student"])
async def add_student(campus_name: str, hostel_name: str, block_name: str, room_no: str, student: Student):

    try:
        campus_key = campus_name.strip().lower()
        hostel_key = hostel_name.strip().lower()
        block_key = block_name.strip().lower()
        room_key = room_no.strip().lower()

        pk = f"BLOCK#{campus_key}#{hostel_key}#{block_key}"
        sk = f"ROOM#{room_key}"

        # ✅ Get Room
        room_res = table.get_item(Key={"PK": pk, "SK": sk})
        if "Item" not in room_res:
            raise HTTPException(status_code=404, detail="Room not found")

        room = room_res["Item"]

        # ✅ Get Hostel
        hostel_res = table.get_item(Key={"PK": "HOSTEL", "SK": hostel_key})
        if "Item" not in hostel_res:
            raise HTTPException(status_code=404, detail="Hostel not found")

        student_data = {
            "student_id": str(uuid4()),
            "name": student.name,
            "subjects": student.subjects
        }

        students = room.get("students", [])
        capacity = room.get("capacity", 0)

        # 🚧 If maintenance → go to waitlist
        if room.get("maintenance", False):
            table.update_item(
                Key={"PK": "HOSTEL", "SK": hostel_key},
                UpdateExpression="SET #wl = list_append(if_not_exists(#wl, :empty), :s)",
                ExpressionAttributeNames={"#wl": "waitlist"},
                ExpressionAttributeValues={
                    ":s": [student_data],
                    ":empty": []
                }
            )

            return {
                "message": "Room under maintenance → added to waitlist",
                "student": student_data
            }

        # ❌ If room full → waitlist
        if len(students) >= capacity:
            table.update_item(
                Key={"PK": "HOSTEL", "SK": hostel_key},
                UpdateExpression="SET #wl = list_append(if_not_exists(#wl, :empty), :s)",
                ExpressionAttributeNames={"#wl": "waitlist"},
                ExpressionAttributeValues={
                    ":s": [student_data],
                    ":empty": []
                }
            )

            return {
                "message": "Room full → added to waitlist",
                "student": student_data
            }

        # ✅ Add to room
        table.update_item(
            Key={"PK": pk, "SK": sk},
            UpdateExpression="SET #st = list_append(if_not_exists(#st, :empty), :s)",
            ExpressionAttributeNames={"#st": "students"},
            ExpressionAttributeValues={
                ":s": [student_data],
                ":empty": []
            }
        )

        return {
            "message": "Student added to room",
            "student": student_data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/campus/{campus_name}/hostel/{hostel_name}/block/{block_name}/room/{room_no}/waitlist/assign", tags=["Student"])
async def assign_waitlist_to_room(campus_name: str, hostel_name: str, block_name: str, room_no: str):

    try:
        campus_key = campus_name.strip().lower()
        hostel_key = hostel_name.strip().lower()
        block_key = block_name.strip().lower()
        room_key = room_no.strip().lower()

        # ✅ Room PK/SK
        room_pk = f"BLOCK#{campus_key}#{hostel_key}#{block_key}"
        room_sk = f"ROOM#{room_key}"

        # ✅ Get Room
        room_res = table.get_item(Key={"PK": room_pk, "SK": room_sk})
        if "Item" not in room_res:
            raise HTTPException(status_code=404, detail="Room not found")

        room = room_res["Item"]

        # 🚧 Maintenance check
        if room.get("maintenance", False):
            raise HTTPException(status_code=400, detail="Room is under maintenance")

        students = room.get("students", [])
        capacity = room.get("capacity", 0)

        # ❌ No space
        available_slots = capacity - len(students)
        if available_slots <= 0:
            raise HTTPException(status_code=400, detail="Room is already full")

        # ✅ Get Hostel waitlist
        hostel_res = table.get_item(
            Key={"PK": "HOSTEL", "SK": hostel_key}
        )

        if "Item" not in hostel_res:
            raise HTTPException(status_code=404, detail="Hostel not found")

        hostel = hostel_res["Item"]
        waitlist = hostel.get("waitlist", [])

        if not waitlist:
            raise HTTPException(status_code=400, detail="Waitlist is empty")

        # ✅ Pick students (FIFO)
        students_to_add = waitlist[:available_slots]
        remaining_waitlist = waitlist[available_slots:]

        # ✅ Add students to room
        table.update_item(
            Key={"PK": room_pk, "SK": room_sk},
            UpdateExpression="SET #st = list_append(if_not_exists(#st, :empty), :s)",
            ExpressionAttributeNames={"#st": "students"},
            ExpressionAttributeValues={
                ":s": students_to_add,
                ":empty": []
            }
        )

        # ✅ Update waitlist
        table.update_item(
            Key={"PK": "HOSTEL", "SK": hostel_key},
            UpdateExpression="SET #wl = :w",
            ExpressionAttributeNames={"#wl": "waitlist"},
            ExpressionAttributeValues={
                ":w": remaining_waitlist
            }
        )

        return {
            "message": "Students assigned from waitlist to room",
            "added_students": students_to_add,
            "remaining_waitlist_count": len(remaining_waitlist)
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))