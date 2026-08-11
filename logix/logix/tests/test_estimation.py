import frappe
import unittest
from frappe.utils import nowdate


class TestLogixEstimation(unittest.TestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        if not frappe.db.exists("Branch", "Logix Test Branch"):
            frappe.get_doc({"doctype": "Branch", "branch": "Logix Test Branch"}).insert()
        self.branch = "Logix Test Branch"
        # ensure a test Customer exists
        if not frappe.db.exists("Customer Group", {"is_group": 0}):
            # create a basic non-group Customer Group if none exist
            frappe.get_doc({"doctype": "Customer Group", "customer_group_name": "Test Customer Group", "is_group": 0}).insert()

        cg = frappe.get_all("Customer Group", filters={"is_group": 0}, limit_page_length=1)
        customer_group = cg[0].name if cg else "Test Customer Group"

        if not frappe.db.exists("Customer", "Test Customer"):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test Customer",
                "customer_type": "Individual",
                "customer_group": customer_group
            }).insert()

        self.from_city = self._master("Logix City", {"city_name": "Test Origin City"})
        self.to_city = self._master("Logix City", {"city_name": "Test Destination City"})
        self.vehicle_type = self._master("Logix Vehicle Type", {"vehicle_type_name": "Test Vehicle Type"})
        self.load_type = self._master("Logix Load Type", {"load_type_name": "Test Load Type"})

    def _master(self, doctype, values):
        name = frappe.db.get_value(doctype, values, "name")
        if not name:
            name = frappe.get_doc({"doctype": doctype, **values}).insert(ignore_permissions=True).name
        return name

    def estimation_values(self):
        return {
            "from_city": self.from_city,
            "to_city": self.to_city,
            "vehicle_type": self.vehicle_type,
            "load_type": self.load_type,
            "base_weight": "1000",
            "pricing_source": "Manual",
        }

    def tearDown(self):
        # cleanup any test estimations created
        for d in frappe.get_all("Logix Estimation", filters={"customer": "Test Customer"}):
            try:
                frappe.get_doc("Logix Estimation", d.name).delete()
            except Exception:
                pass
        # remove the test customer
        try:
            if frappe.db.exists("Customer", "Test Customer"):
                frappe.get_doc("Customer", "Test Customer").delete()
        except Exception:
            pass

    def test_profit_and_margin_computation(self):
        est = frappe.get_doc({
            "doctype": "Logix Estimation",
            "customer": "Test Customer",
            "status": "Draft",
            "branch": self.branch,
            "estimated_revenue": 2000.0,
            "estimated_direct_cost": 1500.0,
            **self.estimation_values(),
        }).insert()

        # explicitly run validate to ensure controller logic executed
        est.run_method("validate")
        # reload to ensure values persisted
        est = frappe.get_doc("Logix Estimation", est.name)
        self.assertAlmostEqual(float(est.estimated_profit), 500.0)
        self.assertAlmostEqual(float(est.estimated_margin_percent), 25.0)

    def test_mark_accepted(self):
        est = frappe.get_doc({
            "doctype": "Logix Estimation",
            "customer": "Test Customer",
            "status": "Draft",
            "branch": self.branch,
            **self.estimation_values(),
        }).insert()

        # call the server-side controller helper to mark accepted
        est.run_method("mark_accepted")
        est = frappe.get_doc("Logix Estimation", est.name)
        self.assertEqual(est.status, "Accepted")

    def test_rate_card_calculates_estimated_revenue(self):
        settings = frappe.get_single("Logix Settings")
        settings.rate_card_pricing_enabled = 1
        settings.manual_pricing_allowed = 1
        settings.save()
        currency = frappe.db.get_single_value("Global Defaults", "default_currency") or "SAR"
        filters = {
            "customer": "Test Customer",
            "from_city": self.from_city,
            "to_city": self.to_city,
            "vehicle_type": self.vehicle_type,
            "load_type": self.load_type,
        }
        rate_name = frappe.db.get_value("Logix Transport Rate Card", filters, "name")
        values = {
            **filters,
            "base_rate": 100,
            "included_weight": 1000,
            "excess_rate": 2,
            "cbm_pricing_enabled": 1,
            "cbm_rate": 10,
            "extra_stop_charge": 5,
            "minimum_freight": 0,
            "currency": currency,
            "effective_from": nowdate(),
            "disabled": 0,
        }
        if rate_name:
            rate = frappe.get_doc("Logix Transport Rate Card", rate_name)
            rate.update(values)
            rate.save(ignore_permissions=True)
        else:
            rate = frappe.get_doc({"doctype": "Logix Transport Rate Card", **values}).insert(ignore_permissions=True)

        estimation_values = self.estimation_values()
        estimation_values.update({"pricing_source": "Rate Card", "base_weight": 1100, "cbm": 2, "extra_stops": 1})
        est = frappe.get_doc({
            "doctype": "Logix Estimation",
            "customer": "Test Customer",
            "branch": self.branch,
            "status": "Draft",
            **estimation_values,
        }).insert()

        self.assertEqual(est.rate_card, rate.name)
        self.assertAlmostEqual(float(est.estimated_revenue), 325.0)
        self.assertAlmostEqual(float(est.estimated_profit), 325.0)
