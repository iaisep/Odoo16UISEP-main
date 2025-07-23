from datetime import date

import pytz

from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    register_id = fields.Many2one('op.attendance.register', string="Register")
    sheet_id = fields.Many2one('op.attendance.sheet', string="Sheet")

    @api.onchange('register_id')
    def onchange_register_sheet(self):
        self.course_id = self.register_id.course_id
        self.batch_id = self.register_id.batch_id
        if self.register_id.subject_id:
            self.subject_id = self.register_id.subject_id
        today_date = date.today()
        sheet_ids = self.env['op.attendance.sheet'].search(
            [('attendance_date', '=', today_date),
             ('register_id', '=', self.register_id.id)])
        for sheet in sheet_ids:
            self.sheet_id = sheet.id
            break
        if not sheet_ids:
            self.sheet_id = None
        return {'domain': {
            'sheet_id': [('id', 'in', sheet_ids.ids)],
            'subject_id': [('id', 'in', self.course_id.subject_ids.ids)]
        }}

    def write(self, vals):
        if self.channel_id and self.sheet_id:
            self.channel_id.sheet_id = self.sheet_id.id
        super(CalendarEvent, self).write(vals)


class OpAttendanceSheet(models.Model):
    _inherit = 'op.attendance.sheet'

    @api.depends("name", "attendance_date")
    def _compute_get_sheet_date(self):
        for record in self:
            now_tz = record.date_time
            now = now_tz.astimezone(pytz.timezone(self.env.user.tz))
            tz = pytz.timezone(self.env.user.tz)
            now_tz = now.astimezone(tz)
            record.attendance_sheet_date = record.name + \
                " " + str(now_tz.strftime("%d-%m-%Y %H:%M"))

    attendance_sheet_date = fields.Char(
        string="attendance sheet date", compute="_compute_get_sheet_date",)
    date_time = fields.Datetime(
        'Date Time', default=lambda self: fields.Datetime.now())
