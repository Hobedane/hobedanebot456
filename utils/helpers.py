import logging

logger = logging.getLogger(__name__)

def format_price(price: float, currency: str = 'EUR') -> str:
    """Format price with currency symbol"""
    if currency.upper() == 'EUR':
        return f"€{price:.2f}"
    elif currency.upper() == 'USD':
        return f"${price:.2f}"
    else:
        return f"{price:.2f} {currency}"

def validate_discount_code(code: str) -> bool:
    """Validate discount code format"""
    if not code or len(code) < 3:
        return False
    return code.isalnum()

def calculate_discounted_price(original_price: float, discount_percentage: float) -> float:
    """Calculate price after discount"""
    discount_amount = original_price * (discount_percentage / 100)
    return original_price - discount_amount

def format_product_description(description: str, max_length: int = 200) -> str:
    """Format product description with length limit"""
    if len(description) <= max_length:
        return description
    return description[:max_length-3] + "..."
