class TierEntitlementError(Exception):
    """Base exception for Brain tier entitlement restrictions."""

    def __init__(
        self,
        code: str,
        message: str,
        required_tier: str | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.required_tier = required_tier