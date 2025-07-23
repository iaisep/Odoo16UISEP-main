from secrets import choice

from odoo import fields, models


class Channel(models.Model):
    _inherit = "mail.channel"

    is_lockmeet = fields.Boolean(string="Lock Meet")
    is_lockpassword = fields.Boolean(string="Lock Password", default=True)
    is_EndMeet = fields.Boolean(string="End Meet", default=True)
    is_password = fields.Char(string="Password")
    users_id = fields.Integer(string="User Id")
    sheet_id = fields.Integer(string="Sheet Id")
    calendar_id = fields.Integer(string="Calendar Id")

    def _update_lockmeet(self, values):
        valid_values = {'is_lockmeet'}
        self.write({key: values[key]
                   for key in valid_values if key in valid_values})

    def _update_lockpassword(self, values):
        valid_values = {'is_lockpassword'}
        self.write({key: values[key]
                   for key in valid_values if key in valid_values})

    def _add_userid(self, values):
        valid_values = {'users_id'}
        self.write({key: values[key]
                   for key in valid_values if key in valid_values})

    def _add_sheetid(self, values):
        self.write({'sheet_id': values})

    def _create_password(self):
        is_password = ''.join(
            choice('abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ23456789')
            for _i in range(10))
        self.write({'is_password': is_password})
