from typing import Optional

from sqlalchemy.orm import Session

from brain.self_development.persistence.system_identity_model import (
    SystemIdentityModel,
)


class SystemIdentityRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        system_id: str,
    ) -> Optional[SystemIdentityModel]:
        return (
            self.db.query(SystemIdentityModel)
            .filter(
                SystemIdentityModel.system_id == system_id
            )
            .first()
        )

    def get_by_name(
        self,
        name: str,
    ) -> Optional[SystemIdentityModel]:
        return (
            self.db.query(SystemIdentityModel)
            .filter(
                SystemIdentityModel.name == name
            )
            .first()
        )

    def create(
        self,
        system_id: str,
        name: str,
        is_active: bool = True,
    ) -> SystemIdentityModel:

        identity = SystemIdentityModel(
            system_id=system_id,
            name=name,
            is_active=is_active,
        )

        self.db.add(identity)
        self.db.flush()

        return identity

    def save(
        self,
        identity: SystemIdentityModel,
    ) -> SystemIdentityModel:

        self.db.add(identity)
        self.db.flush()

        return identity

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()