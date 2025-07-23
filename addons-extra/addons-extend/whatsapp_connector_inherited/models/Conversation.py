from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)


class AcruxChatConversation(models.Model):
    _inherit = 'acrux.chat.conversation'
    _description = 'Chat Conversation Inherit Isep'

    # team_id = fields.Many2one('hr.department', string='Team', domain="[]",
    #                           default=lambda self: self.env['hr.department'].search([('is_coordinator', '=', 'True')],
    #                                                                                 limit=1).id,
    #                           readonly=False)

    new_team_id = fields.Many2one('hr.department', string='Team', domain="[]",
                               default=lambda self: self.env['hr.department'].search([('is_coordinator', '=', 'True')],limit=1).id,
                               readonly=False)
    agent_id = fields.Many2one('res.users', 'Agent', ondelete='set null',
                               domain="[('company_id', 'in', [company_id, False]), ('is_chatroom_group','=',True)]")

    def write(self, vals):
        res = super(AcruxChatConversation, self).write(vals)
        if (not self.env.user.has_group('whatsapp_connector_inherited.group_chat_coordinator') and
                (vals.get('agent_id') and vals.get('agent_id') != self.env.user.id or vals.get('new_team_id'))):
            raise UserError(_("El Usuario actual " + str(self.env.user.name) + " no pertenece al grupo Coordinadores Chatroom pongase en contacto con su administrador."))
        return res

    @api.model
    def search_active_conversation(self):
        ''' Override domain in search messages to splite by deparments'''

        coordinator = self.env.user.sudo().employee_ids.filtered(lambda employee: employee.sudo().chat_department.is_coordinator == True)
        is_coordinator = self.env.user.has_group('whatsapp_connector_inherited.group_chat_coordinator')

        if self.env.user.id == 2:
            domain = ['|', ('status', '=', 'new'), ('status', '=', 'current')]

        elif is_coordinator and self.env.user.id != 2:
            domain = ['|', ('status', '=', 'new'), ('status', '=', 'current'),
                      ('new_team_id', '=', coordinator.sudo().department_id.id)]

        else:
            domain = ['|', ('status', '=', 'new'), ('status', '=', 'current'),
                      ('agent_id', '=', self.env.user.id)]

        conversations = self.search(domain)

        return conversations.build_dict(22)