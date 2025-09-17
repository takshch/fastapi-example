#!/usr/bin/env python3
"""
Script to seed the database with sample employee data
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, close_mongo_connection, get_database

async def seed_data():
    """Seed the database with sample employee data"""
    await connect_to_mongo()
    
    database = await get_database()
    collection = database["employees"]
    
    # Sample employee data
    sample_employees = [
        {
            "employee_id": "E001",
            "name": "John Doe",
            "department": "Engineering",
            "salary": 75000,
            "joining_date": "2023-01-15",
            "skills": ["Python", "MongoDB", "APIs"]
        },
        {
            "employee_id": "E002",
            "name": "Jane Smith",
            "department": "Engineering",
            "salary": 85000,
            "joining_date": "2023-02-20",
            "skills": ["JavaScript", "React", "Node.js"]
        },
        {
            "employee_id": "E003",
            "name": "Mike Johnson",
            "department": "HR",
            "salary": 60000,
            "joining_date": "2023-03-10",
            "skills": ["Recruitment", "Employee Relations", "HRIS"]
        },
        {
            "employee_id": "E004",
            "name": "Sarah Wilson",
            "department": "Engineering",
            "salary": 90000,
            "joining_date": "2023-04-05",
            "skills": ["Python", "Docker", "Kubernetes", "AWS"]
        },
        {
            "employee_id": "E005",
            "name": "David Brown",
            "department": "Marketing",
            "salary": 55000,
            "joining_date": "2023-05-12",
            "skills": ["Digital Marketing", "SEO", "Analytics"]
        },
        {
            "employee_id": "E006",
            "name": "Lisa Davis",
            "department": "HR",
            "salary": 65000,
            "joining_date": "2023-06-18",
            "skills": ["Training", "Performance Management", "Compensation"]
        },
        {
            "employee_id": "E007",
            "name": "Tom Anderson",
            "department": "Engineering",
            "salary": 80000,
            "joining_date": "2023-07-22",
            "skills": ["Java", "Spring Boot", "Microservices"]
        },
        {
            "employee_id": "E008",
            "name": "Emily Taylor",
            "department": "Marketing",
            "salary": 58000,
            "joining_date": "2023-08-30",
            "skills": ["Content Marketing", "Social Media", "Brand Management"]
        }
    ]
    
    # Clear existing data
    await collection.delete_many({})
    print("Cleared existing employee data")
    
    # Insert sample data
    result = await collection.insert_many(sample_employees)
    print(f"Inserted {len(result.inserted_ids)} sample employees")
    
    # Verify the data
    count = await collection.count_documents({})
    print(f"Total employees in database: {count}")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed_data())
