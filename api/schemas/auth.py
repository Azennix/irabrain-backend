from pydantic import BaseModel, EmailStr


# =====================================================
# REGISTER
# =====================================================

class RegisterRequest(BaseModel):

    email: EmailStr
    password: str


# =====================================================
# LOGIN
# =====================================================

class LoginRequest(BaseModel):

    email: EmailStr
    password: str


# =====================================================
# VERIFY EMAIL CODE
# =====================================================

class VerifyEmailCodeRequest(BaseModel):

    email: EmailStr
    code: str


# =====================================================
# RESEND VERIFICATION CODE
# =====================================================

class ResendVerificationRequest(BaseModel):

    email: EmailStr


# =====================================================
# USER RESPONSE
# =====================================================

class UserResponse(BaseModel):

    user_id: int
    email: EmailStr
    is_active: bool


# =====================================================
# AUTH RESPONSE
# =====================================================

class AuthResponse(BaseModel):

    access_token: str
    token_type: str
    user: UserResponse