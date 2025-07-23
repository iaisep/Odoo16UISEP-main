from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def _compute_total_percentage(self):
        percentage = []
        for record in self:
            for value in record.logs_line:
                percentage.append(value.attentive_percentage)
            Sum = sum(percentage)
            if len(percentage) > 0:
                self.meeting_attentive_percentage = Sum / len(percentage)

    logs_line = fields.One2many(
        'channel.logs', 'meeting_id', string='Channel Logs')
    guest_line = fields.One2many('meeting.guest', 'meetin_guest_id',
                                 string='guest Logs')
    channel_id = fields.Many2one('mail.channel', string="Channel")
    total_guest = fields.Integer(string="Total guest")
    total_student = fields.Integer(string="Total student")
    total_member = fields.Integer(string="Total Member")
    meeting_start_time = fields.Datetime("Meeting Start Time")
    meeting_end_time = fields.Datetime("Meeting End Time")
    meeting_duration = fields.Float('Meeting Duration')
    meeting_attentive_percentage = fields.Integer(string="Meeting Attentiveness")


class OpMeetingLogs(models.Model):
    _name = 'channel.logs'
    _description = 'channel Logs'

    @api.depends("visibility_line")
    def _compute_get_total_time(self):
        for record in self:
            total_time = 0
            for time in record.visibility_line:
                total_time = total_time + time.time_log
            record.total_time = total_time

    @api.depends("total_time")
    def _compute_get_percentage(self):
        for record in self:
            if record.meeting_id.duration:
                attendee_time = record.total_time / 60
                if record.meeting_id.duration >= 1:
                    meeting_hour = (record.meeting_id.duration // 1) * 60
                    meeting_minute = (record.meeting_id.duration % 1) * 100
                    per_student_percentage = \
                        100 - ((attendee_time * 100) / (meeting_hour + meeting_minute))
                    record.attentive_percentage = per_student_percentage
                else:
                    per_student_percentage = \
                        100 - ((attendee_time * 100) / (record.meeting_id.duration
                                                        * 100))
                    record.attentive_percentage = per_student_percentage
            else:
                record.attentive_percentage = per_student_percentage = 0

    partner_id = fields.Many2one('res.partner', string='Attendee')
    join_time = fields.Datetime('Joining Time')
    meeting_id = fields.Many2one('calendar.event')
    visibility_line = fields.One2many(
        'log.attentive', 'logs_id', string='Visibility')
    total_time = fields.Float(string="Time", compute="_compute_get_total_time",
                              store=True)
    attentive_percentage = fields.Integer(string="Percentage",
                                          compute="_compute_get_percentage",
                                          store=True, readonly=False)
    raised_hand = fields.Integer(string="Raised Hand")


class OpMeetingguest(models.Model):
    _name = 'meeting.guest'
    _description = 'Meeting Guest'

    guest = fields.Char(string='Guest')
    meetin_guest_id = fields.Many2one('calendar.event')


class OpLogVisible(models.Model):
    _name = 'log.attentive'
    _description = 'Meeting Attentiveness'

    @api.depends("start_time", "end_time")
    def _compute_get_time_in_sec(self):
        for value in self:
            if value.end_time and value.start_time:
                a = value.end_time - value.start_time
                diff_in_sec = a.total_seconds()
                value.time_log = diff_in_sec
            else:
                value.time_log = 0.0

    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    logs_id = fields.Many2one('channel.logs', string="Logs")
    time_log = fields.Float(string="Time",
                            compute="_compute_get_time_in_sec", store=True)
