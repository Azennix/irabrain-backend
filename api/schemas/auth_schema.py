from pydantic import BaseModel, EmailStr, Field

# =====================================================
# REGISTER
# =====================================================

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


# =====================================================
# LOGIN
# =====================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


# =====================================================
# CHECK EMAIL
# =====================================================

class CheckEmailRequest(BaseModel):

    email: EmailStr


# =====================================================
# VERIFY EMAIL CODE
# =====================================================

class VerifyEmailCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^[0-9]{6}$")


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
    full_name: str | None
    email: EmailStr
    is_active: bool
    google_connected: bool



# =====================================================
# UPDATE CURRENT USER
# =====================================================

class UpdateCurrentUserRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr


# =====================================================
# CHANGE PASSWORD
# =====================================================

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)

# =====================================================
# AUTH RESPONSE
# =====================================================

class AuthResponse(BaseModel):

    access_token: str
    token_type: str
    user: UserResponse

# =====================================================
# EMAIL CODE AUTHENTICATION
# =====================================================

class RequestEmailCodeRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class VerifyLoginCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^[0-9]{6}$")