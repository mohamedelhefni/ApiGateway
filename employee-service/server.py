from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory storage for employees
employees = {}

# Pydantic model for employee
class Employee(BaseModel):
    name: str
    age: int
    description: str

# Create a new employee
@app.post("/employees/", response_model=Employee)
def create_employee(employee: Employee):
    employee_id = len(employees) + 1
    employees[employee_id] = employee
    return {"employee_id": employee_id, **employee.dict()}

# Retrieve all employees
@app.get("/employees/", response_model=Dict[int, Employee])
def read_employees():
    return employees

# Retrieve a specific employee by ID
@app.get("/employees/{employee_id}", response_model=Employee)
def read_employee(employee_id: int):
    employee = employees.get(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="employee not found")
    return employee

# Update a employee by ID
@app.put("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, updated_employee: Employee):
    employee = employees.get(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="employee not found")
    
    # Update employee data
    for field, value in updated_employee.dict().items():
        setattr(employee, field, value)
    
    return employee

# Delete a employee by ID
@app.delete("/employees/{employee_id}", response_model=Employee)
def delete_employee(employee_id: int):
    employee = employees.pop(employee_id, None)
    if employee is None:
        raise HTTPException(status_code=404, detail="employee not found")
    return employee

  # uvicorn.run(app, host="0.0.0.0", port=port)
