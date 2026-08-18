import unittest

import frappe
from frappe.exceptions import ValidationError
from frappe.utils import add_days, nowdate


class TestLogixEstimation(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.company = frappe.db.get_single_value("Global Defaults", "default_company")
		self.currency = frappe.db.get_single_value("Global Defaults", "default_currency") or "SAR"
		self.branch = self._master("Branch", {"branch":"Commercial Test Branch"})
		self.customer_a = self._customer("Contract Customer A")
		self.customer_b = self._customer("Contract Customer B")
		self.origin = self._master("Logix City", {"city_name":"Contract Riyadh"})
		self.destination = self._master("Logix City", {"city_name":"Contract Dammam"})
		self.other_city = self._master("Logix City", {"city_name":"Contract Jeddah"})
		self.vehicle = self._master("Logix Vehicle Type", {"vehicle_type_name":"Contract 10 Ton"})
		self.load = self._master("Logix Load Type", {"load_type_name":"Contract General"})
		self.uom = self._master("UOM", {"uom_name":"Ton"})
		settings = frappe.get_single("Logix Settings")
		settings.manual_pricing_allowed = 1
		settings.estimation_cost_visibility = 1
		settings.save(ignore_permissions=True)
		self.contract = self._contract(self.customer_a)

	def tearDown(self):
		frappe.db.rollback()

	def _master(self, doctype, values):
		name = frappe.db.get_value(doctype, values, "name")
		return name or frappe.get_doc({"doctype":doctype, **values}).insert(ignore_permissions=True).name

	def _customer(self, name):
		if frappe.db.exists("Customer", name): return name
		group = frappe.db.get_value("Customer Group", {"is_group":0}, "name")
		return frappe.get_doc({"doctype":"Customer","customer_name":name,"customer_type":"Company","customer_group":group}).insert(ignore_permissions=True).name

	def _contract(self, customer, currency=None, from_date=None, to_date=None):
		doc = frappe.get_doc({"doctype":"Logix Contract Rate","contract_rate_name":f"{customer} 2026","customer":customer,"currency":currency or self.currency,"applicable_from":from_date or add_days(nowdate(), -1),"applicable_to":to_date or add_days(nowdate(), 365),"contract_services":[
			{"bill_by":"Route","from_city":self.origin,"to_city":self.destination,"vehicle_type":self.vehicle,"load_type":self.load,"route_rate":2200},
			{"bill_by":"Weight","vehicle_type":self.vehicle,"load_type":self.load,"rate_per_weight":120,"weight_uom":self.uom},
			{"bill_by":"CBM","vehicle_type":self.vehicle,"load_type":self.load,"rate_per_cbm":75},
		]})
		return doc.insert(ignore_permissions=True)

	def _estimation(self, items, contract=None, customer=None, currency=None, **values):
		return frappe.get_doc({"doctype":"Logix Estimation","customer":customer or self.customer_a,"company":self.company,"branch":self.branch,"estimation_date":nowdate(),"valid_until":add_days(nowdate(), 30),"currency":currency or self.currency,"contract_rate":contract.name if contract else None,"status":"Draft","items":items, **values})

	def test_exact_four_tab_layout(self):
		tabs = [field.label for field in frappe.get_meta("Logix Estimation").fields if field.fieldtype == "Tab Break"]
		self.assertEqual(tabs, ["Commercial", "Costing & Profitability", "References / Additional Information", "Connections"])

	def test_customer_currency_and_validity_are_server_enforced(self):
		item = {"bill_by":"Route","from_city":self.origin,"to_city":self.destination,"vehicle_type":self.vehicle,"load_type":self.load}
		with self.assertRaises(ValidationError): self._estimation([item], self.contract, customer=self.customer_b).insert()
		with self.assertRaises(ValidationError): self._estimation([item], self.contract, currency="USD").insert()
		with self.assertRaises(ValidationError): self._estimation([item], self.contract, valid_until=add_days(nowdate(), -1)).insert()
		expired = self._contract(self.customer_a, from_date=add_days(nowdate(), -10), to_date=add_days(nowdate(), -1))
		with self.assertRaises(ValidationError): self._estimation([item], expired).insert()

	def test_route_weight_cbm_and_manual_pricing(self):
		est = self._estimation([
			{"bill_by":"Route","from_city":self.origin,"to_city":self.destination,"vehicle_type":self.vehicle,"load_type":self.load},
			{"bill_by":"Weight","vehicle_type":self.vehicle,"load_type":self.load,"weight":8,"weight_uom":self.uom},
			{"bill_by":"CBM","vehicle_type":self.vehicle,"load_type":self.load,"cbm":20},
			{"bill_by":"Manual","description":"Special cargo handling","qty":1,"rate":500},
		], self.contract).insert()
		self.assertEqual([row.amount for row in est.items], [2200, 960, 1500, 500])
		self.assertEqual([row.pricing_source for row in est.items], ["Contract Rate", "Contract Rate", "Contract Rate", "Manual"])
		self.assertEqual(est.net_total, 5160)
		bad_route = {"bill_by":"Route","from_city":self.origin,"to_city":self.other_city,"vehicle_type":self.vehicle,"load_type":self.load}
		with self.assertRaises(ValidationError): self._estimation([bad_route], self.contract).insert()

	def test_tax_discount_and_profit_exclude_tax(self):
		est = self._estimation([{"bill_by":"Manual","description":"Service","qty":1,"rate":10000}], additional_discount_percentage=10, apply_discount_on="Net Total", taxes=[{"charge_type":"On Net Total","description":"VAT 15%","rate":15}], estimated_direct_cost=6000).insert()
		self.assertEqual(est.additional_discount_amount, 1000)
		self.assertEqual(est.total_taxes_and_charges, 1350)
		self.assertEqual(est.grand_total, 10350)
		self.assertEqual(est.estimated_selling_value_excluding_tax, 9000)
		self.assertEqual(est.estimated_profit, 3000)
		self.assertAlmostEqual(est.estimated_margin_percent, 33.333333, places=4)

	def test_authorized_rate_override_is_audited(self):
		est = self._estimation([{"bill_by":"Route","from_city":self.origin,"to_city":self.destination,"vehicle_type":self.vehicle,"load_type":self.load,"rate":2000,"manual_rate_override":1,"override_reason":"Negotiated exception"}], self.contract).insert()
		row = est.items[0]
		self.assertEqual(row.pricing_source, "Override")
		self.assertEqual(row.suggested_rate, 2200)
		self.assertEqual(row.amount, 2000)
		self.assertEqual(row.override_user, "Administrator")

	def test_manual_and_override_permissions_are_enforced(self):
		settings = frappe.get_single("Logix Settings")
		settings.manual_pricing_allowed = 0
		settings.save(ignore_permissions=True)
		with self.assertRaises(ValidationError):
			self._estimation([{"bill_by":"Manual","description":"Unauthorized manual","qty":1,"rate":500}]).insert()
		settings.manual_pricing_allowed = 1
		settings.save(ignore_permissions=True)
		user = "commercial-estimator@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc({"doctype":"User","email":user,"first_name":"Commercial Estimator","send_welcome_email":0,"roles":[{"role":"Logix Estimator"}]}).insert(ignore_permissions=True)
		frappe.set_user(user)
		with self.assertRaises(ValidationError):
			self._estimation([{"bill_by":"Route","from_city":self.origin,"to_city":self.destination,"vehicle_type":self.vehicle,"load_type":self.load,"rate":2000,"manual_rate_override":1,"override_reason":"Not authorized"}], self.contract).insert(ignore_permissions=True)

	def test_grand_total_discount(self):
		est = self._estimation([{"bill_by":"Manual","description":"Service","qty":1,"rate":10000}], apply_discount_on="Grand Total", additional_discount_percentage=10, taxes=[{"charge_type":"On Net Total","description":"VAT","rate":15}]).insert()
		self.assertEqual(est.total_taxes_and_charges, 1500)
		self.assertEqual(est.additional_discount_amount, 1150)
		self.assertEqual(est.grand_total, 10350)
		self.assertEqual(est.estimated_selling_value_excluding_tax, 9000)

	def test_discount_amount_updates_equivalent_percentage(self):
		est = self._estimation([{"bill_by":"Manual","description":"Service","qty":1,"rate":10000}], additional_discount_amount=1000).insert()
		self.assertEqual(est.additional_discount_percentage, 10)
		est.additional_discount_amount = 500
		est.save()
		self.assertEqual(est.additional_discount_percentage, 5)
		self.assertEqual(est.grand_total, 9500)
