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
    companies_collection = db["companies"]
    
    # Clear existing data
    await companies_collection.delete_many({})
    
    # Insert dummy companies
    dummy_companies = [
        {"name": "TechCorp Inc", "industry": "Technology", "revenue": 5000000, "employees": 150, "founded": datetime(2015, 3, 10), "status": "Active"},
        {"name": "Global Solutions", "industry": "Consulting", "revenue": 8500000, "employees": 220, "founded": datetime(2012, 7, 22), "status": "Active"},
        {"name": "DataFlow Systems", "industry": "Software", "revenue": 3200000, "employees": 85, "founded": datetime(2018, 1, 5), "status": "Active"},
        {"name": "Innovate Labs", "industry": "Research", "revenue": 2100000, "employees": 45, "founded": datetime(2020, 9, 14), "status": "Active"},
        {"name": "CloudNet Services", "industry": "Cloud Computing", "revenue": 12000000, "employees": 320, "founded": datetime(2010, 11, 30), "status": "Active"},
        {"name": "SecureVault Inc", "industry": "Cybersecurity", "revenue": 6700000, "employees": 180, "founded": datetime(2016, 5, 18), "status": "Active"},
        {"name": "AgriTech Solutions", "industry": "Agriculture", "revenue": 4300000, "employees": 120, "founded": datetime(2017, 8, 9), "status": "Active"},
        {"name": "FinanceHub", "industry": "Finance", "revenue": 9800000, "employees": 250, "founded": datetime(2013, 4, 25), "status": "Active"},
    ]
    await companies_collection.insert_many(dummy_companies)
    print("✨ Dummy data inserted!")

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Hello from FastAPI"
    }

@app.get("/api/companies")
async def get_companies():
    db = get_database()
    companies_collection = db["companies"]
    companies = []
    
    async for company in companies_collection.find():
        company["_id"] = str(company["_id"])
        if "founded" in company:
            company["founded"] = company["founded"].isoformat()
        companies.append(company)
    
    return {"companies": companies, "count": len(companies)}
