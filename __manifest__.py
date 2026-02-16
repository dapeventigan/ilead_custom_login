{
    "name": "Custom Login - Dape",
    "version": "1.0.0",
    "author": "dape",
    "license": "LGPL-3",
    "summary": "iLead I.T Solution Custom Odoo Login Page",
    "depends": ["web"],
    "data": [
            "views/login_template.xml", 
            "views/signup_template.xml", 
             ],
    "assets": {
        "web.assets_frontend": [
            "custom_login/static/src/**/*.css",
        ],
    },
    "installable": True,
    }