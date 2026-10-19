from enum import Enum


class NotificationType(str, Enum):
    SYSTEM = "system"
    PRODUCT_UPDATE = "product_update"
    CAPABILITY_UPDATE = "capability_update"
    SECURITY = "security"
    WORKSPACE = "workspace"