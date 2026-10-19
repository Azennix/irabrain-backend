import hashlib
import secrets
from datetime import datetime, timedelta

import bcrypt

from database.user_repository import UserRepository
from services.google import verify_google_id_token
from services.account_provisioning_service import (
    AccountProvisioningService,
)

class AuthService:

    def __init__(
        self,
        user_repository: UserRepository,
        account_provisioning_service: AccountProvisioningService,
    ):
        self.user_repository = user_repository
        self.account_provisioning_service = (
        account_provisioning_service
    )

    # =====================================================
    # NORMALIZE EMAIL
    # =====================================================

    def _normalize_email(self, email: str) -> str:
        return email.strip().lower()

    # =====================================================
    # HASH PASSWORD
    # =====================================================

    def _hash_password(self, password: str) -> str:

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        return password_hash.decode("utf-8")

    # =====================================================
    # VERIFY PASSWORD
    # =====================================================

    def _verify_password(
        self,
        password: str,
        password_hash: str
    ) -> bool:

        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    # =====================================================
    # EMAIL VERIFICATION CODE
    # =====================================================

    def _generate_email_verification_code(self) -> str:

        return f"{secrets.randbelow(1_000_000):06d}"

    def _hash_email_verification_code(
        self,
        code: str
    ) -> str:

        return hashlib.sha256(
            code.encode("utf-8")
        ).hexdigest()

    # =====================================================
    # REGISTER
    # =====================================================

    def register(
        self,
        full_name: str,
        email: str,
        password: str
    ):
        full_name = full_name.strip()

        if not full_name:
            raise ValueError("Full name is required.")

        email = self._normalize_email(email)

        # -------------------------------------------------
        # ACCOUNT MUST NOT ALREADY EXIST
        # -------------------------------------------------

        existing_user = (
            self.user_repository.get_by_email(email)
        )

        if existing_user is not None:

            raise ValueError(
                "An account with this email already exists. "
                "Please sign in instead."
            )

        # -------------------------------------------------
        # PASSWORD
        # -------------------------------------------------

        password_hash = self._hash_password(password)

        # -------------------------------------------------
        # GENERATE 6-DIGIT VERIFICATION CODE
        # -------------------------------------------------

        verification_code = (
            self._generate_email_verification_code()
        )

        verification_code_hash = (
            self._hash_email_verification_code(
                verification_code
            )
        )

        verification_expires_at = (
            datetime.utcnow()
            + timedelta(minutes=10)
        )

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        try:

            user = self.user_repository.create(
                full_name=full_name,
                email=email,
                password_hash=password_hash
            )


            self.account_provisioning_service.provision_new_account(
                user_id=user.user_id,
)

            user.email_verified = False

            user.email_verification_code_hash = (
                verification_code_hash
            )

            user.email_verification_code_expires_at = (
                verification_expires_at
            )

            self.user_repository.commit()

            return user, verification_code

        except Exception:

            self.user_repository.rollback()

            raise

    # =====================================================
    # VERIFY EMAIL WITH 6-DIGIT CODE
    # =====================================================

    def verify_email_code(
        self,
        email: str,
        code: str
):
        email = self._normalize_email(email)
        code = code.strip()

    # -------------------------------------------------
    # CODE FORMAT
    # -------------------------------------------------

        if not code.isdigit() or len(code) != 6:
            raise ValueError(
                "Verification code must be 6 digits."
        )

    # -------------------------------------------------
    # FIND USER
    # -------------------------------------------------

        user = (
            self.user_repository.get_by_email(email)
    )

        if user is None:
             raise ValueError(
                "Unable to verify this email."
        )

    # -------------------------------------------------
    # ALREADY VERIFIED
    # -------------------------------------------------

        if user.email_verified:
            return user, False

    # -------------------------------------------------
    # CHECK CODE EXISTS
    # -------------------------------------------------

        if not user.email_verification_code_hash:
            raise ValueError(
                "No verification code is active."
        )

    # -------------------------------------------------
    # CHECK EXPIRATION
    # -------------------------------------------------

        if (
            user.email_verification_code_expires_at
            is None
            or
            user.email_verification_code_expires_at
             < datetime.utcnow()
    ):
            raise ValueError(
                "This verification code has expired."
        )

    # -------------------------------------------------
    # HASH ENTERED CODE
    # -------------------------------------------------

        code_hash = (
            self._hash_email_verification_code(code)
    )

    # -------------------------------------------------
    # COMPARE
    # -------------------------------------------------

        if code_hash != user.email_verification_code_hash:
            raise ValueError(
                "Invalid verification code."
        )

    # -------------------------------------------------
    # VERIFY ACCOUNT
    # -------------------------------------------------

        user.email_verified = True

        user.email_verification_code_hash = None

        user.email_verification_code_expires_at = None

        self.user_repository.commit()

        return user, True

    # =====================================================
    # NORMAL LOGIN
    # =====================================================

    def authenticate(
        self,
        email: str,
        password: str
    ):

        email = self._normalize_email(email)

        user = (
            self.user_repository.get_by_email(email)
        )

        if user is None:

            raise ValueError(
                "Invalid email or password."
            )

        if not user.is_active:

            raise ValueError(
                "User account is inactive."
            )

        if not user.email_verified:

            raise ValueError(
                "Please verify your email before signing in."
            )

        if not user.password_hash:

            raise ValueError(
                "This account uses Google sign-in."
            )

        password_valid = (
            self._verify_password(
                password=password,
                password_hash=user.password_hash
            )
        )

        if not password_valid:

            raise ValueError(
                "Invalid email or password."
            )

        return user


    # =====================================================
# UPDATE CURRENT USER PROFILE
# =====================================================

       # =====================================================
    # UPDATE CURRENT USER PROFILE
    # =====================================================

    def update_profile(
        self,
        user,
        full_name: str,
        email: str
    ):

        full_name = full_name.strip()

        if not full_name:
            raise ValueError("Full name is required.")

        email = self._normalize_email(email)

        # -------------------------------------------------
        # CHECK EMAIL CHANGE
        # -------------------------------------------------

        if email != user.email:

            existing_user = (
                self.user_repository.get_by_email(email)
            )

            if (
                existing_user is not None
                and existing_user.user_id != user.user_id
            ):
                raise ValueError(
                    "An account with this email already exists."
                )

        # -------------------------------------------------
        # UPDATE PROFILE
        # -------------------------------------------------

        try:

            updated_user = (
                self.user_repository.update_profile(
                    user=user,
                    full_name=full_name,
                    email=email,
                )
            )

            self.user_repository.commit()

            return updated_user

        except Exception:

            self.user_repository.rollback()

            raise



            # =====================================================
    # CHANGE PASSWORD
    # =====================================================

    def change_password(
        self,
        user,
        current_password: str,
        new_password: str
    ):

        # -------------------------------------------------
        # GOOGLE ACCOUNTS
        # -------------------------------------------------

        if not user.password_hash:

            raise ValueError(
                "This account uses Google sign-in."
            )

        # -------------------------------------------------
        # CURRENT PASSWORD
        # -------------------------------------------------

        if not self._verify_password(
            password=current_password,
            password_hash=user.password_hash
        ):

            raise ValueError(
                "Current password is incorrect."
            )

        # -------------------------------------------------
        # NEW PASSWORD
        # -------------------------------------------------

        if len(new_password) < 8:

            raise ValueError(
                "New password must be at least 8 characters."
            )

        if new_password == current_password:

            raise ValueError(
                "New password must be different from your current password."
            )

        # -------------------------------------------------
        # HASH NEW PASSWORD
        # -------------------------------------------------

        try:

            user.password_hash = (
                self._hash_password(new_password)
            )

            self.user_repository.commit()

            return user

        except Exception:

            self.user_repository.rollback()

            raise







    # =====================================================
    # GOOGLE LOGIN
    # =====================================================

    def authenticate_google(
        self,
        credential: str
    ):

        google_user = verify_google_id_token(
            credential
        )

        # -------------------------------------------------
        # GOOGLE EMAIL MUST BE VERIFIED
        # -------------------------------------------------

        if not google_user["email_verified"]:

            raise ValueError(
                "Google email is not verified."
            )

        google_sub = google_user["google_sub"]

        email = self._normalize_email(
            google_user["email"]
        )

        # -------------------------------------------------
        # 1. FIND BY GOOGLE SUB
        # -------------------------------------------------

        user = (
            self.user_repository.get_by_google_sub(
                google_sub
            )
        )

        if user is not None:

            if not user.is_active:

                raise ValueError(
                    "User account is inactive."
                )

            return user

        # -------------------------------------------------
        # 2. FIND BY EMAIL
        # -------------------------------------------------

        existing_user = (
            self.user_repository.get_by_email(email)
        )

        if existing_user is not None:

            if not existing_user.is_active:

                raise ValueError(
                    "User account is inactive."
                )

            # Link Google to EXISTING IRABRAIN identity
            existing_user.google_sub = google_sub

            # Google has already verified the email
            existing_user.email_verified = True

            self.user_repository.commit()

            return existing_user

        # -------------------------------------------------
        # 3. CREATE GOOGLE USER
        # -------------------------------------------------

        try:
            user = self.user_repository.create_google_user(
                email=email,
                google_sub=google_sub,
)

            self.account_provisioning_service.provision_new_account(
                user_id=user.user_id,
)





            user.email_verified = True

            self.user_repository.commit()

            return user

        except Exception:

            self.user_repository.rollback()

            raise

    # =====================================================
    # RESEND VERIFICATION CODE
    # =====================================================

    def resend_verification(
        self,
        email: str
    ):

        email = self._normalize_email(email)

        user = (
            self.user_repository.get_by_email(email)
        )

        if user is None:

            raise ValueError(
                "Unable to send verification code."
            )

        if user.email_verified:

            return user, None

        verification_code = (
            self._generate_email_verification_code()
        )

        verification_code_hash = (
            self._hash_email_verification_code(
                verification_code
            )
        )

        verification_expires_at = (
            datetime.utcnow()
            + timedelta(minutes=10)
        )

        user.email_verification_code_hash = (
            verification_code_hash
        )

        user.email_verification_code_expires_at = (
            verification_expires_at
        )

        self.user_repository.commit()

        return user, verification_code


        # =====================================================
    # PASSWORDLESS EMAIL AUTHENTICATION
    # =====================================================

    def request_email_auth_code(
        self,
        full_name: str,
        email: str
    ):
        full_name = full_name.strip()
        email = self._normalize_email(email)

        if not full_name:
            raise ValueError("Full name is required.")

        user = self.user_repository.get_by_email(email)

        # -------------------------------------------------
        # CREATE NEW USER
        # -------------------------------------------------

        if user is None:
            user = self.user_repository.create(
                full_name=full_name,
                email=email,
                password_hash=None
            )
            self.account_provisioning_service.provision_new_account(
                user_id=user.user_id,
)

        # -------------------------------------------------
        # EXISTING USER
        # -------------------------------------------------

        else:
            if not user.is_active:
                raise ValueError("User account is inactive.")

            # Update name when supplied
            if full_name:
                user.full_name = full_name

        # -------------------------------------------------
        # GENERATE EMAIL CODE
        # -------------------------------------------------

        verification_code = (
            self._generate_email_verification_code()
        )

        verification_code_hash = (
            self._hash_email_verification_code(
                verification_code
            )
        )

        verification_expires_at = (
            datetime.utcnow() + timedelta(minutes=10)
        )

        user.email_verification_code_hash = (
            verification_code_hash
        )

        user.email_verification_code_expires_at = (
            verification_expires_at
        )

        self.user_repository.commit()

        return user, verification_code


        # =====================================================
    # VERIFY PASSWORDLESS LOGIN CODE
    # =====================================================

    def verify_login_code(
        self,
        email: str,
        code: str
    ):
        email = self._normalize_email(email)

        if not code or not code.isdigit() or len(code) != 6:
            raise ValueError("Invalid verification code.")

        user = self.user_repository.get_by_email(email)

        if user is None:
            raise ValueError("Invalid verification code.")

        if not user.is_active:
            raise ValueError("User account is inactive.")

        # -------------------------------------------------
        # CHECK CODE EXISTS
        # -------------------------------------------------

        if not user.email_verification_code_hash:
            raise ValueError("Verification code is invalid or expired.")

        # -------------------------------------------------
        # CHECK EXPIRY
        # -------------------------------------------------

        if (
            not user.email_verification_code_expires_at
            or datetime.utcnow()
            > user.email_verification_code_expires_at
        ):
            raise ValueError("Verification code has expired.")

        # -------------------------------------------------
        # CHECK CODE
        # -------------------------------------------------

        code_hash = self._hash_email_verification_code(code)

        if code_hash != user.email_verification_code_hash:
            raise ValueError("Invalid verification code.")

        # -------------------------------------------------
        # VERIFY EMAIL
        # -------------------------------------------------

        user.email_verified = True

        # -------------------------------------------------
        # CLEAR USED CODE
        # -------------------------------------------------

        user.email_verification_code_hash = None
        user.email_verification_code_expires_at = None

        self.user_repository.commit()

        return user