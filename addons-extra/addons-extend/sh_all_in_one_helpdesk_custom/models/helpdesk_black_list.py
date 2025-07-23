# Copyright 2014 ABF OSIELL <http://osiell.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ShHelpdeskTicketBlackLists(models.Model):
    _name = "sh.helpdesk.ticket.black.lists"

    name = fields.Char(string='Palabras restringidas', required=True)
    comment = fields.Text(string="Comment", tracking=True, translate=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
