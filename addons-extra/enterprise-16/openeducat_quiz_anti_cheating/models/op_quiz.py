from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class Opquiz(models.Model):
    _inherit = 'op.quiz'

    face_tracking = fields.Boolean('Face Tracking')
    warning_limit = fields.Integer('Warning Limit', default=5)
    warning_state = fields.Selection([
        ('open', 'In-Progress After Warning'),
        ('hold', 'Permission From Admin'),
        ('submit', 'Submit'),
    ], string='Warning State', default='hold')
    face_sensitivity = fields.Float('Sensitivity', default=0.3)
    copy_paste_allow = fields.Boolean('Copy/Paste Allow')
    question_time_out = fields.Integer('Question Time Out')
    take_screenshot = fields.Selection([
        ('random', 'Random'),
        ('time_interval', 'Time Interval'),
    ], string='Take Screenshot')
    particular_interval = fields.Integer('Take Screenshots', default=1)
    random_start = fields.Integer("Start", default=1)
    random_end = fields.Integer("End", default=2)

    @api.constrains('face_sensitivity')
    def _check_face_sensitivity(self):
        for quiz in self:
            if not 0 < quiz.face_sensitivity < 1:
                raise ValidationError(_('Sensitivity Must Be Between 0 And 1'))

    @api.onchange('warning_limit')
    def onchange_warning_limit(self):
        for result in self:
            if result.warning_limit < 5:
                raise UserError(_('Warning limit can not be less than 5'))

    @api.onchange('question_time_out')
    def onchange_question_time_out(self):
        for result in self:
            if result.question_time_out < 0:
                raise UserError(_('Question time out must be positive.'))

    @api.onchange('particular_interval')
    def onchange_particular_interval(self):
        for result in self:
            if result.particular_interval < 1:
                raise UserError(_('Screenshot Interval time must be greater than 0.'))

    @api.onchange('random_start', 'random_end')
    def onchange_random_start(self):
        for result in self:
            if result.random_start > result.random_end:
                raise UserError(_('Start time must be less than end time.'))
            if result.random_start == result.random_end:
                raise UserError(_('Start time and end time not be the same.'))
            if result.random_start < 1:
                raise UserError(_('Screenshot Interval time must be greater than 0.'))
            if result.random_end < 1:
                raise UserError(_('Screenshot Interval time must be greater than 0.'))


class OpQuizResult(models.Model):
    _inherit = "op.quiz.result"

    warning_line_ids = fields.One2many(
        'op.quiz.result.warning', 'result_id', 'Warning Line')


class OpQuizResultWarning(models.Model):
    _name = "op.quiz.result.warning"
    _description = "Warning data"

    result_id = fields.Many2one('op.quiz.result', 'Result')
    warning_no = fields.Integer("Warning Number")
    warning_name = fields.Char('Name')
    time = fields.Char("Time")
    warning_attachment = fields.Binary(string="Attachment", attachment=False)
