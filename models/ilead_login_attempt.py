from odoo import models, fields, api
from datetime import date

class ilead_login_attempt(models.Model):
    _name = 'res.users'
    _inherit = ['res.users', 'mail.thread', 'mail.activity.mixin']

    ilead_failed_login_count = fields.Integer(string='Failed Login Count',default=0)
    ilead_last_failed_date = fields.Date(string='Last Failed Date')
    ilead_password_last_updated = fields.Date(string="Password Last Updated", default=fields.Date.today())
    ilead_enable_idle = fields.Boolean(string="Enable Idle Time")
    ilead_idle_time = fields.Integer(string="Idle Time", default=10)
    ilead_status = fields.Selection([
        ('a_new', 'New'),
        ('b_activated', 'Activated'),
    ], string='Account Status', default="a_new")

    _ilead_positive_idle_time = models.Constraint(
        'CHECK(ilead_idle_time >= 1)',
        "Idle Time should not be zero.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ilead_login_attempt, self).create(vals_list)
        users.notify_admin_users()
        
        return users

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
            users.group_ids = [(3, 10, 0)]
            users.group_ids = [(4, 1, 0)]
            users.ilead_status = 'b_activated'

            activities = self.env['mail.activity'].search([
                ('res_id', '=', users.id),
                ('res_model', '=', 'res.users')
            ])
            
            if activities:
                activities.sudo().unlink()

    def notify_admin_users(self):
        todo_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        activity_type_id = todo_type.id if todo_type else 1 
        admin_group = self.env.ref('base.group_system')
        admins = self.env['res.users'].sudo().search([('group_ids', 'in', admin_group.id)])
        model_id = self.env['ir.model']._get_id('res.users')

        for record in self:
            if record.ilead_status == 'a_new':
                for target_admin in admins:
                    self.env['mail.activity'].sudo().create({
                        'res_id': record.id,
                        'res_model_id': model_id,
                        'res_model': 'res.users',
                        'activity_type_id': activity_type_id,
                        'summary': f"Approval Required: {record.name}",
                        'note': f"User {record.name} ({record.login}) is waiting for login approval.",
                        'date_deadline': fields.Date.today(),
                        'user_id': target_admin.id, 
                    })