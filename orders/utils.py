from .models import Order
from users.models import ServiceType

# Simple pricing logic per service type; you can adjust as needed
BASE_PRICES = {
    ServiceType.PLUMBER: 120_000,
    ServiceType.ELECTRICIAN: 150_000,
    ServiceType.CLEANER: 80_000,
}


def compute_price(service_type: str, description: str | None = None) -> int:
    """
    Compute service price based on service_type and optionally description.
    Current logic: fixed base price per service. Adds a tiny premium for long descriptions.
    """
    base = BASE_PRICES.get(service_type, 100_000)
    premium = 0
    if description:
        # add 1k per 50 chars as a trivial complexity premium, capped
        premium = min((len(description) // 50) * 1_000, 20_000)
    return base + premium
