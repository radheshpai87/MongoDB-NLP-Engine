from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.mongo import connect_to_mongo, close_mongo_connection, get_database
from datetime import datetime

app = FastAPI()

# 👇 ADD THIS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    # Insert some dummy data
    db = get_database()
    users_collection = db["users"]
    
    # Clear existing data
    await users_collection.delete_many({})
    
    # Insert dummy users
    dummy_users = [
        {"name": "Alice Johnson", "email": "alice@example.com", "role": "Developer", "status": "Active", "joined": datetime(2024, 1, 15)},
        {"name": "Bob Smith", "email": "bob@example.com", "role": "Designer", "status": "Active", "joined": datetime(2024, 2, 20)},
        {"name": "Charlie Brown", "email": "charlie@example.com", "role": "Manager", "status": "Active", "joined": datetime(2024, 3, 10)},
        {"name": "Diana Prince", "email": "diana@example.com", "role": "Developer", "status": "Active", "joined": datetime(2024, 4, 5)},
        {"name": "Eve Davis", "email": "eve@example.com", "role": "QA Engineer", "status": "Away", "joined": datetime(2024, 5, 12)},
    ]
    await users_collection.insert_many(dummy_users)
    print("✨ Dummy data inserted!")

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Hello from FastAPI 👋"
    }

@app.get("/api/users")
async def get_users():
    db = get_database()
    users_collection = db["users"]
    users = []
    
    async for user in users_collection.find():
        user["_id"] = str(user["_id"])
        if "joined" in user:
            user["joined"] = user["joined"].isoformat()
        users.append(user)
    
    return {"users": users, "count": len(users)}
