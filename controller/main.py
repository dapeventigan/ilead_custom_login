import logging
import werkzeug
import re
from werkzeug.urls import url_encode

from odoo import http,fields,_
from odoo.http import request
from odoo.addons.web.models.res_users import SKIP_CAPTCHA_LOGIN
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.tools.translate import LazyTranslate
from datetime import timedelta
from odoo.exceptions import UserError

_lt = LazyTranslate(__name__)
_logger = logging.getLogger(__name__)

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

        user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)

        try: 
            credentials = {
                'login': login,
                'password': password,
                'type': 'password'
            }

            uid = request.session.authenticate(request.env, credentials)

            if uid:
                request.env['res.users'].sudo().search([('login', '=', login)], limit=1).reset_failed_attempts()
                limit_date = fields.Date.today() - timedelta(days=90)
                
                if not user.ilead_password_last_updated or user.ilead_password_last_updated < limit_date:
                    user.sudo().write({'ilead_status': 'c_locked'})
                    request.session.logout()
                    return request.render('custom_login.custom_login_template', {
                        'error': 'Your password has expired (90-day limit). Please use "Forgot Password" to reset it.',
                        'force_password_reset': True,
                        'login': login,
                    })
                else:
                    if user.ilead_status == "c_locked" or user.ilead_failed_login_count >= 5:
                        if user.ilead_status != "c_locked":
                            user.sudo().write({'ilead_status': 'c_locked'})

                        return request.render('custom_login.custom_login_template', {
                            'error': 'Account locked. Too many failed attempts. Please click Forgot Password.'
                        })

                return request.redirect('/web')
        except Exception:
            if user:
                user.register_failed_attempt()
                attempts_left = 5 - user.ilead_failed_login_count
                error_msg = f"Wrong username or password. {max(0, attempts_left)} attempts remaining today."
            else:
                error_msg = "Wrong username or password."

            return request.render('custom_login.custom_login_template', {
                'error': error_msg
            })

class CustomSignupController(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            return request.render('web.errors', {'message': _("Signup is disabled.")})

        if request.httprequest.method == 'POST':
            password = qcontext.get('password')
            errors = []
            if len(password) < 8:
                errors.append("at least 8 characters")

            if not re.search(r"[A-Z]", password):
                errors.append("one uppercase letter")

            if not re.search(r"[a-z]", password):
                errors.append("one lowercase letter")

            if not re.search(r"[\d\W]", password):
                errors.append("one number or special character")

            if errors:
                missing_str = ", ".join(errors[:-1]) + (" and " if len(errors) > 1 else "") + errors[-1]
                error_msg = f"Password must include {missing_str}."
                
                return request.render('custom_login.custom_signup_template', {'error': error_msg,**qcontext})
            try:
                self.do_signup(qcontext)
                return request.redirect(qcontext.get('redirect') or '/web')
            except Exception as e:
                qcontext['error'] = str(e)

        return request.render('custom_login.custom_signup_template', qcontext)

    def _prepare_signup_values(self, qcontext):
        login = qcontext.get('login')

        existing_user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)

        if not existing_user:
            values = super()._prepare_signup_values(qcontext)

            values.update({
                'email': qcontext.get('email'),
            })
            
            internal_group = request.env.ref('base.group_portal')
            values['group_ids'] = [(6, 0, [internal_group.id])]
            
            return values
        else:
            values = { key: qcontext.get(key) for key in ('login', 'name', 'password') }
            if not values:
                raise UserError(_("The form was not properly filled in."))
            if values.get('password') != qcontext.get('confirm_password'):
                raise UserError(_("Passwords do not match; please retype them."))
            supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
            lang = request.env.context.get('lang', '')
            if lang in supported_lang_codes:
                values['lang'] = lang
            return values

class CustomResetPassword(http.Controller):
    @http.route('/password/renew', type='http', auth="public", methods=['GET', 'POST'], website=True)
    def password_renewal(self, **kw):
        values = {
            'login': kw.get('login', '') 
        }
        if request.httprequest.method == 'POST':
            login = kw.get('login')
            old_password = kw.get('old_password')
            new_password = kw.get('new_password')
            confirm_password = kw.get('confirm_password')

            if new_password != confirm_password:
                values['error'] = "New password do not match."
            else:
                errors = []
                if len(new_password) < 8:
                    errors.append("at least 8 characters")

                if not re.search(r"[A-Z]", new_password):
                    errors.append("one uppercase letter")

                if not re.search(r"[a-z]", new_password):
                    errors.append("one lowercase letter")

                if not re.search(r"[\d\W]", new_password):
                    errors.append("one number or special character")

                if errors:
                    missing_str = ", ".join(errors[:-1]) + (" and " if len(errors) > 1 else "") + errors[-1]
                    values['error'] = f"Password must include {missing_str}."
                    return request.render('custom_login.password_renew_template', values)
                try:
                    credentials = {
                        'login': login,
                        'password': old_password,
                        'type': 'password'
                    }

                    uid = request.session.authenticate(request.env, credentials)
                    if uid:
                        user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)

                        user.sudo().write({
                            'ilead_status': 'b_activated',
                            'password': new_password,
                            'ilead_password_last_updated': fields.Date.today()
                        })
                        return request.redirect('/web/login?message=password_updated')
                except Exception:
                    values['error'] = "Invalid username or old password."
        
        return request.render('custom_login.password_renew_template', values)


class CustomForgotPassword(AuthSignupHome):

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False, captcha='password_reset', list_as_website_content=_lt("Reset Password"))
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    retrieved_info = request.env['res.partner'].sudo()._signup_retrieve_info(qcontext.get('token'))
                    if retrieved_info:
                        user = request.env['res.users'].sudo().search([('login', '=', retrieved_info.get('login'))], limit=1)
                        if user:
                            user.sudo().reset_failed_attempts()
                            self.do_signup(qcontext, do_login=False)
                            request.update_context(skip_captcha_login=SKIP_CAPTCHA_LOGIN)
                            qcontext['message'] = _("Your password has been reset successfully.")
                        else:
                            qcontext['message'] = _("Account doesn't exist. Please contact your administrator.")
                else:
                    login = qcontext.get('login')
                    email = qcontext.get('email')
                    assert login, _("No login provided.")
                    assert email, _("No email provided.")

                    user = request.env['res.users'].sudo().search([
                        ('login', '=', login),
                        ('email', '=', email),
                        ('state', '!=', 'new')
                    ], limit=1)

                    if user:
                        user.sudo().action_reset_password()
                        
                        qcontext['message'] = _("Password reset instructions sent to your email.")
                    else:
                        qcontext['error'] = _("Invalid Username or Email address.")

            except UserError as e:
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search([('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        response = request.render('custom_login.ilead_custom_reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

class CustomLogoutController(http.Controller):

    @http.route('/get_idle_time/timer', auth='public', type='jsonrpc')
    def get_idle_time(self):
        if request.env.user.ilead_enable_idle:
            return request.env.user.ilead_idle_time