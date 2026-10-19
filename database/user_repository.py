from sqlalchemy.orm import Session

from database.user_model import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # FIND USER BY ID
    # =====================================================

    def get_by_id(
        self,
        user_id: int
    ) -> User | None:

        return (
            self.db.query(User)
            .filter(
                User.user_id == user_id
            )
            .first()
        )


    def get_brain_tier(
        self,
        user_id: int
    ) -> str:

        user = self.get_by_id(user_id)

        if user is None:
            raise ValueError(
                f"User not found: {user_id}"
            )

        return user.brain_tier

        # =====================================================
    # UPDATE USER BRAIN TIER
    # =====================================================

    def update_brain_tier(
        self,
        user_id: int,
        tier: str
    ) -> User:

        user = self.get_by_id(user_id)

        if user is None:
            raise ValueError(
                f"User not found: {user_id}"
            )

        user.brain_tier = tier

        self.db.flush()

        return user

    # =====================================================
    # FIND USER BY EMAIL
    # =====================================================

    def get_by_email(
        self,
        email: str
    ) -> User | None:

        return (
            self.db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

    # =====================================================
# UPDATE USER PROFILE
# =====================================================

    # =====================================================
    # UPDATE USER PROFILE
    # =====================================================

    def update_profile(
        self,
        user: User,
        full_name: str,
        email: str
    ) -> User:

        user.full_name = full_name
        user.email = email

        self.db.flush()

        return user

    # =====================================================
    # FIND USER BY GOOGLE ID
    # =====================================================

    def get_by_google_sub(
        self,
        google_sub: str
    ) -> User | None:

        return (
            self.db.query(User)
            .filter(
                User.google_sub == google_sub
            )
            .first()
        )

    # =====================================================
    # CREATE NORMAL USER
    # =====================================================

    def create(
        self,
        full_name: str,
        email: str,
        password_hash: str | None
    ) -> User:

        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash
        )

        self.db.add(user)

        self.db.flush()

        return user

    # =====================================================
    # CREATE GOOGLE USER
    # =====================================================

    def create_google_user(
        self,
        email: str,
        google_sub: str
    ) -> User:

        user = User(
            email=email,
            password_hash=None,
            google_sub=google_sub
        )

        self.db.add(user)

        self.db.flush()

        return user

    # =====================================================
    # LINK GOOGLE ACCOUNT
    # =====================================================

    def link_google_account(
        self,
        user: User,
        google_sub: str
    ) -> User:

        user.google_sub = google_sub

        self.db.flush()

        return user


        # =====================================================
    # FIND USER BY VERIFICATION TOKEN
    # =====================================================

    def get_by_email_verification_token_hash(
        self,
        token_hash: str
    ) -> User | None:

        return (
            self.db.query(User)
            .filter(
                User.email_verification_token_hash
                == token_hash
            )
            .first()
        )

    # =====================================================
    # SAVE CHANGES
    # =====================================================

    def commit(self) -> None:

        self.db.commit()

    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(self) -> None:

        self.db.rollback()