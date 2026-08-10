from __future__ import unicode_literals
import frappe

def execute():
    # Create roles
    roles = [
        'Logix Manager', 'Logix Branch Manager', 'Logix Dispatcher', 'Logix Operations User',
        'Logix Estimator', 'Logix Driver', 'Logix Finance User', 'Logix Storage User', 'Logix Read Only'
    ]
    for r in roles:
        if not frappe.db.exists('Role', r):
            frappe.get_doc({'doctype':'Role', 'role_name': r}).insert(ignore_permissions=True)

    # Add custom fields to Customer, Vehicle, Driver
    custom_fields = {
        'Customer': [
            {'fieldname':'logix_default_branch', 'label':'Logix Default Branch', 'fieldtype':'Link', 'options':'Branch'},
            {'fieldname':'logix_default_load_type', 'label':'Logix Default Load Type', 'fieldtype':'Link', 'options':'Logix Load Type'},
            {'fieldname':'logix_prefer_pod', 'label':'Logix POD Required', 'fieldtype':'Select', 'options':'Inherit Global\nPOD Required\nPOD Not Required'}
        ],
        'Vehicle': [
            {'fieldname':'logix_branch', 'label':'Logix Branch', 'fieldtype':'Link', 'options':'Branch'},
            {'fieldname':'logix_vehicle_type', 'label':'Logix Vehicle Type', 'fieldtype':'Link', 'options':'Logix Vehicle Type'}
        ]
    }

    for dt, fields in custom_fields.items():
        for f in fields:
            if not frappe.db.exists('Custom Field', {'dt': dt, 'fieldname': f['fieldname']}):
                cf = frappe.get_doc({
                    'doctype':'Custom Field',
                    'dt': dt,
                    'label': f['label'],
                    'fieldname': f['fieldname'],
                    'fieldtype': f['fieldtype'],
                    'insert_after': 'naming_series'
                })
                if 'options' in f:
                    cf.options = f['options']
                cf.insert(ignore_permissions=True)

    frappe.db.commit()
