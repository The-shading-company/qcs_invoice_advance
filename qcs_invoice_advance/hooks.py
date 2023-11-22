from . import __version__ as app_version

app_name = "qcs_invoice_advance"
app_title = "QCS Invoice Advance"
app_publisher = "Quark Cyber Systems FZC"
app_description = "QCS Invoice Advance"
app_email = "support@quarkcs.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/qcs_invoice_advance/css/qcs_invoice_advance.css"
# app_include_js = "/assets/qcs_invoice_advance/js/qcs_invoice_advance.js"

# include js, css files in header of web template
# web_include_css = "/assets/qcs_invoice_advance/css/qcs_invoice_advance.css"
# web_include_js = "/assets/qcs_invoice_advance/js/qcs_invoice_advance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "qcs_invoice_advance/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Sales Order": "public/js/sales_order.js",
              "Sales Invoice": "public/js/sales_invoice.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "qcs_invoice_advance.utils.jinja_methods",
#	"filters": "qcs_invoice_advance.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "qcs_invoice_advance.install.before_install"
# after_install = "qcs_invoice_advance.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "qcs_invoice_advance.uninstall.before_uninstall"
# after_uninstall = "qcs_invoice_advance.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "qcs_invoice_advance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Purchase Order": "qcs_invoice_advance.controller.qcs_purchase_order.CustomPurchaseOrder",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Item": {
		"after_insert": "qcs_invoice_advance.controller.item.create_bom",
        "validate": "qcs_invoice_advance.controller.item.update_bom",
        "on_trash": "qcs_invoice_advance.controller.item.delete_bom",
	}
}



fixtures = [
    {
        "dt": "Custom Field", "filters": [
            [
                "name", "in", [
                    'Sales Invoice-original_total',
                    'Sales Invoice Item-original_qty',
                    'Sales Order-partial_invoice',
                    'Sales Invoice-original_total',
                    'Sales Invoice-order_percentage',
                    'Sales Invoice Item-custom_ref_no',
                    'Sales Order Item-custom_ref_no'           
                ]
            ]
        ]
    },
    
]

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"qcs_invoice_advance.tasks.all"
#	],
#	"daily": [
#		"qcs_invoice_advance.tasks.daily"
#	],
#	"hourly": [
#		"qcs_invoice_advance.tasks.hourly"
#	],
#	"weekly": [
#		"qcs_invoice_advance.tasks.weekly"
#	],
#	"monthly": [
#		"qcs_invoice_advance.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "qcs_invoice_advance.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "qcs_invoice_advance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "qcs_invoice_advance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["qcs_invoice_advance.utils.before_request"]
# after_request = ["qcs_invoice_advance.utils.after_request"]

# Job Events
# ----------
# before_job = ["qcs_invoice_advance.utils.before_job"]
# after_job = ["qcs_invoice_advance.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"qcs_invoice_advance.auth.validate"
# ]
