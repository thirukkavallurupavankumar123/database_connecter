import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Organization, User
from app.schemas.schemas import SignupRequest, LoginRequest, AuthResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account. Either create a new org or join an existing one."""
    # Check email not already taken
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if not payload.password or len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # Org password is always required
    if not payload.organization_password or len(payload.organization_password) < 4:
        raise HTTPException(status_code=400, detail="Organization password is required (min 4 characters)")

    # Resolve organization
    if payload.organization_id:
        org = db.query(Organization).filter(Organization.id == payload.organization_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        # Verify org password
        if not verify_password(payload.organization_password, org.password_hash):
            raise HTTPException(status_code=403, detail="Incorrect organization password")
    elif payload.organization_name:
        org = Organization(
            name=payload.organization_name,
            password_hash=hash_password(payload.organization_password),
        )
        db.add(org)
        db.flush()
    else:
        raise HTTPException(status_code=400, detail="Provide organization_name (new) or organization_id (existing)")

    # Create user
    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        organization_id=org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(org)

    return AuthResponse(
        user_id=user.id,
        user_name=user.name,
        email=user.email,
        organization_id=org.id,
        organization_name=org.name,
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email and password."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    org = db.query(Organization).filter(Organization.id == user.organization_id).first()

    return AuthResponse(
        user_id=user.id,
        user_name=user.name,
        email=user.email,
        organization_id=org.id,
        organization_name=org.name,
    )


@router.get("/me/{user_id}", response_model=AuthResponse)
def get_current_user(user_id: str, db: Session = Depends(get_db)):
    """Get the current user's profile (session validation)."""
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    org = db.query(Organization).filter(Organization.id == user.organization_id).first()

    return AuthResponse(
        user_id=user.id,
        user_name=user.name,
        email=user.email,
        organization_id=org.id,
        organization_name=org.name,
    )
