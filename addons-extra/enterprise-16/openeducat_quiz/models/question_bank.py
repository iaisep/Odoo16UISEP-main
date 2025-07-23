# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import urllib.parse as urlparse

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpQuestionBank(models.Model):
    _name = "op.question.bank"
    _description = "Quiz Question Bank"

    name = fields.Char('Name')
    bank_type_id = fields.Many2one('op.question.bank.type', 'Type')
    description = fields.Text('Description')
    line_ids = fields.One2many('op.question.bank.line', 'bank_id', 'Questions')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    def action_onboarding_question_bank_layout(self):
        self.env.user.company_id.onboarding_question_bank_layout_state = 'done'


class OpQuestionLine(models.Model):
    _name = "op.question.bank.line"
    _description = "Quiz Question Lines"

    name = fields.Char('Question')
    que_type = fields.Selection([
        ('optional', 'Optional'), ('blank', 'Fill in the Blank'),
        ('descriptive', 'Descriptive')], 'Question Type', default='optional')
    answer = fields.Char('Answer')
    grade_true_id = fields.Many2one(
        'op.answer.grade', 'Grade for truly given answer')
    grade_false_id = fields.Many2one(
        'op.answer.grade', 'Grade for wrongly given answer')
    bank_id = fields.Many2one('op.question.bank', 'Question Bank')
    case_sensitive = fields.Boolean('Case Sensitive')
    mark = fields.Float('Marks', default=1.0)
    line_ids = fields.One2many('op.question.bank.answer', 'question_id',
                               string='Answers')
    material_type = fields.Selection([
        ('video', 'Video'), ('audio', 'Audio'),
        ('document', 'Document/PDF'), ('infographic', 'Image')],
        string='Material Type')
    video_type = fields.Selection([
        ('youtube', 'Youtube'), ('vimeo', 'Vimeo'),
        ('dartfish', 'Dartfish'), ('fileupload', 'FileUpload')],
        string="Video Type", default="youtube")
    datas = fields.Binary('Content', attachment=True)
    url = fields.Char('Document URL', help="Youtube or Google Document URL")
    document_id = fields.Char('Document ID')

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.onchange('url')
    def on_change_url(self):
        self.ensure_one()
        if self.url:
            data = urlparse.urlparse(self.url)
            if data.scheme and data.netloc:
                doc_id = False
                if self.video_type == 'youtube':
                    url_data = urlparse.urlparse(self.url)
                    query = urlparse.parse_qs(url_data.query)
                    doc_id = query.get('v', False) and query['v'][0] or False
                    if not doc_id:
                        doc_id = url_data.path and url_data.path[1:] or False
                elif self.video_type == 'vimeo':
                    url_data = urlparse.urlparse(self.url)
                    doc_id = url_data.path and url_data.path[1:] or False
                elif self.video_type == 'dartfish':
                    url_data = urlparse.urlparse(self.url)
                    query = urlparse.parse_qs(url_data.query)
                    doc_id = query.get('CR', False) and query['CR'][0] or False
            else:
                raise ValidationError(
                    _('Please enter valid URL: %s' % self.url))
            if doc_id:
                self.document_id = doc_id
            else:
                raise ValidationError(_('Could not fetch url. Document Id or \
                        access right not available:\n%s') % doc_id)


class OpQuesionBankAnswer(models.Model):
    _name = "op.question.bank.answer"
    _description = "Quiz Question Bank Answers"

    name = fields.Char('Answer')
    grade_id = fields.Many2one('op.answer.grade', 'Grade')
    question_id = fields.Many2one('op.question.bank.line', 'Question')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)


class OpQuestionBankType(models.Model):
    _name = "op.question.bank.type"
    _description = "Quiz Question Bank Type"

    name = fields.Char('Name')
    description = fields.Text('Description')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)
