from rest_framework.throttling import UserRateThrottle

from app.throttling import ConfigurableThrottlingMixin


class NotionThrottle(ConfigurableThrottlingMixin, UserRateThrottle):
    """Throttle for any authorization views."""

    scope = "notion-materials"
