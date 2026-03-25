from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from boto3.dynamodb.conditions import Key
from typing import List
from uuid import uuid4
from boto3.dynamodb.conditions import Attr
table = boto3.resource("dynamodb").Table("Campus")

app = FastAPI()


dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table("Campus")  # Make sure table name is correct



class Campus(BaseModel):
    campus_name: str
    location: str
    total_hostels: int
class Hostel(BaseModel):
    campus_id:str
    hostel_name: str
    total_rooms:int
class Block(BaseModel):
    block_name: str
class Room(BaseModel):
    Room_no:int
    capacity: int
class Student(BaseModel):
    student_name: str
    subjects: List[str]
class Maintenance(BaseModel):
    issue: str
    status: str = ("OPEN")
@app.post("/campus/add",tags=["Campus"]))
async def add_campus(campus: Campus):
    try:
        campus_name = campus.campus_name.strip()
        campus_id = f"CAMPUS#{uuid4()}"
        response = table.scan(
            FilterExpression=Attr("campus_name").eq(campus_name))
        if response.get("Items"):
            raise HTTPException(status_code=400,detail="Campus already exists")
        items={
            "PK":"campus",
            "SK":campus_id,
            "campus_id":campus_id,
            "campus_name":campus_name,
            "location":campus.location,
            "total_hostels":campus.total_hostels
        }
        table.put_item(Item=items)
        return{
            "message":"campus added successfully",
            "campus_id":campus_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/campus", tags=["Campus"])
async def get_all_campus():
    try:
        response = table.query(
            KeyConditionExpression=Key("PK").eq("campus")
        )

        campuses = response.get("Items", [])

        return {
            "total": len(campuses),
            "campuses": campuses
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/hostel/add", tags=["Hostel"])
async def add_hostel(hostel: Hostel):
    try:

        response = table.scan(
            FilterExpression="PK = :pk",
            ExpressionAttributeValues={":pk": "hostel"},
            Select="COUNT"
        )

        room_count = response.get("Count", 0)

        if room_count >= 500:
            raise HTTPException(
                status_code=400,
                detail="room limit reached (Maximum 500 allowed)"
            )
        hostel_id = f"HOSTEL#{uuid4()}"
        response = table.scan(
            FilterExpression="#hn = :name",
            ExpressionAttributeNames={"#hn": "hostel_name"},
            ExpressionAttributeValues={":name": hostel.hostel_name}
        )

        if response.get("Items"):
            raise HTTPException(status_code=400, detail="Hostel already exists")
        item = {
            "PK": "hostel",
            "SK": hostel_id,
            "hostel_id": hostel_id,
            "hostel_name": hostel.hostel_name,
            "total_rooms": hostel.total_rooms
        }

        table.put_item(Item=item)

        return {
            "message": "Hostel created successfully",
            "hostel_id": hostel_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/hostel", tags=["Hostel"])
async def get_all_hostels():
    try:
        response = table.query(
            KeyConditionExpression=Key("PK").eq("hostel")
        )

        hostels = response.get("Items", [])

        return {
            "total": len(hostels),
            "hostels": hostels
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.put("/hostel/update/{hostel_id}", tags=["Hostel"])
async def update_hostel(hostel_id: str, hostel: Hostel):
    try:
        hostel_id = hostel_id.strip()
        response = table.get_item(
            Key={"PK": "hostel", "SK": hostel_id}
        )

        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Hostel not found")
        table.update_item(
            Key={"PK": "hostel", "SK": hostel_id},
            UpdateExpression="""
                SET #hn = :name,
                    total_rooms = :tr
            """,
            ExpressionAttributeNames={
                "#hn": "hostel_name"
            },
            ExpressionAttributeValues={
                ":name": hostel.hostel_name,
                ":tr": hostel.total_rooms
            },
            ReturnValues="ALL_NEW"
        )

        return {
            "message": "Hostel updated successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.delete("/hostel/delete/{hostel_id}", tags=["Hostel"])
async def delete_hostel(hostel_id: str):
    try:
        hostel_id = hostel_id.strip()
        response = table.get_item(
            Key={"PK": "hostel", "SK": hostel_id}
        )

        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Hostel not found")
        table.delete_item(
            Key={"PK": "hostel", "SK": hostel_id}
        )

        return {
            "message": "Hostel deleted successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/hostel/{hostel_id}/block/add", tags=["Block"])
async def add_block(hostel_id: str, block: Block):
    try:
        hostel_id = hostel_id.strip()
        hostel_res = table.scan(
            FilterExpression="SK = :sk",
            ExpressionAttributeValues={":sk": hostel_id}
        )
        if not hostel_res.get("Items"):
            raise HTTPException(status_code=404, detail="Hostel not found")
        block_id = f"BLOCK#{uuid4()}"
        response = table.query(
            KeyConditionExpression=Key("PK").eq(hostel_id) & Key("SK").begins_with("BLOCK#")
        )

        for item in response.get("Items", []):
            if item.get("block_name", "").lower() == block.block_name.lower():
                raise HTTPException(status_code=400, detail="Block already exists")
        item = {
            "PK":hostel_id,
            "SK": block_id,
            "block_id": block_id,
            "block_name": block.block_name
        }

        table.put_item(Item=item)

        return {
            "message": "Block added successfully",
            "block_id": block_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/hostel/{hostel_id}/blocks", tags=["Block"])
async def get_blocks(hostel_id: str):
    try:
        response = table.query(
            KeyConditionExpression=Key("PK").eq(hostel_id) & Key("SK").begins_with("BLOCK#")
        )

        return {
            "blocks": response.get("Items", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.delete("/hostel/{hostel_id}/block/{block_id}", tags=["Block"])
async def delete_block(hostel_id: str, block_id: str):
    try:

        response = table.get_item(
            Key={"PK": hostel_id, "SK": block_id}
        )
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Block not found")
        table.delete_item(
            Key={"PK":hostel_id, "SK": block_id}
        )

        return {
            "message": "Block deleted successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/block/{block_id}/room/add", tags=["Room"])
async def add_room(block_id: str, room: Room):
    try:
        block_id = block_id.strip()
        block_res = table.scan(
            FilterExpression="SK = :sk",
            ExpressionAttributeValues={":sk": block_id}
        )

        if not block_res.get("Items"):
            raise HTTPException(status_code=404, detail="Block not found")
        room_id = f"ROOM#{uuid4()}"
        item = {
            "PK": block_id,
            "SK": room_id,
            "room_id": room_id,
            "room_number": room.Room_no
        }

        table.put_item(Item=item)

        return {
            "message": "Room added successfully",
            "room_id": room_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/block/{block_id}/rooms", tags=["Room"])
async def get_rooms(block_id: str):
    try:
        response = table.query(
            KeyConditionExpression=Key("PK").eq(block_id) & Key("SK").begins_with("ROOM#")
        )

        return {
            "rooms": response.get("Items", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.delete("/block/{block_id}/room/{room_id}", tags=["Room"])
async def delete_room(block_id: str, room_id: str):
    try:
        block_id = block_id.strip()
        room_id = room_id.strip()
        if not room_id.startswith("ROOM#"):
            raise HTTPException(status_code=400, detail="Invalid room_id format")
        response = table.get_item(
            Key={"PK": block_id, "SK": room_id}
        )

        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Room not found")
        table.delete_item(
            Key={"PK": block_id, "SK": room_id}
        )

        return {
            "message": "Room deleted successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/room/{room_id}/maintenance/add", tags=["Maintenance"])
async def add_maintenance(room_id: str, maintenance: Maintenance):
    try:
        room_id = room_id.strip()
        room_res = table.scan(
            FilterExpression="SK = :sk",
            ExpressionAttributeValues={":sk": room_id}
        )
        if not room_res.get("Items"):
            raise HTTPException(status_code=404, detail="Room not found")
        room_item = room_res["Items"][0]
        room_number = room_item.get("room_number")
        maintenance_id = f"MAINT#{uuid4()}"
        item = {
            "PK": room_id,
            "SK": maintenance_id,
            "maintenance_id": maintenance_id,
            "issue": maintenance.issue,
            "status": maintenance.status,
            "room_number": room_number   # 🔥 fetched from DB
        }

        table.put_item(Item=item)

        return {
            "message": "Room assigned to maintenance",
            "maintenance_id": maintenance_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.delete("/room/{room_id}/maintenance/{maintenance_id}", tags=["Maintenance"])
async def delete_maintenance(room_id: str, maintenance_id: str):
    try:
        table.delete_item(
            Key={
                "PK": room_id,
                "SK": maintenance_id
            }
        )

        return {
            "message": "Maintenance record deleted"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/room/{room_id}/student/add", tags=["Student"])
async def add_student(room_id: str, student: Student):
    try:
        room_id = room_id.strip()

        room_res = table.scan(
            FilterExpression="SK = :sk",
            ExpressionAttributeValues={":sk": room_id}
        )

        if not room_res.get("Items"):
            raise HTTPException(status_code=404, detail="Room not found")

        room_item = room_res["Items"][0]
        room_capacity = room_item.get("capacity", 0)
        maintenance_res = table.query(
            KeyConditionExpression=Key("PK").eq(room_id) & Key("SK").begins_with("MAINT#")
        )

        for item in maintenance_res.get("Items", []):
            if item.get("status") in ["OPEN", "IN_PROGRESS"]:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot add student. Room is under maintenance"
                )
        student_res = table.query(
            KeyConditionExpression=Key("PK").eq(room_id) & Key("SK").begins_with("STUDENT#")
        )
        current_students = len(student_res.get("Items", []))
        if current_students >= room_capacity:
            raise HTTPException(
                status_code=400,
                detail=f"Room is full. Capacity: {room_capacity}, Current: {current_students}"
            )
        student_id = f"STUDENT#{uuid4()}"
        item = {
            "PK": room_id,
            "SK": student_id,
            "student_id": student_id,
            "student_name": student.student_name,
            "age": student.age
        }

        table.put_item(Item=item)

        return {
            "message": "Student added successfully",
            "student_id": student_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.delete("/room/{room_id}/student/{student_id}", tags=["Student"])
async def delete_student(room_id: str, student_id: str):
    try:
        room_id = room_id.strip()
        student_id = student_id.strip()
        if not student_id.startswith("STUDENT#"):
            raise HTTPException(status_code=400, detail="Invalid student_id format")
        response = table.get_item(
            Key={
                "PK": room_id,
                "SK": student_id
            }
        )

        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Student not found")
        table.delete_item(
            Key={
                "PK": room_id,
                "SK": student_id
            }
        )

        return {
            "message": "Student removed successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/campus/{campus_id}/students/count", tags=["Student"])
async def get_total_students(campus_id: str):
    try:
        campus_id = campus_id.strip()

        total_students = 0
        block_res = table.scan(
            FilterExpression="campus_id = :cid AND begins_with(SK, :b)",
            ExpressionAttributeValues={
                ":cid": campus_id,
                ":b": "BLOCK#"
            }
        )

        blocks = block_res.get("Items", [])

        if not blocks:
            return {
                "campus_id": campus_id,
                "total_students": 0
            }
        for block in blocks:
            block_id = block["SK"]

            room_res = table.query(
                KeyConditionExpression=Key("PK").eq(block_id) & Key("SK").begins_with("ROOM#")
            )

            rooms = room_res.get("Items", [])
            for room in rooms:
                room_id = room["SK"]

                student_res = table.query(
                    KeyConditionExpression=Key("PK").eq(room_id) & Key("SK").begins_with("STUDENT#")
                )

                total_students += len(student_res.get("Items", []))

        return {
            "campus_id": campus_id,
            "total_students": total_students
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from uuid import uuid4
from fastapi import HTTPException
from boto3.dynamodb.conditions import Key

@app.post("/campus/{campus_id}/student/add", tags=["Student"])
async def add_student_with_waitlist(campus_id: str, room_id: str, student: Student):
    try:
        campus_id = campus_id.strip()
        room_id = room_id.strip()
        campus_res = table.scan(
            FilterExpression="SK = :sk",
            ExpressionAttributeValues={":sk": campus_id}
        )

        if not campus_res.get("Items"):
            raise HTTPException(status_code=404, detail="Campus not found")

        campus_item = campus_res["Items"][0]
        campus_limit = campus_item.get("total_students_limit", 100)

        total_students = 0

        block_res = table.scan(
            FilterExpression="campus_id = :cid AND begins_with(SK, :b)",
            ExpressionAttributeValues={
                ":cid": campus_id,
                ":b": "BLOCK#"
            }
        )

        for block in block_res.get("Items", []):
            block_id = block["SK"]

            room_res = table.query(
                KeyConditionExpression=Key("PK").eq(block_id) & Key("SK").begins_with("ROOM#")
            )

            for room in room_res.get("Items", []):
                room_id_loop = room["SK"]

                student_res = table.query(
                    KeyConditionExpression=Key("PK").eq(room_id_loop) & Key("SK").begins_with("STUDENT#")
                )

                total_students += len(student_res.get("Items", []))
        student_id = f"STUDENT#{uuid4()}"
        if total_students >= campus_limit:
            waitlist_id = f"WAITLIST#{uuid4()}"

            item = {
                "PK": campus_id,
                "SK": waitlist_id,
                "student_id": student_id,
                "student_name": student.student_name,
                "age": student.age,
                "status": "WAITLIST"
            }

            table.put_item(Item=item)

            return {
                "message": "Campus full. Student added to waitlist",
                "status": "WAITLIST",
                "student_id": student_id
            }

@app.post("/room/{room_id}/student/{student_id}/assign", tags=["Student"])
async def assign_student_to_room(room_id: str, student_id: str):
    try:
        room_id = room_id.strip()
        student_id = student_id.strip()
        room_res = table.scan(
            FilterExpression="SK = :sk",
            ExpressionAttributeValues={":sk": room_id}
        )

        if not room_res.get("Items"):
            raise HTTPException(status_code=404, detail="Room not found")

        room_item = room_res["Items"][0]
        room_capacity = room_item.get("capacity", 0)
        maintenance_res = table.query(
            KeyConditionExpression=Key("PK").eq(room_id) & Key("SK").begins_with("MAINT#")
        )

        for m in maintenance_res.get("Items", []):
            if m.get("status") in ["OPEN", "IN_PROGRESS"]:
                raise HTTPException(
                    status_code=400,
                    detail="Room is under maintenance"
                )
        student_res = table.query(
            KeyConditionExpression=Key("PK").eq(room_id) & Key("SK").begins_with("STUDENT#")
        )

        current_students = len(student_res.get("Items", []))

        if current_students >= room_capacity:
            raise HTTPException(
                status_code=400,
                detail="Room is full"
            )
        scan_res = table.scan(
            FilterExpression="student_id = :sid",
            ExpressionAttributeValues={":sid": student_id}
        )

        if not scan_res.get("Items"):
            raise HTTPException(status_code=404, detail="Student not found")

        student_item = scan_res["Items"][0]
        table.delete_item(
            Key={
                "PK": student_item["PK"],
                "SK": student_item["SK"]
            }
        )
        new_item = {
            "PK": room_id,
            "SK": student_id,
            "student_id": student_id,
            "student_name": student_item.get("student_name"),
            "age": student_item.get("age"),
            "status": "ASSIGNED"
        }

        table.put_item(Item=new_item)

        return {
            "message": "Student assigned to room successfully",
            "room_id": room_id,
            "student_id": student_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/campus/{campus_id}/waitlist", tags=["Student"])
async def get_waitlist_students(campus_id: str):
             try:
                campus_id = campus_id.strip()
                response = table.query(
                    KeyConditionExpression=Key("PK").eq(campus_id) & Key("SK").begins_with("WAITLIST#")
                )

                waitlist = response.get("Items", [])

                if not waitlist:
                    return {
                        "message": "No students in waitlist",
                        "total_waitlist": 0,
                        "students": []
                    }

                return {
                    "campus_id": campus_id,
                    "total_waitlist": len(waitlist),
                    "students": waitlist
                }

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))