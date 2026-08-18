"""Compatibility import for callers moving to customer Contract Rates.

There is intentionally one pricing engine: ``contract_pricing``. New code should
import it directly.
"""

from logix.services.contract_pricing import (  # noqa: F401
	ContractPriceResult,
	calculate_contract_price,
	preview_contract_price,
	validate_contract_rate,
)
