from calendar import day_abbr

from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.openapi.models import Schema
from sqlalchemy.orm import Session
import models, schemas, database
from models import Outlet
import requests
from typing import Optional
from fastapi.encoders import jsonable_encoder

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
        raise HTTPException(status_code=404, detail="Outlet not found")
    return outlet

# # ✅ Get pizzas available at an outlet (mocked or call pizza-service)
# @outlet_router.get("/{outlet_id}/pizzas", response_model=list[dict])
# def get_outlet_pizzas(
#     outlet_id: int,
#     db: Session = Depends(database.get_db),
#     authorization: Optional[str] = Header(None)
# ):
#     outlet = db.query(models.Outlet).filter(models.Outlet.id == outlet_id).first()
#     if not outlet:
#         raise HTTPException(status_code=404, detail="Outlet not found")
#
#     try:
#         # Here you can call pizza-service or use internal mapping
#         response = requests.get("http://localhost:8002/pizza/")  # Adjust pizza-service URL
#         return response.json()
#     except:
#         raise HTTPException(status_code=503, detail="Pizza service unavailable")

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