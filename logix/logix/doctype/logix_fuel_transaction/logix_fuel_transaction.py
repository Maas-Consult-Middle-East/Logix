import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_datetime


class LogixFuelTransaction(Document):
	def validate(self):
		self._validate_trip_resources()
		self._set_company_and_currency()
		self._calculate_consumption()

	def on_submit(self):
		last_odometer = flt(frappe.db.get_value("Vehicle", self.vehicle, "last_odometer"))
		if flt(self.odometer) > last_odometer:
			frappe.db.set_value("Vehicle", self.vehicle, "last_odometer", self.odometer)

	def before_cancel(self):
		if self.purchase_invoice and frappe.db.get_value("Purchase Invoice", self.purchase_invoice, "docstatus") != 2:
			frappe.throw(_("Cancel Purchase Invoice {0} before cancelling this Fuel Transaction.").format(self.purchase_invoice))

		vehicle_odometer = flt(frappe.db.get_value("Vehicle", self.vehicle, "last_odometer"))
		if vehicle_odometer == flt(self.odometer):
			frappe.db.set_value("Vehicle", self.vehicle, "last_odometer", self.previous_odometer)

	def _validate_trip_resources(self):
		trip = frappe.db.get_value(
			"Logix Trip", self.trip, ["branch", "vehicle", "driver", "docstatus", "status"], as_dict=True
		)
		if not trip or trip.docstatus == 2 or trip.status == "Cancelled":
			frappe.throw(_("Fuel Transaction requires an active Trip."))
		if not trip.vehicle or not trip.driver:
			frappe.throw(_("Assign a Vehicle and Driver to Trip {0} before recording fuel.").format(self.trip))
		if self.vehicle != trip.vehicle:
			frappe.throw(_("Vehicle must match the Vehicle assigned to Trip {0}.").format(self.trip))
		if self.driver != trip.driver:
			frappe.throw(_("Driver must match the Driver assigned to Trip {0}.").format(self.trip))
		self.branch = trip.branch

	def _set_company_and_currency(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")
		if not self.company:
			frappe.throw(_("Select a Company for the Fuel Transaction."))
		company_currency = frappe.db.get_value("Company", self.company, "default_currency")
		if not self.currency:
			self.currency = company_currency
		if self.currency != company_currency:
			frappe.throw(_("Fuel Transaction currency must match the Company currency {0}.").format(company_currency))

	def _calculate_consumption(self):
		if flt(self.odometer) <= 0:
			frappe.throw(_("Current Odometer must be greater than zero."))
		if flt(self.fuel_quantity) <= 0:
			frappe.throw(_("Fuel Quantity must be greater than zero."))
		if flt(self.rate) <= 0:
			frappe.throw(_("Rate per Litre must be greater than zero."))

		previous = self._get_previous_odometer()
		if previous and flt(self.odometer) < previous:
			frappe.throw(
				_("Current Odometer cannot be below the previous reading of {0} km.").format(previous)
			)

		self.previous_odometer = previous
		self.distance_travelled = flt(self.odometer) - previous if previous else 0
		self.total_cost = flt(self.fuel_quantity) * flt(self.rate)
		self.actual_efficiency = (
			flt(self.distance_travelled) / flt(self.fuel_quantity) if self.distance_travelled else 0
		)
		self.expected_efficiency = flt(
			frappe.db.get_value("Vehicle", self.vehicle, "logix_expected_fuel_efficiency_kmpl")
			or frappe.db.get_single_value("Logix Settings", "default_fuel_efficiency_kmpl")
		)
		self.efficiency_variance_percent = 0
		self.is_abnormal = 0
		if self.actual_efficiency and self.expected_efficiency:
			self.efficiency_variance_percent = (
				(self.expected_efficiency - self.actual_efficiency) / self.expected_efficiency * 100
			)
			threshold = flt(
				frappe.db.get_single_value("Logix Settings", "abnormal_fuel_variance_percent") or 20
			)
			self.is_abnormal = self.efficiency_variance_percent > threshold

	def _get_previous_odometer(self):
		posting_datetime = get_datetime(f"{self.posting_date} {self.posting_time}")
		previous = frappe.db.sql(
			"""
			select odometer
			from `tabLogix Fuel Transaction`
			where vehicle = %(vehicle)s
			  and docstatus = 1
			  and name != %(name)s
			  and timestamp(posting_date, posting_time) <= %(posting_datetime)s
			order by posting_date desc, posting_time desc, creation desc
			limit 1
			""",
			{"vehicle": self.vehicle, "name": self.name or "", "posting_datetime": posting_datetime},
		)
		if previous:
			return flt(previous[0][0])
		return flt(frappe.db.get_value("Vehicle", self.vehicle, "last_odometer"))
