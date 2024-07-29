"""Define enumeration constants for OpenAPI tags."""

from enum import StrEnum


class OpenAPITags(StrEnum):
    """Define enumeration constants for OpenAPI tags."""

    USERS = "Users"
    PROPERTIES = "Properties"
    BOOKINGS = "Bookings"
    PAYMENTS = "Payments"
    SEARCH = "Search"
    NOTIFICATIONS = "Notifications"
    REVIEWS = "Reviews"
    HEALTH_CHECK = "Health Check"
