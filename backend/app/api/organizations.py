from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
from app.database import get_db
from app.models.models import Organization, User
from app.schemas.schemas import (
    OrganizationCreate, OrganizationResponse,
    UserCreate, UserResponse, MessageResponse,
)

router = APIRouter(prefix="/api/organizations", tags=["Organizations"])


@router.post("/", response_model=OrganizationResponse)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    if not payload.password or len(payload.password) < 4:
        raise HTTPException(status_code=400, detail="Organization password must be at least 4 characters")
    org = Organization(
        name=payload.name,
        password_hash=bcrypt.hashpw(payload.password.encode(), bcrypt.gensalt()).decode(),
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/", response_model=list[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)):
    return db.query(Organization).all()


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: str, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


# --- Users ---
@router.post("/{org_id}/users", response_model=UserResponse)
def create_user(org_id: str, payload: UserCreate, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=bcrypt.hashpw(payload.password.encode(), bcrypt.gensalt()).decode(),
        organization_id=org_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{org_id}/users", response_model=list[UserResponse])
def list_users(org_id: str, user_id: str = None, db: Session = Depends(get_db)):
    # If user_id provided, verify they belong to this org
    if user_id:
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user or user.organization_id != org_id:
            raise HTTPException(status_code=403, detail="Access denied")
    return db.query(User).filter(User.organization_id == org_id).all()
