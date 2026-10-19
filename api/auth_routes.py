import logging
logger = logging.getLogger(__name__)
from pydantic import BaseModel, EmailStr

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database.dependencies import get_db
from database.user_repository import UserRepository

from services.auth_service import AuthService
from services.account_provisioning_service import (
    AccountProvisioningService,

)
from services.auth_rate_limiter import auth_rate_limiter
from services.email_service import send_email

from api.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    CheckEmailRequest,
    VerifyEmailCodeRequest,
    ResendVerificationRequest,
    RequestEmailCodeRequest,
    VerifyLoginCodeRequest,
    UserResponse,
    UpdateCurrentUserRequest,
    ChangePasswordRequest,
    AuthResponse,
)

from core.security import create_access_token
from security.dependencies import get_current_user
from api.notification_dependencies import get_notification_service
from brain.notification.notification_service import NotificationService
from brain.notification.notification_types import NotificationType

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

def enforce_auth_rate_limit(
    request: Request,
    action: str,
    limit: int,
    window_seconds: int,
) -> None:
    client_ip = (
        request.client.host
        if request.client is not None
        else "unknown"
    )

    allowed = auth_rate_limiter.allow(
        key=f"{action}:{client_ip}",
        limit=limit,
        window_seconds=window_seconds,
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Please try again later.",
            headers={"Retry-After": str(window_seconds)},
        )


# =====================================================
# REGISTER
# =====================================================

@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    request: RegisterRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate_limit(http_request, "register", 5, 3600)
    repository = UserRepository(db)

    account_provisioning_service = AccountProvisioningService(
        db=db
    )

    auth_service = AuthService(
        user_repository=repository,
        account_provisioning_service=account_provisioning_service,
    )

    try:
        user, verification_code = auth_service.register(
            full_name=request.full_name,
            email=request.email,
            password=request.password,
        )

        # -------------------------------------------------
        # SEND VERIFICATION EMAIL
        # -------------------------------------------------

        send_email(
            to_email=user.email,
            subject="Your IRABRAIN verification code",
            body=f"""
Welcome to IRABRAIN.

Your verification code is:

{verification_code}

This code expires in 10 minutes.

If you did not create an IRABRAIN account, you can ignore this email.

— IRABRAIN
""",
        )

        return UserResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            is_active=user.is_active,
            google_connected=user.google_sub is not None,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from None
    except Exception:
        logger.exception("Registration failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to complete registration.",
        )  from None


# =====================================================
# CHECK EMAIL
# =====================================================

@router.post("/check-email")
def check_email(
    request: CheckEmailRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate_limit(http_request, "check_email", 20, 600)
    repository = UserRepository(db)

    email = str(request.email).strip().lower()

    user = repository.get_by_email(email)

    # -------------------------------------------------
    # NEW EMAIL
    # -------------------------------------------------

    if user is None:
        return {
            "exists": False,
            "email_verified": False,
            "next": "create_password",
        }

    # -------------------------------------------------
    # EXISTING VERIFIED ACCOUNT
    # -------------------------------------------------

    if user.email_verified:
        return {
            "exists": True,
            "email_verified": True,
            "next": "login",
        }

    # -------------------------------------------------
    # EXISTING BUT NOT VERIFIED
    # -------------------------------------------------

    return {
        "exists": True,
        "email_verified": False,
        "next": "verify_email",
    }


# =====================================================
# VERIFY EMAIL CODE
# =====================================================

@router.post("/verify-email-code")
def verify_email_code(
    request: VerifyEmailCodeRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    notification_service: NotificationService = Depends(
        get_notification_service
    ),
):
    enforce_auth_rate_limit(http_request, "verify_email", 10, 600)
    repository = UserRepository(db)

    account_provisioning_service = AccountProvisioningService(
        db=db
    )

    auth_service = AuthService(
        user_repository=repository,
        account_provisioning_service=account_provisioning_service,
    )

    try:
        user, newly_verified = auth_service.verify_email_code(
            email=request.email,
            code=request.code,
        )

        if newly_verified:
            notification_service.create_notification(
                user_id=user.user_id,
                type=NotificationType.SYSTEM,
                title="Welcome to IRABRAIN",
                message="Your email is verified and your IRABRAIN account is ready.",
            )

        return {
            "message": "Email verified successfully.",
            "email": user.email,
            "email_verified": user.email_verified,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception :
        logger.exception("Email code verification failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to verify email.",
        ) from None


# =====================================================
# RESEND VERIFICATION CODE
# =====================================================

@router.post("/resend-verification")
def resend_verification(
    request: ResendVerificationRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate_limit(http_request, "resend_verification", 3, 900)
    repository = UserRepository(db)

    account_provisioning_service = AccountProvisioningService(
        db=db
    )

    auth_service = AuthService(
        user_repository=repository,
        account_provisioning_service=account_provisioning_service,
    )

    try:
        user, verification_code = (
            auth_service.resend_verification(
                email=request.email
            )
        )

        # -------------------------------------------------
        # ALREADY VERIFIED
        # -------------------------------------------------

        if verification_code is None:
            return {
                "message": "Email is already verified.",
                "email": user.email,
            }

        # -------------------------------------------------
        # SEND NEW CODE
        # -------------------------------------------------

        send_email(
            to_email=user.email,
            subject="Your new IRABRAIN verification code",
            body=f"""
Your new IRABRAIN verification code is:

{verification_code}

This code expires in 10 minutes.

If you did not request this code, you can ignore this email.

— IRABRAIN
""",
        )

        return {
            "message": "A new verification code has been sent.",
            "email": user.email,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception:
        logger.exception("Resend verification failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to resend verification code.",
        ) from None


# =====================================================
# PASSWORDLESS EMAIL AUTHENTICATION
# =====================================================

@router.post("/request-email-code")
def request_email_code(
    request: RequestEmailCodeRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate_limit(http_request, "request_email_code", 3, 900)
    repository = UserRepository(db)

    account_provisioning_service = AccountProvisioningService(
        db=db
    )

    auth_service = AuthService(
        user_repository=repository,
        account_provisioning_service=account_provisioning_service,
    )

    try:
        user, verification_code = (
            auth_service.request_email_auth_code(
                full_name=request.full_name,
                email=request.email,
            )
        )

        # -------------------------------------------------
        # SEND VERIFICATION EMAIL
        # -------------------------------------------------

        send_email(
            to_email=user.email,
            subject="Your IRABRAIN verification code",
            body=f"""
Welcome to IRABRAIN.

Your verification code is:

{verification_code}

This code expires in 10 minutes.

If you did not create an IRABRAIN account, you can ignore this email.

— IRABRAIN
""",
        )

        return {
            "message": "Verification code sent.",
            "email": user.email,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception:
        logger.exception("Passwordless email code request failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to send verification code.",
        ) from None


# =====================================================
# VERIFY PASSWORDLESS LOGIN CODE
# =====================================================

@router.post(
    "/verify-login-code",
    response_model=AuthResponse,
)
def verify_login_code(
    request: VerifyLoginCodeRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate_limit(http_request, "verify_login_code", 10, 600)
    repository = UserRepository(db)

    account_provisioning_service = AccountProvisioningService(
        db=db
    )

    auth_service = AuthService(
        user_repository=repository,
        account_provisioning_service=account_provisioning_service,
    )

    try:
        user = auth_service.verify_login_code(
            email=request.email,
            code=request.code,
        )

        access_token = create_access_token(
            user.user_id
        )

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                user_id=user.user_id,
                full_name=user.full_name,
                email=user.email,
                is_active=user.is_active,
                google_connected=user.google_sub is not None,
            ),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )

    except Exception:
        logger.exception("Passwordless login verification failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to verify login code.",
        ) from None


# =====================================================
# LOGIN
# =====================================================

@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate_limit(http_request, "login", 10, 300)
    repository = UserRepository(db)

    account_provisioning_service = AccountProvisioningService(
        db=db
    )

    auth_service = AuthService(
        user_repository=repository,
        account_provisioning_service=account_provisioning_service,
    )

    try:
        user = auth_service.authenticate(
            email=request.email,
            password=request.password,
        )

        access_token = create_access_token(
            user.user_id
        )

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                user_id=user.user_id,
                full_name=user.full_name,
                email=user.email,
                is_active=user.is_active,
                google_connected=user.google_sub is not None,
            ),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )


# =====================================================
# GOOGLE LOGIN
# =====================================================

class GoogleLoginRequest(BaseModel):
    credential: str


@router.post(
    "/google",
    response_model=AuthResponse,
)
def google_login(
    request: GoogleLoginRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate_limit(http_request, "google_login", 10, 300)
    repository = UserRepository(db)

    account_provisioning_service = AccountProvisioningService(
        db=db
    )

    auth_service = AuthService(
        user_repository=repository,
        account_provisioning_service=account_provisioning_service,
    )

    try:
        user = auth_service.authenticate_google(
            credential=request.credential
        )

        access_token = create_access_token(
            user.user_id
        )

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                user_id=user.user_id,
                full_name=user.full_name,
                email=user.email,
                is_active=user.is_active,
                google_connected=user.google_sub is not None,
            ),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )


# =====================================================
# CURRENT USER
# =====================================================

@router.get("/me")
def get_me(
    current_user=Depends(get_current_user),
):
    return {
        "user_id": current_user.user_id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "google_connected": current_user.google_sub is not None,
        "brain_tier": current_user.brain_tier,
    }


# =====================================================
# UPDATE CURRENT USER
# =====================================================

@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_me(
    request: UpdateCurrentUserRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = UserRepository(db)

    account_provisioning_service = AccountProvisioningService(
        db=db
    )

    auth_service = AuthService(
        user_repository=repository,
        account_provisioning_service=account_provisioning_service,
    )

    try:
        user = auth_service.update_profile(
            user=current_user,
            full_name=request.full_name,
            email=request.email,
        )

        return UserResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            is_active=user.is_active,
            google_connected=user.google_sub is not None,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception :
        logger.exception("Profile update failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to update profile.",
        ) from None


# =====================================================
# CHANGE PASSWORD
# =====================================================

@router.patch("/password")
def change_password(
    request: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = UserRepository(db)

    account_provisioning_service = AccountProvisioningService(
        db=db
    )

    auth_service = AuthService(
        user_repository=repository,
        account_provisioning_service=account_provisioning_service,
    )

    try:
        auth_service.change_password(
            user=current_user,
            current_password=request.current_password,
            new_password=request.new_password,
        )

        return {
            "success": True,
            "message": "Password changed successfully.",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception:
        logger.exception("Password change failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to change password.",
        ) from None