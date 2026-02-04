from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.db.mongo import connect_to_mongo, close_mongo_connection, get_database
from app.nlp.parser import NLPQueryParser
from datetime import datetime

app = FastAPI()
nlp_parser = NLPQueryParser()

class QueryRequest(BaseModel):
    query: str
    collection: str = "companies"

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
        # Convert datetime fields to ISO format
        if "founded" in company:
            company["founded"] = company["founded"].isoformat()
        companies.append(company)
    
    return {"companies": companies, "count": len(companies)}

@app.post("/api/query")
async def natural_language_query(request: QueryRequest):
    """Process natural language query and return filtered or aggregated results"""
    try:
        # Parse the natural language query
        parsed = nlp_parser.parse(request.query, request.collection)
        
        # Check if parsing failed
        if "error" in parsed:
            return {
                "results": [],
                "count": 0,
                "error": parsed["error"],
                "parsed_filter": {},
                "original_query": request.query
            }
        
        # Get database and collection
        db = get_database()
        collection = db[parsed["collection"]]
        
        # Handle queries asking for document with max/min value
        if parsed.get("query_type") == "find_extreme":
            agg = parsed["aggregation"]
            agg_type = agg["type"]
            field = agg["field"]
            
            # Sort by field and get the first document
            sort_order = -1 if agg_type == "max" else 1
            result = await collection.find_one(sort=[(field, sort_order)])
            
            if result:
                result["_id"] = str(result["_id"])
                # Convert datetime fields to ISO format
                for key, value in result.items():
                    if isinstance(value, datetime):
                        result[key] = value.isoformat()
                
                return {
                    "results": [result],
                    "count": 1,
                    "parsed_filter": {field: {"$" + agg_type: "document"}},
                    "original_query": request.query
                }
            else:
                return {
                    "results": [],
                    "count": 0,
                    "error": "No documents found",
                    "original_query": request.query
                }
        
        # Handle aggregation queries
        if parsed.get("query_type") == "aggregation":
            agg = parsed["aggregation"]
            agg_type = agg["type"]
            field = agg["field"]
            
            if agg_type == "count":
                count = await collection.count_documents({})
                return {
                    "query_type": "aggregation",
                    "aggregation_result": {
                        "operation": "count",
                        "value": count,
                        "field": field
                    },
                    "original_query": request.query
                }
            
            # For sum, avg, max, min
            pipeline = []
            if agg_type == "sum":
                pipeline = [{"$group": {"_id": None, "result": {"$sum": f"${field}"}}}]
            elif agg_type == "avg":
                pipeline = [{"$group": {"_id": None, "result": {"$avg": f"${field}"}}}]
            elif agg_type == "max":
                pipeline = [{"$group": {"_id": None, "result": {"$max": f"${field}"}}}]
            elif agg_type == "min":
                pipeline = [{"$group": {"_id": None, "result": {"$min": f"${field}"}}}]
            
            if pipeline:
                cursor = collection.aggregate(pipeline)
                result = await cursor.to_list(length=1)
                value = result[0]["result"] if result else 0
                
                return {
                    "query_type": "aggregation",
                    "aggregation_result": {
                        "operation": agg_type,
                        "field": field,
                        "value": value
                    },
                    "original_query": request.query
                }
        
        # Handle filter queries
        # Get one document to check available fields
        sample_doc = await collection.find_one()
        if sample_doc:
            available_fields = list(sample_doc.keys())
            available_fields.remove("_id")
            
            # Check if queried field exists in collection
            queried_fields = list(parsed["filter"].keys())
            if queried_fields:
                invalid_fields = [f for f in queried_fields if f not in available_fields]
                if invalid_fields:
                    return {
                        "results": [],
                        "count": 0,
                        "error": f"Field '{invalid_fields[0]}' not found in collection. Available fields: {', '.join(available_fields)}",
                        "parsed_filter": parsed["filter"],
                        "original_query": request.query
                    }
        
        # Execute filter query
        results = []
        async for doc in collection.find(parsed["filter"]):
            doc["_id"] = str(doc["_id"])
            # Convert datetime fields to ISO format
            for key, value in doc.items():
                if isinstance(value, datetime):
                    doc[key] = value.isoformat()
            results.append(doc)
        
        return {
            "results": results,
            "count": len(results),
            "parsed_filter": parsed["filter"],
            "original_query": request.query
        }
    except Exception as e:
        return {
            "results": [],
            "count": 0,
            "error": f"Query execution failed: {str(e)}",
            "parsed_filter": {},
            "original_query": request.query
        }
        if "founded" in company:
            company["founded"] = company["founded"].isoformat()
        companies.append(company)
    
    return {"companies": companies, "count": len(companies)}
