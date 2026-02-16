from odoo import http
from odoo.http import request

class CustomLoginController(http.Controller):
    @http.route('/web/login', type='http', auth="public", website=True)
    def custom_login(self, **kwargs):
        if request.session.uid:
            return request.redirect('/web')
        return request.render('custom_login.custom_login_template')

    @http.route('/custom/ilead_login', type='http', auth="public", methods=['POST'], csrf=False, website=True)
    def custom_do_login(self, **kwargs):
        login = kwargs.get('login')
        password = kwargs.get('password')
        email = kwargs.get('email')

        try: 

            credentials = {
                'login': login,
                'password': password,
                'type': 'password'
            }

            uid = request.session.authenticate(request.env, credentials)

            # uid = request.session.authenticate(request.db, login, password)
            if uid:
                return request.redirect('/web')
        except Exception:
            pass
        return request.render('custom_login.custom_login_template', {
            'error': 'Wrong username or password'
        })