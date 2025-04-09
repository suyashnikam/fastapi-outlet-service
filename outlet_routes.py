from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
import models, schemas, database
from models import Outlet
import requests
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()

outlet_router = APIRouter(prefix="/outlet", tags=["Outlet"])


# ✅ Create new outlet
@outlet_router.post("/create", response_model=schemas.OutletOut, status_code=status.HTTP_201_CREATED)
def create_outlet(
    outlet: schemas.OutletCreate,
    db: Session = Depends(database.get_db),
    authorization: Optional[str] = Header(None)
):
    new_outlet = Outlet(**outlet.dict())
    db.add(new_outlet)
    db.commit()
    db.refresh(new_outlet)
    return new_outlet


# ✅ Get all outlets
@outlet_router.get("/", response_model= list[schemas.OutletOut])
def list_outlets(
    db: Session = Depends(database.get_db),
    authorization: Optional[str] = Header(None)
):
    return db.query(Outlet).all()


# ✅ Get outlet by ID
@outlet_router.get("/{outlet_id}", response_model=schemas.OutletOut)
def get_outlet(
    outlet_id: int,
    db: Session = Depends(database.get_db),
    authorization: Optional[str] = Header(None)
):
    outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found for this ID!!")
    return outlet


# ✅ Get outlet by ID
@outlet_router.get("/by-code/{outlet_code}", response_model=schemas.OutletOut)
def get_outlet(
    outlet_code: str,
    db: Session = Depends(database.get_db),
    authorization: Optional[str] = Header(None)
):
    outlet = db.query(models.Outlet).filter(models.Outlet.code == outlet_code).first()
    print(authorization)
    print("Outlet for code outlet_code",outlet)
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found with this code!!")
    return outlet


# ✅ Update outlet
@outlet_router.put("/{outlet_id}", response_model=schemas.OutletOut)
def update_outlet(
    outlet_id: int,
    outlet_data: schemas.OutletCreate,
    db: Session = Depends(database.get_db),
    authorization: Optional[str] = Header(None)
):
    outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")

    for field, value in outlet_data.dict().items():
        setattr(outlet, field, value)

    db.commit()
    db.refresh(outlet)
    return outlet


# ✅ Delete outlet
@outlet_router.delete("/{outlet_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_outlet(
    outlet_id: int,
    db: Session = Depends(database.get_db),
    authorization: Optional[str] = Header(None)
):
    outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")

    db.delete(outlet)
    db.commit()
    return {"message": f"Outlet with ID {outlet_id} has been deleted successfully"}

# ✅ Get available pizzas at outlet
@outlet_router.get("/{outlet_code}/pizzas", response_model=list[dict])
def get_outlet_pizzas(
    outlet_code: str,
    db: Session = Depends(database.get_db),
    Authorization: Optional[str] = Header(None)
):
    outlet = db.query(models.Outlet).filter(models.Outlet.code == outlet_code).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")

    try:
        headers = {"Authorization": f"{Authorization}"}
        pizza_service_url = os.getenv("PIZZA_SERVICE_BASE_URL",
                                       "http://127.0.0.1:8005") + f"/pizza/for-outlet/{outlet_code}"
        print(pizza_service_url)
        print(headers)
        response = requests.get(pizza_service_url, headers=headers, timeout=5)
        print(response)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Pizza service error: {str(e)}")