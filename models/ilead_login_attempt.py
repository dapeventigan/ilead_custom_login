from odoo import models, fields, api
from datetime import date

class ilead_login_attempt(models.Model):
    _inherit = 'res.users'

    ilead_failed_login_count = fields.Integer(default=0)
    ilead_last_failed_date = fields.Date()
    ilead_password_last_updated = fields.Date(string="Password Last Updated", default=fields.Date.today())


    def register_failed_attempt(self):
        today = date.today()
        for user in self:
            if user.ilead_last_failed_date == today:
                user.ilead_failed_login_count += 1
            else:
                user.ilead_last_failed_date = today
                user.ilead_failed_login_count = 1

    def reset_failed_attempts(self):
        self.write({'ilead_failed_login_count': 0, 'ilead_last_failed_date': False})

    def write(self, vals):
            if 'password' in vals:
                vals['ilead_password_last_updated'] = fields.Date.today()
            return super(ilead_login_attempt, self).write(vals)