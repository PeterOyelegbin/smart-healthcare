from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from math import ceil
from database.db_config import get_db
from database import models, schema

router = APIRouter(prefix="/api/v1/patients", tags=["Patients"])

@router.post("/", response_model=schema.PatientResponse, status_code=status.HTTP_201_CREATED, summary="Create a new patient record")
async def create_patient(patient_data: schema.PatientCreate, db: Session = Depends(get_db)):
    """
    Create a new patient record. Requires authenticated user.

    - Checks if patient record already exists for this user
    - Creates new patient record
    """
    existing_patient = db.query(models.Patient).filter(models.Patient.email == patient_data.email).first()
    if existing_patient:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Patient record already exists for user {patient_data.email}")
    try:
        patient = models.Patient(**patient_data.model_dump())
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient
    except Exception as e:
        print(f"Error creating patient record: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create patient record")

@router.get("/", response_model=schema.PatientListResponse)
async def get_patients(db: Session = Depends(get_db), page: int = 1, page_size: int = 20):
    """
    Get paginated patient records. Requires authenticated user.
    """
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    skip = (page - 1) * page_size
    patients = db.query(models.Patient).offset(skip).limit(page_size).all()
    total = db.query(models.Patient).count()
    total_pages = ceil(total / page_size) if total > 0 else 1
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "patients": patients}

@router.get("/search", response_model=schema.PatientListResponse)
async def search_patients(query: str, db: Session = Depends(get_db), page: int = 1, page_size: int = 20):
    """
    Search patient records by name or email. Requires authenticated user.
    """
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    skip = (page - 1) * page_size
    search_query = db.query(models.Patient).filter(
        (models.Patient.name.ilike(f"%{query}%")) | (models.Patient.email.ilike(f"%{query}%"))
    )
    patients = search_query.offset(skip).limit(page_size).all()
    total = search_query.count()
    total_pages = ceil(total / page_size) if total > 0 else 1
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "patients": patients}

@router.get("/{patient_id}", response_model=schema.PatientResponse)
async def get_patient(patient_id: UUID, db: Session = Depends(get_db)):
    """
    Get a patient record by ID. Requires authenticated user.
    """
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient

@router.patch("/{patient_id}", status_code=status.HTTP_200_OK, response_model=schema.PatientResponse)
async def update_patient(patient_id: UUID, patient_data: schema.PatientUpdate, db: Session = Depends(get_db)):
    """
    Update a patient record by ID. Requires authenticated user.
    """
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    for key, value in patient_data.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient
