# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import random
import urllib.parse as urlparse

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.http_routing.models.ir_http import slug


class OpQuizResultMessage(models.Model):
    _name = "op.quiz.result.message"
    _description = "Quiz Result Message"

    result_from = fields.Float('Result From (%)')
    result_to = fields.Float('Result To (%)')
    message = fields.Html('Message')
    quiz_id = fields.Many2one('op.quiz', 'Quiz')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)


class OpQuiz(models.Model):
    _name = "op.quiz"
    _inherit = ['mail.thread']
    _description = "Quiz"

    @api.depends('line_ids', 'line_ids.mark')
    def _compute_get_total_marks(self):
        for obj in self:
            total = 0.0
            for line in obj.line_ids:
                if not line.display_type:
                    total += line.mark or 0.0
            obj.total_marks = total

    name = fields.Char('Name')
    state = fields.Selection([
        ('draft', 'Draft'), ('open', 'In-Progress'), ('done', 'Done'),
        ('cancel', 'Cancel')], 'State', default="draft")
    categ_id = fields.Many2one('op.quiz.category', 'Category')
    line_ids = fields.One2many('op.quiz.line', 'quiz_id', 'Questions')
    quiz_message_ids = fields.One2many('op.quiz.result.message', 'quiz_id',
                                       string='Message')
    total_marks = fields.Float(compute="_compute_get_total_marks",
                               string='Total Marks', store=True)
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one('op.quiz', 'Parent Quiz')
    assigned_to = fields.Selection([('open_for_all', 'Open For All'),
                                    ('specific_student', 'Specific Student(s)'),
                                    ('specific_course', 'Specific Course(s)'),
                                    ('specific_batch', 'Specific Batch(s)')],
                                   'Assigned To', default='open_for_all', required=True)
    course_ids = fields.Many2many('op.course', string='Courses')
    batch_ids = fields.Many2many('op.batch', string='Batches')
    student_ids = fields.Many2many('op.student', string='Students')

    # Result Configuration
    show_result = fields.Boolean('Display Result')
    right_ans = fields.Boolean('Display Right Answer')
    wrong_ans = fields.Boolean('Display Wrong Answer')
    not_attempt_ans = fields.Boolean('Display Not Attempted Answer')
    display_result = fields.Boolean('display On Portal')

    # Quiz Config with Question Bank
    quiz_config = fields.Selection([
        ('normal', 'Manual'),
        ('quiz_bank_selected', 'Quiz Bank with Selected Question'),
        ('quiz_bank_random', 'Quiz Bank with Random Quesiton')],
        'Configuration', default='normal')
    no_of_question = fields.Integer(
        'No of Question from each Question Bank', default=5)
    config_ids = fields.One2many('op.quiz.config', 'quiz_id',
                                 string='Quiz Configuration')

    # Configuration Part
    single_que = fields.Boolean('Single Question Per Page', default=True)
    prev_allow = fields.Boolean('Previous Question Allowed')
    prev_readonly = fields.Boolean('Only One Time Answer')
    no_of_attempt = fields.Integer('No of Attempt')
    que_required = fields.Boolean('All Question are Required')
    shuffle = fields.Boolean('Shuffle the Choices')
    exit_allow = fields.Boolean('Allow Exit')
    manual = fields.Boolean("Manual", default=False)

    # Timing Configuration
    time_config = fields.Boolean('Time Configuration', default=True)
    time_limit_hr = fields.Integer('Hour', default=1)
    time_limit_minute = fields.Integer('Minutes')
    time_expire = fields.Selection([
        ('auto_submit', 'Open attempts are submitted automatically'),
        ('grace_period', "There is a grace period when open attempts can be "
                         "submitted, but no more questions answered"),
        ('cancel', "Attempts must be submitted before time expires, "
                   "or they are not counted")], 'When Time Expires')
    grace_period = fields.Boolean('Grace Period')
    grace_period_hr = fields.Integer('Submission Grace Period')
    grace_period_minute = fields.Integer('Grace Minutes')
    start_view = fields.Selection([
        ('audio', 'Audio'), ('video', 'Video'), ('html', 'HTML')],
        'Starting View', default="html")
    quiz_audio = fields.Binary('Audio File')
    quiz_video = fields.Binary('Video File')

    def _compute_count_quiz(self):
        for record in self:
            record.total_quiz_count = len(
                self.env['op.quiz.result'].search([('quiz_id', '=', record.id)]))

    total_quiz_count = fields.Integer(
        string='Total Quiz',
        compute='_compute_count_quiz',
        readonly=True)

    def total_quiz(self):
        action = self.env.ref('openeducat_quiz.'
                              'act_open_op_quiz_result_view').read()[0]
        action['domain'] = [('quiz_id', 'in', self.ids)]
        return action

    def _get_default_note(self):
        result = """
               <div>
                   <p>During the exam:</p>
                   <ul><li>Close all programs, including email.</li>
                   <li>Maintain silence in the exam room.</li>
                   <li>The student may not use his or her textbook, course notes,
                    or receive help from a proctor or any other outside source.</li>
                   <li>Students must not stop the session and then return to it.</li>
                   <ul/>
               </div>"""
        return result

    quiz_html = fields.Html('HTML Content', default=_get_default_note)
    description = fields.Char('Short Description', size=256)
    challenge_ids = fields.Many2many(
        'gamification.challenge', string='Challenges')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    def action_confirm(self):
        for obj in self:
            course_id = [record.id for record in obj.course_ids]
            batch_id = [record.id for record in obj.batch_ids]

            if batch_id:
                students = self.env['op.student'].sudo().search(
                    [('course_detail_ids.course_id', 'in', course_id),
                     ('course_detail_ids.batch_id', 'in', batch_id)])
                obj.student_ids = students
            else:
                students = self.env['op.student'].sudo().search(
                    [('course_detail_ids.course_id', 'in', course_id)])
                if course_id:
                    obj.student_ids = students

            count = self.env['op.quiz.line'].search_count(
                [('quiz_id', '=', obj.id), ('que_type', '=', 'descriptive')])
            if obj.show_result and count > 0:
                obj.show_result = False
            obj.state = 'open'
        return True

    def action_draft(self):
        for obj in self:
            obj.state = 'draft'
        return True

    def action_cancel(self):
        for obj in self:
            obj.state = 'cancel'
        return True

    def action_done(self):
        for obj in self:
            obj.state = 'done'
        return True

    def action_random_question(self):
        self.ensure_one()
        question_list = []
        if self.line_ids:
            for line in self.line_ids:
                line.unlink()
        que_bank_line = self.env['op.question.bank.line']
        for config in self.config_ids:
            bank = config.bank_id
            question_ids = que_bank_line.search(
                [('bank_id', '=', bank.id)]).ids
            random.shuffle(question_ids)
            if config.no_of_question and config.no_of_question > 0:
                question_ids = question_ids[:config.no_of_question]
            for question in que_bank_line.browse(question_ids):
                if question.que_type in ['optional', 'blank', 'descriptive']:
                    line_data = []
                    correct_ans = ''
                    values = {
                        'name': question.name,
                        'question_mark': question.mark or 0.0,
                    }
                    if question.que_type == 'optional':
                        for answer in question.line_ids:
                            if answer.grade_id and answer.grade_id.value == 100.0:
                                correct_ans = answer.name
                            line_data.append([0, False, {
                                'name': answer.name,
                                'grade_id': answer.grade_id and (
                                    answer.grade_id.id) or False
                            }])
                        if not line_data:
                            continue
                        values['line_ids'] = line_data
                    elif question.que_type == 'blank':
                        correct_ans = question.answer or ''
                        values['grade_true_id'] = question.grade_true_id.id
                        values['grade_false_id'] = question.grade_false_id.id
                        values[
                            'que_type'] = question.que_type
                        values['case_sensitive'] = question.case_sensitive or False
                    values['answer'] = correct_ans
                    question_list.append([0, False, values])
        return question_list

    def get_result_id(self):
        uid = request.env.user.partner_id
        user = self.env['res.users']. \
            sudo().search([("partner_id", '=', uid.id)])
        result_pool = self.env['op.quiz.result']
        open_result = result_pool.sudo().search([
            ('user_id', '=', request.env.user.id),
            ('quiz_id', '=', self.id),
            ('state', '=', 'open')])
        hold_result = result_pool.sudo().search([
            ('user_id', '=', request.env.user.id),
            ('quiz_id', '=', self.id),
            ('state', '=', 'hold')])
        if open_result:
            return open_result[0]
        elif hold_result:
            return hold_result[0]
        result_id = result_pool.search([
            ('user_id', '=', request.env.user.id),
            ('quiz_id', '=', self.id),
            ('state', '=', 'asses')])
        total_attempt = len(result_id)
        allowed_attempt = self.no_of_attempt or 0.0
        if total_attempt >= allowed_attempt:
            raise exceptions.ValidationError(
                _('You are already reached maximum attempt of this exam'))

        line_data = []
        # ans = self.env['op.question.bank.line'].search([])
        if self.quiz_config in ('quiz_bank_selected', 'normal'):
            for line in self.line_ids:
                answer_data = []
                correct_ans = ''
                values = {
                    'name': line.name,
                    'question_mark': line.mark,
                    'bank_line': line.id,
                    'display_type': line.display_type,
                    'sequence': line.sequence
                    # 'bank_line':ans,
                }
                if line.que_type == 'optional':
                    for answer in line.line_ids:
                        if answer.grade_id and answer.grade_id.value == 100.0:
                            correct_ans = answer.name
                        answer_data.append([0, False, {
                            'name': answer.name,
                            'grade_id': answer.grade_id and
                                            answer.grade_id.id or False}])
                    values['line_ids'] = answer_data
                elif line.que_type == 'blank':
                    correct_ans = line.answer or ''
                    values['grade_true_id'] = line.grade_true_id.id or 0.0
                    values['grade_false_id'] = line.grade_false_id.id or 0.0
                    values['que_type'] = line.que_type
                    values['case_sensitive'] = line.case_sensitive or False
                elif line.que_type == 'descriptive':
                    values['que_type'] = line.que_type
                values['answer'] = correct_ans
                line_data.append([0, False, values])
        elif self.quiz_config == 'quiz_bank_random':
            line_data = self.action_random_question()
        result_id = result_pool.create({
            'name': self.name + ' - ' + user.name,
            'quiz_id': self.id,
            'user_id': user.id,
            'line_ids': line_data,
            'state': 'open'
        })
        for challenge in self.challenge_ids:
            self.env['gamification.goal'].sudo().search(
                [('challenge_id', '=', challenge.id),
                 ('user_id', '=', request.env.uid),
                 ('state', '!=', 'reached')]).sudo().update_goal()
            challenge.sudo()._check_challenge_reward()
        return result_id

    def view_quiz(self):
        quiz_url = request.httprequest.host_url + "quiz/rules/" + str(slug(
            self.get_result_id()))
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': quiz_url
        }

    def redirect_exam(self):
        return request.httprequest.host_url + "quiz/rules/" + str(slug(
            self.get_result_id()))

    def quiz_allow(self, diffrence=None, student_id=None):
        result_id = self.env['op.quiz.result'].search([
            ('user_id', '=', self.env.uid), ('quiz_id', '=', self.id),
            '|', '|', ('state', '=', 'submit'),
            ('state', '=', 'assets'), ('state', '=', 'done')])
        total_attempt = len(result_id)
        allowed_attempt = self.no_of_attempt or 0.0
        if diffrence:
            allow = 0
        elif student_id:
            allow = 0
        else:
            allow = 1

        if allowed_attempt and total_attempt >= allowed_attempt:
            allow = 0
        return allow

    def action_onboarding_quiz_layout(self):
        self.env.user.company_id.onboarding_quiz_layout_state = 'done'


class OpQuizLine(models.Model):
    _name = "op.quiz.line"
    _description = "Questions"

    sequence = fields.Integer(default=1)
    display_type = fields.Selection(
        selection=[
            ('section', "Section"),
        ],
        default=False)
    name = fields.Char('Question')
    que_type = fields.Selection([
        ('optional', 'Optional'), ('blank', 'Fill in the Blank'),
        ('descriptive', 'Descriptive')], 'Question Type', default='optional')
    answer = fields.Char('Answer')
    grade_true_id = fields.Many2one(
        'op.answer.grade', 'Grade for truly given answer')
    grade_false_id = fields.Many2one(
        'op.answer.grade', 'Grade for wrongly given answer')
    case_sensitive = fields.Boolean('Case Sensitive')
    line_ids = fields.One2many('op.quiz.answer', 'line_id', 'Answers')
    quiz_id = fields.Many2one('op.quiz', 'Quiz')
    mark = fields.Float('Marks', default=1.0)
    que_id = fields.Many2one('op.question.bank.line', 'question')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    _sql_constraints = [
        ('check_mark', 'check(mark > 0)',
         'Questions mark should be greater then 0')
    ]

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

    embed_code = fields.Text(
        'Embed Code', readonly=True, compute='_compute_get_embed_code')

    @api.onchange('url')
    def on_change_urls(self):
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

    def _compute_get_embed_code(self):
        for record in self:
            if record.material_type == 'video' and record.datas:
                record.embed_code = '<video controls \
                        controlsList="nodownload"><source class="audio" \
                        src="data:video/mp4;base64,%s"></video>' % record. \
                    datas.decode("utf-8")
            elif record.material_type == 'video' and (
                    record.video_type == 'youtube') and record.document_id:
                record.embed_code = '<iframe \
                src="https://www.youtube.com/embed/%s?theme=light" \
                allowFullScreen="true" frameborder="0"></iframe>' % (
                    record.document_id)
            elif record.material_type == 'video' and \
                    record.video_type == 'vimeo' and record.document_id:
                record.embed_code = '<iframe \
                src="https://player.vimeo.com/video/%s" \
                frameborder="0" webkitallowfullscreen mozallowfullscreen \
                allowfullscreen></iframe>' % (record.document_id)
            elif record.material_type == 'video' and \
                    record.video_type == 'dartfish' and record.document_id:
                record.embed_code = '<iframe \
                src="https://www.dartfish.tv/Embed?CR=' + \
                                    record.document_id + \
                                    '&VW=100%&VH=100%" frameborder="0" \
                                    allowfullscreen ></iframe>'
            elif record.datas and (record.material_type == 'document'):
                record.embed_code = '<iframe src="/material/embed/%s?page=1" \
                            allowFullScreen="true" height="%s" width="%s" \
                            frameborder="0"></iframe>' % (record.id, 315, 420)
            elif record.material_type == 'audio':
                record.embed_code = '<audio controls \
                            controlsList="nodownload"><source class="audio" \
                            src="data:audio/mp3;base64,%s"></audio>' % record. \
                    datas.decode("utf-8")
            elif record.datas and (record.material_type == 'infographic'):
                record.embed_code = '<iframe src="/material/embed/%s?page=1" \
                allowFullScreen="true" height="%s" width="%s" \
                frameborder="0"></iframe>' % (record.id, 315, 420)

            else:
                record.embed_code = False

    @api.depends('name')
    def _compute_website_url(self):
        super(OpQuizLine, self)._compute_website_url()
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        for material in self:
            if material.id:
                if self.env.registry.get('link.tracker'):
                    url = self.env['link.tracker'].sudo().create({
                        'url': '%s/quiz/material/%s' % (
                            base_url, slug(material))
                    }).short_url
                else:
                    url = '%s/quiz/material/%s' % (base_url, slug(material))
                material.website_url = url


class OpQuizAnswer(models.Model):
    _name = "op.quiz.answer"
    _description = "Quiz Answers"

    name = fields.Char('Answer')
    grade_id = fields.Many2one('op.answer.grade', 'Grade', required=True)
    line_id = fields.Many2one('op.quiz.line', 'Question')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)


class OpAnswerGrade(models.Model):
    _name = "op.answer.grade"
    _description = "Quiz Answer Grades"

    name = fields.Char('Name')
    value = fields.Float('Grade (%)')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)


class OpQuizConfig(models.Model):
    _name = "op.quiz.config"
    _description = "Quiz Configuration"

    quiz_id = fields.Many2one('op.quiz', 'Quiz')
    bank_id = fields.Many2one('op.question.bank', 'Question Bank')
    no_of_question = fields.Integer('Number of Question')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
