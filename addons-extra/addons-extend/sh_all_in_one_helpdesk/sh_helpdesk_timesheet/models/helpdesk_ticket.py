# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import UserError


class TicketTimeAccountLine(models.Model):
    _name = 'ticket.time.account.line'
    _description = 'Ticket Time Account Line'

    def _get_default_start_time(self):
        active_model = self.env.context.get('active_model')
        if active_model == 'sh.helpdesk.ticket':
            active_id = self.env.context.get('active_id')
            if active_id:
                ticket_search = self.env['sh.helpdesk.ticket'].search(
                    [('id', '=', active_id)], limit=1)
                return ticket_search.start_time

    def _get_default_end_time(self):
        return datetime.now()

    def _get_default_duration(self):
        active_model = self.env.context.get('active_model')
        if active_model == 'sh.helpdesk.ticket':
            active_id = self.env.context.get('active_id')
            if active_id:
                ticket_search = self.env['sh.helpdesk.ticket'].search(
                    [('id', '=', active_id)], limit=1)
                diff = fields.Datetime.from_string(fields.Datetime.now(
                )) - fields.Datetime.from_string(ticket_search.start_time)
                if diff:
                    duration = float(diff.days) * 24 + \
                        (float(diff.seconds) / 3600)
                    return round(duration, 2)

    name = fields.Char("Description", required=True)
    start_date = fields.Datetime(
        "Start Date", default=_get_default_start_time, readonly=True)
    end_date = fields.Datetime(
        "End Date", default=_get_default_end_time, readonly=True)
    duration = fields.Float(
        "Duration (HH:MM)", default=_get_default_duration, readonly=True)
    # duration = fields.Float(
    #     "Duration (HH:MM)")
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    project_id = fields.Many2one('project.project', string='Project')

    @api.model
    def default_get(self, fields_list):
        res = super(TicketTimeAccountLine, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        ticket_id = self.env['sh.helpdesk.ticket'].sudo().browse(active_id)
        if ticket_id:
            timesheet_line = ticket_id.timehseet_ids.filtered(
                lambda x: x.ticket_id.id == ticket_id.id and x.end_date == False and x.start_date != False)
            if timesheet_line:
                res.update({
                    'project_id': timesheet_line.project_id.id,
                })
        else:
            if self.env.company.project_id:
                res.update({
                    'project_id': self.env.company.project_id.id,
                })
        return res

    def end_ticket(self):
        context = dict(self.env.context or {})
        active_model = context.get('active_model', False)
        active_id = context.get('active_id', False)

        vals = {'name': self.name, 'unit_amount': self.duration,
                'amount': self.duration, 'date': datetime.now()}
        ticket_search = False
        if active_model == 'sh.helpdesk.ticket':
            if active_id:
                ticket_search = self.env['sh.helpdesk.ticket'].search(
                    [('id', '=', active_id)], limit=1)

                if ticket_search:
                    vals.update({'start_date': ticket_search.start_time})
                    vals.update({'end_date': datetime.now()})
                    vals.update({'ticket_id': ticket_search.id})
                if self.project_id:
                    vals.update({'project_id': self.project_id.id})
                    act_id = self.env['project.project'].sudo().browse(
                        self.project_id.id).analytic_account_id
                    if act_id:
                        vals.update({'account_id': act_id.id})
                else:
                    vals.update({'project_id': self.env.company.project_id.id})
                    act_id = self.env['project.project'].sudo().browse(
                        self.env.company.project_id.id).analytic_account_id
                    if act_id:
                        vals.update({'account_id': act_id.id})
        timesheet_line = self.env['account.analytic.line'].sudo().search(
            [('ticket_id', '=', ticket_search.id), ('end_date', '=', False),('employee_id.user_id','=',self.env.user.id)], limit=1)
        if timesheet_line:
            timesheet_line.write(vals)
            if ticket_search:
                ticket_search.sudo().write(
                    {'start_time': False, 'duration': 0.0, 'ticket_running': False})
        self.sudo()._cr.commit()
        return {'type': 'ir.actions.client', 'tag': 'reload'}


class ShHelpdesk(models.Model):
    _name = 'sh.helpdesk.ticket'
    _inherit = ['sh.helpdesk.ticket']

    start_time = fields.Datetime("Start Time", copy=False, compute='_compute_start_time_test')
    end_time = fields.Datetime("End Time", copy=False,compute='_compute_end_time_test')
    total_time = fields.Char("Total Time", copy=False)
    timehseet_ids = fields.One2many(
        'account.analytic.line', 'ticket_id', string='Timesheets')
    duration = fields.Float('Real Duration', compute='_compute_duration')
    ticket_running = fields.Boolean("Ticket Running")
    ticket_run = fields.Boolean("Ticket run", compute='_check_ticket_run')

    # -----------------------------------------------------------------------------
    # COMPUTE END-TIME BASED ON USER SPECIFIC TIMESHEET FROM TIMESHEET MENU
    # -----------------------------------------------------------------------------
    def _compute_end_time_test(self):
        for rec in self:
            rec.end_time = (rec.timehseet_ids.filtered(lambda x: x.ticket_id.id == rec.id and x.end_date == False and x.start_date != False and x.employee_id.user_id == self.env.user)).end_date    
    # -----------------------------------------------------------------------------
    # COMPUTE END-TIME BASED ON USER SPECIFIC TIMESHEET FROM TIMESHEET MENU
    # -----------------------------------------------------------------------------



    # -----------------------------------------------------------------------------
    # COMPUTE START-TIME BASED ON USER SPECIFIC TIMESHEET FROM TIMESHEET MENU
    # -----------------------------------------------------------------------------
    def _compute_start_time_test(self):
        for rec in self:
            rec.start_time = (rec.timehseet_ids.filtered(lambda x: x.ticket_id.id == rec.id and x.end_date == False and x.start_date != False and x.employee_id.user_id == self.env.user)).start_date
    # -----------------------------------------------------------------------------
    # COMPUTE START-TIME BASED ON USER SPECIFIC TIMESHEET FROM TIMESHEET MENU
    # -----------------------------------------------------------------------------



    # -----------------------------------------------------------------------------
    # CHECK TRUE/FALSE BASED ON TIMER START BY USER AND RELATED TIMESHEET ENTRY
    # -----------------------------------------------------------------------------
    def _check_ticket_run(self):
        for rec in self:
            rec.ticket_run = False
            timesheet_line = rec.timehseet_ids.filtered(
                    lambda x: x.ticket_id.id == rec.id and x.end_date == False and x.start_date != False and x.employee_id.user_id == self.env.user)
            if timesheet_line:
                rec.ticket_run = True
    # -----------------------------------------------------------------------------
    # CHECK TRUE/FALSE BASED ON TIMER START BY USER AND RELATED TIMESHEET ENTRY
    # -----------------------------------------------------------------------------


    @api.model
    def get_duration(self, ticket):
        if ticket:
            ticket = self.sudo().browse(int(ticket))
            if ticket and ticket.start_time:
                diff = fields.Datetime.from_string(
                    fields.Datetime.now()) - fields.Datetime.from_string(ticket.start_time)
                if diff:
                    duration = float(diff.days) * 24 + \
                        (float(diff.seconds) / 3600)
                    return diff.total_seconds() * 1000

    # @api.depends('timehseet_ids.unit_amount')
    def _compute_duration(self):
        for rec in self:
            rec.duration = 0.0
            if rec and rec.timehseet_ids:
                timesheet_line = rec.timehseet_ids.filtered(
                    lambda x: x.ticket_id.id == rec.id and x.end_date == False and x.start_date != False and x.employee_id.user_id == self.env.user)
                if timesheet_line:
                    rec.duration = timesheet_line[0].unit_amount

    def action_ticket_start(self):
        # if self.ticket_running == True:
        #     raise UserError(
        #         " This ticket has been already started by another user !")
        if not self.env.company.project_id:
            raise UserError(
                "Please Set Default Project from configuration!")
        
        running_ticket = self.env['sh.helpdesk.ticket'].sudo().search(
            [('ticket_running', '=', True), ('id', '!=', self.id)], limit=1)
        
        if not self.env.company.sh_multiple_ticket_allowed and running_ticket:
            raise UserError("You can not start 2 tickets at same time !")

       
        # self.sudo().start_time = datetime.now()

        vals = {'name': '/', 'date': datetime.now()}
        if self:
            vals.update({'start_date': datetime.now()})
            vals.update({'ticket_id': self.id})
        usr_id = self.env.user.id
        if usr_id:
            emp_search = self.env['hr.employee'].search(
                [('user_id', '=', usr_id)], limit=1)
            if emp_search:
                vals.update({'employee_id': emp_search.id})
            else:
                # raise UserError("No employee found for %s",self.env.user.name)
                raise UserError(_("No employee found for %s") % (self.env.user.name,))
        if self.env.company.project_id:
            vals.update({'project_id': self.env.company.project_id.id})
            act_id = self.env['project.project'].sudo().browse(
                self.env.company.project_id.id).analytic_account_id
            if act_id:
                vals.update({'account_id': act_id.id})
        self.env['account.analytic.line'].sudo().create(vals)
        self.sudo().write({'ticket_running': True})
        self.sudo()._cr.commit()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_ticket_end(self):
        
        start_time_rec = self.sudo().timehseet_ids.filtered(lambda x: x.ticket_id.id == self.id and x.end_date == False and x.start_date != False and x.employee_id.user_id == self.env.user)

        # self.sudo().end_time = datetime.now()

        # tot_sec = (self.end_time - start_time_rec.start_date).total_seconds()
        # tot_hours = round((tot_sec / 3600.0), 2)

        # self.sudo().total_time = tot_hours

        if self.env.company.sh_default_description:
            context = {}
            context.update({
                'default_name': str(self.env.user.name)+'-'+str(self.name)
            })
            return {
                'name': "End Ticket",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ticket.time.account.line',
                'context': context,
                'target': 'new',
            }
        else:
            return {
                'name': "End Ticket",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ticket.time.account.line',
                'target': 'new',
            }
