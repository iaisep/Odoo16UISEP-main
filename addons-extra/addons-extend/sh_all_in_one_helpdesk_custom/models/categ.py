# Copyright 2014 ABF OSIELL <http://osiell.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError

 

 

class HelpdeskCategory(models.Model):
    _inherit = "helpdesk.category"

    public_site=fields.Boolean(string="Publico")
    help_teams_id=fields.Many2many("sh.helpdesk.team",string="Equipos de asistencia")

class HelpdeskSubcategory(models.Model):
    _inherit = "helpdesk.subcategory"

    public_site=fields.Boolean(string="Publico")

class ShHelpdeskTeam(models.Model):
    _inherit = "sh.helpdesk.team"

    users_leads_ids=fields.Many2many("res.users",'users_leads_rel','team_id','user_id',string="Lideres")
    mail1=fields.Char(string="Email 1")
    mail2=fields.Char(string="Email 2")
    mail3=fields.Char(string="Email 3")

class ShHelpdeskTicket(models.Model):
    _inherit = "sh.helpdesk.ticket"

    @api.onchange('team_id')
    def onchange_team(self):
        if self.team_id:
            self.team_head = self.team_id.team_head
            self.sh_user_ids = self.team_id.users_leads_ids.ids
            user_ids = self.env['sh.helpdesk.team'].sudo().search([('id', '=', self.team_id.id)   ])
            return {
                'domain': {
                    'user_id': [('id', 'in', user_ids.team_members.ids)],
                    'sh_user_ids': ['|',('id', 'in', user_ids.team_members.ids),('id','in', user_ids.users_leads_ids.ids)]
                }
            }
        else:
            self.team_head = False

    team_members_ids = fields.Many2many('res.users', string='Miembros', related="team_id.team_members")

    @api.model_create_multi
    def create(self, vals):
        i=0
        for val in vals:
            #########validando team_id
            if 'team_id' in val:
                team_id=self.env['sh.helpdesk.team'].search([('id','=',val['team_id'] )])
                if team_id and team_id.users_leads_ids:
                    vals[i].update({'sh_user_ids':[(6,0,team_id.users_leads_ids.ids)]})
            ##########################
            if val.get('email_subject',False) or val.get('email',False):
                black_list=self.env['sh.helpdesk.ticket.black.lists'].search(['|',('name','ilike',val.get('email',False)),
                    ('name','ilike',val.get('email_subject',False))])
                if black_list:
                    raise UserError(_("El asunto '%s' ó el mail '%s', no estan permitidos, entan incluidos en lista negra...")
                        %(val.get('email_subject',False),val.get('email',False)))
            i+=1
        res = super(ShHelpdeskTicket, self).create(vals)
        return res

    def write(self, vals):
        res = super(ShHelpdeskTicket, self).write(vals)
        for this in self:
            if this.email_subject and this.email:
                for bl in self.env['sh.helpdesk.ticket.black.lists'].search([]):
                    if bl.name in this.email or bl.name in this.email_subject:
                        raise UserError(_("El asunto '%s' ó el mail '%s', no estan permitidos, entan incluidos en lista negra...")%(this.email_subject, this.email))

        return res


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def generate_email(self, res_ids, fields):
        res=super(MailTemplate,self).generate_email(res_ids, fields)
        template_id=self.env.ref('sh_all_in_one_helpdesk.sh_ticket_new_template', raise_if_not_found=False)
        if template_id and template_id.id==self.id and res.get('model')=='sh.helpdesk.ticket':
            ticket_id=self.env['sh.helpdesk.ticket'].search([('id','=',res.get('res_id'))])
            mails=False
            mail1=ticket_id.team_id.mail1+'@'+ticket_id.team_id.alias_domain if ticket_id.team_id.mail1 and ticket_id.team_id.alias_domain else False
            mail2=ticket_id.team_id.mail2+'@'+ticket_id.team_id.alias_domain if ticket_id.team_id.mail2 and ticket_id.team_id.alias_domain else False
            mail3=ticket_id.team_id.mail2+'@'+ticket_id.team_id.alias_domain if ticket_id.team_id.mail3 and ticket_id.team_id.alias_domain else False
            if mail1:
                mails=mail1
            if mail2:
                mails=mail2
            if mail3:
                mails=mails+','+mail3
            res.update({'email_cc':mails})

        return res

class ShHelpdeskSla(models.Model):
    _inherit = "sh.helpdesk.sla"
    
    sh_team_id=fields.Many2many("sh.helpdesk.team",string="Equipo de servicio de ayuda?")

 
