from dataclasses import dataclass

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate


@dataclass(frozen=True)
class PriceResult:
	rate_card: str
	amount: float
	currency: str | None


def find_rate_card(customer, from_city, to_city, vehicle_type=None, load_type=None, posting_date=None):
	posting_date = getdate(posting_date or nowdate())
	base_filters = {"from_city": from_city, "to_city": to_city}
	if vehicle_type:
		base_filters["vehicle_type"] = vehicle_type
	if load_type:
		base_filters["load_type"] = load_type

	for rate_customer in (customer, ""):
		filters = dict(base_filters, customer=rate_customer)
		cards = frappe.get_all(
			"Logix Transport Rate Card",
			filters=filters,
			fields=["*"],
			order_by="effective_from desc, modified desc",
		)
		for card in cards:
			if (not card.effective_from or getdate(card.effective_from) <= posting_date) and (
				not card.effective_to or getdate(card.effective_to) >= posting_date
			):
				return card
	frappe.throw(_("No applicable transport rate card was found."))


def calculate_transport_price(
	customer, from_city, to_city, vehicle_type=None, load_type=None, weight=0,
	cbm=0, extra_stops=0, trip_pricing="One Way", posting_date=None,
):
	card = find_rate_card(customer, from_city, to_city, vehicle_type, load_type, posting_date)
	amount = flt(card.base_rate)
	excess = max(flt(weight) - flt(card.included_weight), 0)
	amount += excess * flt(card.excess_rate)
	if card.cbm_pricing_enabled:
		amount += flt(cbm) * flt(card.cbm_rate)
	amount += max(int(extra_stops or 0), 0) * flt(card.extra_stop_charge)
	if trip_pricing == "Round Trip":
		amount = flt(card.round_trip_rate) or amount * 2
	elif trip_pricing == "Return Trip":
		amount = flt(card.return_trip_rate) or amount
	return PriceResult(card.name, max(amount, flt(card.minimum_freight)), card.currency)
