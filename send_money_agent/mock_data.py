"""
Mock country data for Send Money Agent

In production, this would be replaced with API calls to:
- Exchange rate service
- Payment method availability service
- Country configuration database
"""

SUPPORTED_COUNTRIES = [
    {
        "country_name": "Brazil",
        "currency_code": "BRL",
        "exchange_rate": 5.36,  # USD to BRL rate (mock)
        "delivery_methods": ["Pix", "Bank Transfer"]
    },
    {
        "country_name": "Mexico",
        "currency_code": "MXN",
        "exchange_rate": 17.15,  # USD to MXN rate (mock)
        "delivery_methods": ["SPEI", "Cash Pickup", "Bank Transfer"]
    },
    {
        "country_name": "Argentina",
        "currency_code": "ARS",
        "exchange_rate": 1055.50,  # USD to ARS rate (mock)
        "delivery_methods": ["Bank Transfer", "Cash Pickup"]
    }
]


def get_supported_country_names() -> list:
    """Get list of supported country names"""
    return [country['country_name'] for country in SUPPORTED_COUNTRIES]


def get_available_methods(country: str) -> list:
    """Get available delivery methods for a country"""
    country_lower = country.lower()
    for country_config in SUPPORTED_COUNTRIES:
        if country_config['country_name'].lower() == country_lower:
            return country_config['delivery_methods']
    return []
