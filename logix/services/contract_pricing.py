from __future__ import annotations

from dataclasses import asdict, dataclass, field

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate


@dataclass(frozen=True)
class ContractPriceResult:
	matched_contract_service: str
	rate: float
	quantity: float
	base_amount: float
	additional_amount: float
	final_amount: float
	pricing_source: str = "Contract Rate"
	warnings: list[str] = field(default_factory=list)

	def as_dict(self):
		return asdict(self)


def validate_contract_rate(contract_rate, customer, currency, estimation_date=None):
	"""Return an eligible customer Contract Rate or raise a precise validation error."""
	if not contract_rate:
		frappe.throw(_("Select a Contract Rate before pricing contract-derived items."))
	contract = frappe.get_doc("Logix Contract Rate", contract_rate)
	date = getdate(estimation_date or nowdate())
	if contract.disabled or contract.requires_review:
		frappe.throw(_("Contract Rate {0} is disabled or awaiting review.").format(contract.name))
	if contract.customer != customer:
		frappe.throw(_("Contract Rate {0} does not belong to Customer {1}.").format(contract.name, customer))
	if contract.currency != currency:
		frappe.throw(_("Contract Rate currency {0} does not match Estimation currency {1}.").format(contract.currency, currency))
	if getdate(contract.applicable_from) > date or getdate(contract.applicable_to) < date:
		frappe.throw(_("Contract Rate {0} is not valid on {1}.").format(contract.name, date))
	return contract


def _matches_dimension(service_value, requested_value):
	return not service_value or service_value == requested_value


def _find_service(contract, bill_by, from_city=None, to_city=None, vehicle_type=None, load_type=None):
	candidates = []
	for row in contract.contract_services:
		if row.bill_by != bill_by:
			continue
		if not all(
			_matches_dimension(row.get(fieldname), value)
			for fieldname, value in (
				("from_city", from_city), ("to_city", to_city),
				("vehicle_type", vehicle_type), ("load_type", load_type),
			)
		):
			continue
		# Prefer the rule with the greatest number of explicit matching dimensions.
		score = sum(bool(row.get(fieldname)) for fieldname in ("from_city", "to_city", "vehicle_type", "load_type"))
		candidates.append((score, row.idx, row))
	if not candidates:
		frappe.throw(_("No matching {0} Contract Service was found in Contract Rate {1}.").format(bill_by, contract.name))
	return sorted(candidates, key=lambda value: (-value[0], value[1]))[0][2]


def calculate_contract_price(
	*, customer, contract_rate, estimation_date, currency, bill_by,
	from_city=None, to_city=None, vehicle_type=None, load_type=None,
	weight=0, weight_uom=None, cbm=0, number_of_stops=0,
):
	contract = validate_contract_rate(contract_rate, customer, currency, estimation_date)
	if bill_by not in {"Route", "Weight", "CBM"}:
		frappe.throw(_("Contract pricing supports Route, Weight, or CBM billing."))
	if bill_by == "Route" and (not from_city or not to_city):
		frappe.throw(_("Route pricing requires From and To."))
	service = _find_service(contract, bill_by, from_city, to_city, vehicle_type, load_type)
	additional = 0.0
	if bill_by == "Route":
		rate = flt(service.route_rate)
		quantity = 1.0
		base_amount = rate
		if flt(service.extra_stop_rate):
			additional = max(int(number_of_stops or 0), 0) * flt(service.extra_stop_rate)
	elif bill_by == "Weight":
		if not weight_uom or weight_uom != service.weight_uom:
			frappe.throw(_("Weight UOM must match Contract Service UOM {0}; automatic conversion is not enabled.").format(service.weight_uom))
		quantity = flt(weight)
		if quantity <= 0:
			frappe.throw(_("Weight must be greater than zero."))
		rate = flt(service.rate_per_weight)
		base_amount = quantity * rate
	else:
		quantity = flt(cbm)
		if quantity <= 0:
			frappe.throw(_("CBM must be greater than zero."))
		rate = flt(service.rate_per_cbm)
		base_amount = quantity * rate
	final_amount = max(base_amount + additional, flt(service.minimum_charge))
	return ContractPriceResult(
		matched_contract_service=service.name,
		rate=rate,
		quantity=quantity,
		base_amount=base_amount,
		additional_amount=additional,
		final_amount=final_amount,
	)


@frappe.whitelist()
def preview_contract_price(**kwargs):
	return calculate_contract_price(**kwargs).as_dict()

