import frappe
import unittest


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
        }).insert()

        # call the server-side controller helper to mark accepted
        est.run_method("mark_accepted")
        est = frappe.get_doc("Logix Estimation", est.name)
        self.assertEqual(est.status, "Accepted")
