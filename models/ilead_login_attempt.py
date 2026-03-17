from odoo import models, fields, api
from datetime import date

class ilead_login_attempt(models.Model):
    _inherit = 'res.users'

    ilead_failed_login_count = fields.Integer(string='Failed Login Count',default=0)
    ilead_last_failed_date = fields.Date(string='Last Failed Date')
    ilead_password_last_updated = fields.Date(string="Password Last Updated", default=fields.Date.today())
    ilead_enable_idle = fields.Boolean(string="Enable Idle Time")
    ilead_idle_time = fields.Integer(string="Idle Time", default=10)
    _ilead_positive_idle_time = models.Constraint(
        'CHECK(ilead_idle_time >= 1)',
        "Idle Time should not be zero.",
    )


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

    def activate_user(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env["res.users"].browse(selected_ids)

        for users in selected_records:
            users.group_ids = [(6, 0, [1])]