from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

class CustomLoginController(Home):

    @http.route('/web/login', type='http', auth="public", website=True, sitemap=False)
    def web_login(self, redirect=None, **kw):
        ensure_db()
        if request.session.uid:
            return request.redirect(self._login_redirect(request.session.uid, redirect=redirect))
        
        return request.render('custom_login.custom_login_template', {
            'redirect': redirect,
            'error': kw.get('error'),
        })

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

            if uid:
                return request.redirect('/web')
        except Exception:
            pass
        return request.render('custom_login.custom_login_template', {
            'error': 'Wrong username or password'
        })

class CustomSignupController(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            return request.render('web.errors', {'message': _("Signup is disabled.")})

        if request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                return request.redirect(qcontext.get('redirect') or '/web')
            except Exception as e:
                qcontext['error'] = str(e)

        return request.render('custom_login.custom_signup_template', qcontext)

    def _prepare_signup_values(self, qcontext):
        values = super()._prepare_signup_values(qcontext)

        values.update({
            'email': qcontext.get('email'),
        })
        
        internal_group = request.env.ref('base.group_user')
        values['group_ids'] = [(6, 0, [internal_group.id])]
        
        return values