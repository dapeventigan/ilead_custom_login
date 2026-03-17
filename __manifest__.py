{
    "name": "Custom Login - Dape",
    "version": "1.0.0",
    "author": "dape",
    "license": "LGPL-3",
    "summary": "iLead I.T Solution Custom Odoo Login Page",
    "depends": ["web", "auth_signup"],
    "data": [
            "views/login_template.xml", 
            "views/signup_template.xml", 
            "views/reset_password_template.xml", 
            "views/ilead_login.xml", 
            "views/ilead_users.xml", 
            "views/ilead_main_menu.xml", 
             ],
    "assets": {
        "web.assets_frontend": [
            "custom_login/static/src/**/*.css",
            "custom_login/static/src/**/*.js",
            "custom_login/static/src/**/*.xml",
        ],
        "web.assets_backend": [
            "custom_login/static/src/**/*.css",
            "custom_login/static/src/**/*.js",
            "custom_login/static/src/**/*.xml",
        ],
    },
    "installable": True,
    }