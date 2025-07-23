# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import base64
from collections import OrderedDict
from datetime import datetime

import werkzeug
from markupsafe import Markup

from odoo import _, http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv import expression

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import QueryURL

PPG = 10  # record per page


class OpeneducatQuizRender(http.Controller):

    def get_quiz_result_data(self, values):
        wrong_answers = []
        not_attempt_answer = []
        right_answers = []

        result = request.env['op.quiz.result']. \
            sudo().browse(int(values['ExamID']))
        result_line_answer = request.env['op.quiz.result.line.answers']
        for line in result.line_ids:
            if ('question' + str(line.id)) in values:
                given_answer_id = int(values['question' + str(line.id)])
                answer = result_line_answer.browse(
                    given_answer_id)
                line.given_answer = answer.name
                if answer.grade_id and answer.grade_id.value == 100.0:
                    right_answers.append({
                        'question': line.name,
                        'answer': answer.name,
                        'que_type': line.que_type})
                    line.mark = line.question_mark or 0.0
                else:
                    wrong_answers.append({
                        'que_type': line.que_type,
                        'question': line.name,
                        'given_answer': answer.name,
                        'answer': line.answer or '',
                    })
                    line.mark = answer.grade_id.value * line.question_mark / 100
            elif ('blank' + str(line.id)) in values:
                line.given_answer = values['blank' + str(line.id)]
                if line.case_sensitive:
                    if line.answer == line.given_answer:
                        received_mark = (line.question_mark *
                                         (line.grade_true_id.value or 0.0)) / 100
                        line.mark = received_mark
                    else:
                        received_mark = (line.question_mark *
                                         (line.grade_false_id.value or 0.0)) / 100
                        line.mark = received_mark
                else:
                    if line.answer.lower() == line.given_answer.lower():
                        received_mark = (line.question_mark *
                                         (line.grade_true_id.value or 0.0)) / 100
                        line.mark = received_mark
                    else:
                        received_mark = (line.question_mark *
                                         (line.grade_false_id.value or 0.0)) / 100
                        line.mark = received_mark
            elif ('descriptive' + str(line.id)) in values:
                line.given_answer = values['descriptive' + str(line.id)]
            else:
                not_attempt_answer.append({
                    'question': line.name,
                    'que_type': line.que_type,
                    'answer': line.answer or ''})
        score = result.score or 0.0
        quiz = result.quiz_id
        message = ''
        is_message = 0
        for msg in quiz.quiz_message_ids:
            result_to = msg.result_to
            result_from = msg.result_from
            if (result <= result_to) and (result >= result_from):
                message = msg.message
                is_message = 1
        display_wrong_ans = 0
        if quiz.wrong_ans and wrong_answers:
            display_wrong_ans = 1
        display_true_ans = 0
        if quiz.right_ans and right_answers:
            display_true_ans = 1
        not_attempt_ans = 0
        if quiz.not_attempt_ans and not_attempt_answer:
            not_attempt_ans = 1
        result.submit_date = datetime.today()
        result.state = 'submit'
        return {
            'wrong_answer': wrong_answers,
            'not_attempt_answer': not_attempt_answer,
            'right_answers': right_answers,
            'total_question': result.total_question,
            'total_correct': result.total_correct,
            'total_incorrect': result.total_incorrect,
            'total_marks': result.total_marks,
            'received_marks': result.received_marks,
            'percentage': score,
            'display_wrong_ans': display_wrong_ans,
            'display_true_ans': display_true_ans,
            'not_attempt_ans': not_attempt_ans,
            'message': message,
            'is_message': is_message
        }

    def get_search_domain_quiz(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', '|', '|', '|', '|', '|', '|',
                    ('index', 'ilike', srch), ('quiz_id', 'ilike', srch),
                    ('finish_date', 'ilike', srch), ('total_correct', 'ilike', srch),
                    ('total_incorrect', 'ilike', srch),
                    ('total_marks', 'ilike', srch), ('received_marks', 'ilike', srch),
                    ('score', 'ilike', srch), ('total_question', 'ilike', srch)]
        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]
        return domain

    def check_access_role(self, student):
        user = request.env.user.partner_id
        if student.partner_id.id != user.id:
            parent_list = []
            for parent in student.parent_ids:
                parent_list.append(parent.user_id.partner_id.id)
            if user.id in parent_list:
                return True
            else:
                return False
        else:
            return True

    def get_student(self, student_id=None, **kw):

        partner = request.env.user.partner_id
        student_obj = request.env['op.student']
        if not student_id:
            student = student_obj.sudo().search([
                ('partner_id', '=', partner.id)])
        else:
            student = student_obj.sudo().browse(student_id)

            access_role = self.check_access_role(student)
            if not access_role:
                return False

        return student

    @http.route(['/users/result-overview',
                 '/users/result-overview/<int:student_id>',
                 '/users/result-overview/page/<int:page>',
                 '/users/result-overview/<int:student_id>/page/<int:page>'],
                type="http", auth="user", website=True)
    def get_result_overview(
        self, date_begin=None, student_id=None, date_end=None, page=1,
        search=None, ppg=False, sortby=None, filterby=None,
            search_in='index', groupby='none', **post):

        quiz_result = request.env['op.quiz.result'].search([])
        user = request.env['res.users'].browse(request.env.uid)
        student = request.env["op.student"].sudo().search(
            [('id', '=', student_id)])
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        searchbar_sortings = {
            'index': {'label': _('Index'), 'order': 'index'},
            'quiz_id': {'label': _('Exam'), 'order': 'quiz_id'},
            'finish_date': {'label': _('Attempt Date'),
                            'order': 'finish_date'},
            'total_question': {'label': _('Total Question'),
                               'order': 'total_question'},
            'total_correct': {'label': _('Total Correct'),
                              'order': 'total_correct'},
            'total_incorrect': {'label': _('Total InCorrect'),
                                'order': 'total_incorrect'},
            'total_marks': {'label': _('Total Marks'),
                            'order': 'total_marks'},
            'received_marks': {'label': _('Received Marks'),
                               'order': 'received_marks'},
            'score': {'label': _('Total Score'), 'order': 'score'},
        }
        if not sortby:
            sortby = 'index'
        order = searchbar_sortings[sortby]['order']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")]
                         for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'index': {'input': 'index',
                      'label': Markup(_('Search in Index <span class="nolabel"> '
                                        '(in Content)</span>'))},
            'quiz_id': {'input': 'quiz_id',
                        'label': _('Search in Exam Name')},
            'finish_date': {'input': 'finish_date',
                            'label': _('Search in Attempt Date')},
            'score': {'input': 'score',
                      'label': _('Search in Score')},
            'total_marks': {'input': 'total_marks',
                            'label': _('Search in Total Marks')},
            'received_marks': {'input': 'received_marks',
                               'label': _('Search in Received Marks')},
            'total_question': {'input': 'total_question',
                               'label': _('Search in Total Question')},
            'total_correct': {'input': 'total_correct',
                              'label': _('Search in Total Correct')},
            'total_incorrect': {'input': 'total_incorrect',
                                'label': _('Search in Total InCorrect')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }

        if student_id:
            quiz = request.env['op.quiz.result'].sudo().search(
                [('user_id', '=', student.user_id.id)])
            for rec in quiz:
                searchbar_filters.update({
                    str(rec.quiz_id.id):
                        {'label': rec.quiz_id.name,
                         'domain': [('quiz_id', '=', rec.quiz_id.id)]}
                })
        else:
            quiz = request.env['op.quiz.result'].sudo().search(
                [('user_id', '=', user.id)])
            for rec in quiz:
                searchbar_filters.update({
                    str(rec.quiz_id.id):
                        {'label': rec.quiz_id.name,
                         'domain': [('quiz_id', '=', rec.quiz_id.id)]}
                })
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'index'):
                search_domain = expression.OR(
                    [search_domain, [('index', 'ilike', search)]])
            if search_in in ('all', 'quiz_id'):
                search_domain = expression.OR(
                    [search_domain, [('quiz_id', 'ilike', search)]])
            if search_in in ('all', 'finish_date'):
                search_domain = expression.OR(
                    [search_domain, [('finish_date', 'ilike', search)]])
            if search_in in ('all', 'score'):
                search_domain = expression.OR(
                    [search_domain, [('score', 'ilike', search)]])
            if search_in in ('all', 'total_marks'):
                search_domain = expression.OR(
                    [search_domain, [('total_marks', 'ilike', search)]])
            if search_in in ('all', 'received_marks'):
                search_domain = expression.OR(
                    [search_domain, [('received_marks', 'ilike', search)]])
            if search_in in ('all', 'total_correct'):
                search_domain = expression.OR(
                    [search_domain, [('total_correct', 'ilike', search)]])
            if search_in in ('all', 'total_incorrect'):
                search_domain = expression.OR(
                    [search_domain, [('total_incorrect', 'ilike', search)]])
            if search_in in ('all', 'total_question'):
                search_domain = expression.OR(
                    [search_domain, [('total_question', 'ilike', search)]])
            domain += search_domain

        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        domain += self.get_search_domain_quiz(search, attrib_values)

        if student_id:
            keep = QueryURL('/users/result-overview/%s' % student_id,
                            search=search, attrib=attrib_list,
                            order=post.get('order'))

            domain += [('user_id', '=', student.user_id.id)]

            total = request.env['op.quiz.result'].sudo().search_count(domain)

            pager = portal_pager(
                url="/users/result-overview/%s" % student_id,
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_id': search_in},
                total=total,
                page=page,
                step=ppg
            )
        else:
            keep = QueryURL('/users/result-overview',
                            search=search, attrib=attrib_list,
                            order=post.get('order'))
            domain += [('user_id', '=', user.id)]

            total = request.env['op.quiz.result'].sudo().search_count(domain)

            pager = portal_pager(
                url="/users/result-overview",
                url_args={'date_begin': date_begin, 'date_end': date_end,
                          'sortby': sortby, 'filterby': filterby,
                          'search': search, 'search_id': search_in},
                total=total,
                page=page,
                step=ppg
            )
        if student_id:
            student_access = self.get_student(student_id=student_id)
            if student_access is False:
                return request.render('website.404')
            post['user'] = user
            attempt = quiz_result.sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])
        else:
            post['user'] = user
            attempt = quiz_result.sudo().search(
                domain, order=order, limit=ppg, offset=pager['offset'])

        total_exam = 0
        progress = 0
        if attempt:
            total_result = sum([val.score for val in attempt])
            total_exam = len(attempt.ids)
            progress = int(total_result) / int(len(attempt))
        post['total_exam'] = total_exam
        post['progress'] = progress
        post['result_btn'] = 0
        data = []
        attempts = attempt.filtered(lambda r: r.state == 'done')
        for res in attempts:
            data.append({
                'id': res.id,
                'index': res.index,
                'name': res.quiz_id.name,
                'ttl_que': res.total_question or 0,
                'ttl_crct': res.total_correct or 0,
                'ttl_incrct': res.total_incorrect or 0,
                'ttl_marks': res.total_marks or 0,
                'rec_marks': res.received_marks or 0,
                'score': str(res.score or 0) + ' %',
                'finish_date': res.finish_date,
                'display_result': res.quiz_id.display_result,
            })
        post['result_data'] = data

        if student_id:
            values = {
                'date': date_begin,
                'result_data': data,
                'page_name': 'Quiz info',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'stud_id': student_id,
                'default_url': '/users/result-overview/%s' % student_id,
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,

            }

        else:
            values = {
                'date': date_begin,
                'result_data': data,
                'page_name': 'Quiz info',
                'pager': pager,
                'ppg': ppg,
                'keep': keep,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
                'default_url': '/users/result-overview',
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'searchbar_groupby': searchbar_groupby,
                'groupby': groupby,

            }

        return http.request.render('openeducat_quiz.my_result', values)

    @http.route(['/online-exams',
                 '/online-exams/<int:student_id>'],
                type="http", auth="user", website=True)
    def get_exam_details(self, search='', student_id=None, **post):
        quiz_result = request.env['op.quiz.result']
        stud = request.env['op.student'].sudo().search(
            [('id', '=', student_id)])

        if student_id:
            user = request.env['res.users'].sudo().browse(stud.user_id.id)
        else:
            user = request.env['res.users'].browse(request.env.uid)

        post['user'] = user
        attempt = quiz_result.sudo().search(
            [('user_id', '=', user.id)])
        progress = 0
        quiz_attempt = {}
        total_exam = 0
        if attempt:
            total_result = sum([val.score for val in attempt])
            total_exam = len(attempt.ids)
            progress = int(total_result) / int(len(attempt))
        post['total_exam'] = total_exam
        post['progress'] = round(progress, 2)
        post['result_btn'] = 1
        domain = [('state', '=', 'open')]
        if search:
            domain += [('name', 'ilike', search)]

        quiz_domain = domain + [('assigned_to', '=', 'open_for_all')]
        quiz_ref = request.env['op.quiz']
        open_exam = quiz_ref.sudo().search(quiz_domain)
        if student_id:
            selected_user = domain + [('student_ids.user_id', 'in', [stud.user_id.id])]
        else:
            selected_user = domain + [('student_ids.user_id', 'in', [request.env.uid])]
        selected_quiz = quiz_ref.sudo().search(selected_user)

        exams = [record for record in open_exam]
        exams += [record for record in selected_quiz]

        if student_id:
            student = request.env['op.student'].sudo().search(
                [('user_id', '=', stud.user_id.id)])
        else:
            student = request.env['op.student'].sudo().search(
                [('user_id', '=', request.env.uid)])
        course_id = [i.course_id.id for i in student.course_detail_ids]
        batch_id = [i.batch_id.id for i in student.course_detail_ids]
        selected_users_domian = domain + [
            '|', ('course_ids', 'in', course_id),
            ('batch_ids', 'in', batch_id)]
        selected_quizs = quiz_ref.sudo().search(selected_users_domian)

        set_1 = set(exams)
        set_2 = set(selected_quizs)
        diffrence = list(set_2 - set_1)

        exams += [record for record in diffrence]

        for exam in exams:
            ttl_atmp = quiz_result.sudo().search(
                [('quiz_id', '=', exam.id)])
            ttl_res = 0
            diffrence_id = [record.id for record in diffrence]

            if exam.id in diffrence_id:
                allow = exam.quiz_allow(diffrence, student_id=None)
            elif student_id:
                allow = exam.quiz_allow(diffrence, student_id)
            else:
                allow = exam.quiz_allow()
            if ttl_atmp:
                ttl_res = sum([atmp_res.score for atmp_res in ttl_atmp])
                ttl_res = ttl_res / len(ttl_atmp.ids)
            quiz_attempt.update({exam.id: {
                'ttl_atmp': len(ttl_atmp.ids),
                'avg_res': int(ttl_res),
                'allow': allow
            }})
        post['quiz_attempt'] = quiz_attempt
        post['exams'] = exams
        if selected_quiz:
            post['my_exam'] = True

        return http.request.render('openeducat_quiz.online_exam_page', post)

    @http.route('/exam/start/<model("op.quiz"):quiz>',
                type="http", auth="public", sitemap=False, website=True)
    def start_exam(self, quiz):
        exam_link = quiz.sudo().redirect_exam()
        return request.redirect(exam_link)

    @http.route('/quiz/submit/<model("op.quiz.result"):result>',
                type="http", auth="public", sitemap=False, website=True)
    def get_result_submit(self, result):
        if not result.quiz_id.show_result:
            return http.request.render(
                'openeducat_quiz.quiz_completed', {})
        return request.redirect('/exam/score/%s' % (result.id))

    @http.route('/quiz/rules/<model("op.quiz.result"):result>', type="http",
                auth="public", sitemap=False, website=True)
    def get_quiz_start(self, result, search='', **post):
        if search:
            for srch in search:
                exam = request.env['op.quiz'].sudo().search(
                    [('name', 'ilike', srch)])

        exam = result.quiz_id
        audio = False
        video = False
        html = False

        if exam.start_view == 'audio' and exam.quiz_audio:
            audio = '<audio controls controlsList="nodownload" \
            class="col-md-12"><source \
            src="data:audio/mp3;base64,%s"></audio>' % exam.quiz_audio
        elif exam.start_view == 'video' and exam.quiz_video:
            video = '<video controls controlsList="nodownload" \
            style="height: 450px;" class="col-md-12"><source \
            src="data:video/mp4;base64,%s"></video>' % exam.quiz_video
        elif exam.start_view == 'html':
            html = exam.quiz_html
        post.update({
            'audio': audio,
            'exam': exam,
            'video': video,
            'html': html,
            'result': result
        })
        single_page = 0
        if not result.quiz_id.single_que:
            single_page = 1
        post.update({'single_page': single_page})
        return http.request.render('openeducat_quiz.quiz_starting_page', post)

    # Submit the Single page single question form submition
    @http.route('/quiz/attempt/record', type="http", auth="public", sitemap=False,
                website=True)
    def quiz_result_attempt(self, **kwargs):
        if kwargs.get('question', False):
            result_line = request.env['op.quiz.result.line']
            line = result_line.sudo().browse(
                int(kwargs['question']))
            if 't_spent_time' in kwargs and kwargs['t_spent_time']:
                if line.result_id.quiz_id.time_config:
                    time_val = kwargs['t_spent_time'].split(':')
                    line.result_id.write({
                        'time_spent_hr': time_val[0],
                        'time_spent_minute': time_val[1],
                        'time_spent_second': time_val[2]
                    })
            if 'answer' in kwargs and kwargs['answer']:
                if line.que_type == 'optional':
                    answer = request.env[
                        'op.quiz.result.line.answers'].browse(
                        int(kwargs['answer']))
                    line.given_answer = answer.name
                    line.mark = answer.grade_id.value * line.question_mark / 100
                elif line.que_type == 'blank':
                    line.given_answer = str(kwargs['answer'])
                    if line.case_sensitive:
                        if line.answer == line.given_answer:
                            received_mark = (line.question_mark *
                                             (line.grade_true_id.value or 0.0)) / 100
                            line.mark = received_mark
                        else:
                            received_mark = (line.question_mark *
                                             (line.grade_false_id.value or 0.0)) / 100
                            line.mark = received_mark
                    else:
                        if line.answer.lower() == line.given_answer.lower():
                            received_mark = (line.question_mark *
                                             (line.grade_true_id.value or 0.0)) / 100
                            line.mark = received_mark
                        else:
                            received_mark = (line.question_mark *
                                             (line.grade_false_id.value or 0.0)) / 100
                            line.mark = received_mark
                elif line.que_type == 'descriptive':
                    line.given_answer = str(kwargs['answer'])
            line_val = line.result_id.get_prev_next_result(line.id)
            if line_val['next_result']:
                return request.redirect('/quiz/attempt/%s/question/%s?fullscreen=1' % (
                    line.result_id.id, int(line_val['next_result'])))
            else:
                quiz_ref = request.env['op.quiz']
                quiz_id = quiz_ref.sudo().browse(
                    int(kwargs['ExamID']))
                if quiz_id.manual:
                    line.result_id.write({
                        'state': 'submit',
                        'submit_date': datetime.today(),
                    })
                else:
                    line.result_id.write({
                        'state': 'asses',
                        'submit_date': datetime.today(),
                    })

                result_line.search_count(
                    [('result_id', '=', line.result_id.id),
                     ('que_type', '=', 'descriptive')])
                if not line.result_id.quiz_id.show_result:
                    return http.request.render(
                        'openeducat_quiz.quiz_completed', {})
                return request.redirect('/exam/score/%s' % (line.result_id.id))

    @http.route('/exam/score/<model("op.quiz.result"):result>', type='http',
                auth='user', website=True)
    def exam_final_result(self, result, **post):
        data = result.get_answer_data()
        return http.request.render(
            'openeducat_quiz.quiz_results', data)

    @http.route('/exam/result/<int:res_id>', type='http',
                auth='user', website=True)
    def exam_result(self, res_id):
        result = request.env['op.quiz.result'].sudo().search([
            ('state', '=', 'done'), ('id', '=', res_id)])
        return request.render('openeducat_quiz.exam_results', {
            'result': result})

    @http.route([
        '/quiz/attempt/<model("op.quiz.result"):result>',
        '/quiz/attempt/<model("op.quiz.result"):result>/question/<model(\
        "op.quiz.result.line"):line>',
        '/quiz/attempt/<model("op.quiz.result"):result>/question/<model(\
        "op.quiz.result.line"):line>/prev/<string:spent_time>',
        '/quiz/attempt/<model("op.quiz.result"):result>/question/<model(\
                "op.quiz.result.line"):line>/prev',
    ], type='http', auth='user', website=True)
    def render_quiz(self, result, line=False, spent_time=None, **post):
        if spent_time:
            time_val = spent_time.split(':')
            result.sudo().write({
                'time_spent_hr': time_val[0],
                'time_spent_minute': time_val[1],
                'time_spent_second': time_val[2]
            })
        post['exam'] = result.quiz_id
        next_allow = 0
        prev_allow = 0
        if line:
            result_val = result.get_prev_next_result(line.id)
            if result_val['next_result']:
                next_allow = 1
            if result_val['prev_result']:
                prev_allow = 1
            post.update({
                'next_result': result_val['next_result'],
                'prev_result': result_val['prev_result'],
                'question_no': result_val['question_no'],
                'next_allow': next_allow,
                'result': result,
                'line': line
            })
        else:
            for qline in result.line_ids:
                if qline.given_answer:
                    line = qline
            if line:
                result_val = result.get_prev_next_result(line.id)
                if result_val['next_result']:
                    next_allow = 1
                if result_val['prev_result']:
                    prev_allow = 1
                post.update({
                    'next_result': result_val['next_result'],
                    'prev_result': result_val['prev_result'],
                    'question_no': result_val['question_no'],
                    'next_allow': next_allow,
                    'result': result,
                    'line': line
                })
            else:
                prev_result = False
                next_result = False
                if not result.line_ids:
                    return True
                if len(result.line_ids) > 1:
                    next_result = request.env['op.quiz.result.line'].browse(
                        result.line_ids.ids[1])
                line = request.env['op.quiz.result.line'].browse(
                    result.line_ids.ids[0])
                if next_result:
                    next_allow = 1
                post.update({
                    'next_result': next_result,
                    'prev_result': prev_result,
                    'question_no': 1,
                    'next_allow': next_allow,
                    'result': result,
                    'line': line
                })
        given_answer_id = line.get_line_answer()
        post['given_answer'] = given_answer_id
        is_required = 0
        is_readonly = 0
        is_prev = 0
        if given_answer_id > 0:
            if line.result_id.quiz_id.prev_readonly:
                is_readonly = 1
        if line.result_id.quiz_id.que_required:
            is_required = 1
        if line.result_id.quiz_id.prev_allow and prev_allow:
            is_prev = 1
        if line.result_id.quiz_id.prev_readonly and line.given_answer:
            is_readonly = 1
        post.update({
            'is_required': is_required,
            'is_readonly': is_readonly,
            'prev_allow': is_prev,
            'grid_data': line.result_id.get_quiz_grid_data(line),
            'progress': line.result_id.get_progress_data()
        })
        time_hr = 0
        time_minute = 0
        time_spent_hr = 0
        time_spent_minute = 0
        time_spent_second = 0
        if result.quiz_id.time_config:
            time_hr = result.quiz_id.time_limit_hr or 0
            time_minute = result.quiz_id.time_limit_minute or 0
            if result.time_spent_hr:
                time_spent_hr = result.time_spent_hr or 0
            if result.time_spent_minute:
                time_spent_minute = result.time_spent_minute or 0
            if not time_spent_hr and not time_spent_minute:
                time_spent_hr = time_hr
                time_spent_minute = time_minute
            time_spent_second = result.time_spent_second or 0
        post.update({
            'time_hr': time_hr,
            'time_minute': time_minute
        })
        timer = 1 if time_hr or time_minute else 0
        post.update({
            'timer': timer,
            'time_spent_hr': time_spent_hr,
            'time_spent_minute': time_spent_minute,
            'time_spent_second': time_spent_second,
        })
        if post.get('fullscreen') == '1':
            return request.render("openeducat_quiz."
                                  "quiz_render_form_view_fullscreen", post)
        return request.render("openeducat_quiz.quiz_render_form_view", post)

    @http.route('/material/embed/<int:material_id>', type='http',
                auth='public', website=True)
    def materials_embed(self, material_id, page="1", **kw):
        try:
            template = 'openeducat_quiz.embed_material'
            material = request.env['op.quiz.line'].browse(material_id)
        except AccessError:
            template = 'openeducat_quiz.embed_material_forbidden'
            material = request.env['op.quiz.line'].sudo().browse(material_id)
        return request.render(template, {'material': material})

    @http.route('''/quiz/material/<model( \
                    "op.quiz.line", "[('datas', '!=', False), ( \
                    'material_type', '=', 'document')]"):material>/pdf_content''',
                type='http', auth="public", sitemap=False, website=True)
    def material_get_pdf_content(self, material):
        response = werkzeug.wrappers.Response()
        response.data = material.datas and base64.b64decode(
            material.datas) or b''
        response.mimetype = 'application/pdf'
        return response

    @http.route('/quiz/<model("op.quiz.result"):result>', type='http',
                auth='user', website=True)
    def quiz_render_question(self, result, **post):
        post.update({
            'exam': result.quiz_id,
            'result': result,
            'total_question': result.total_question
        })

        if post.get('fullscreen') == '1':
            if not result.quiz_id.single_que:
                return request.render("openeducat_quiz.quiz_web_page_fullscreen",
                                      post)
            return request.render(
                "openeducat_quiz.quiz_web_page_single_fullscreen", post)
        else:
            if not result.quiz_id.single_que:
                return request.render("openeducat_quiz.quiz_web_page", post)
            return request.render(
                "openeducat_quiz.quiz_web_page_single", post)

    @http.route('/quiz/results/<int:ExamID>', type="http", auth="public",
                sitemap=False, website=True)
    def quiz_result(self, ExamID, **kwargs):
        values = {
            'ExamID': ExamID
        }
        result = request.env['op.quiz.result'].sudo(). \
            browse(int(values['ExamID']))
        quiz = result.sudo().quiz_id
        value = self.get_quiz_result_data(values)
        if not quiz.show_result:
            return http.request.render('openeducat_quiz.quiz_completed', {})
        return http.request.render('openeducat_quiz.quiz_results', value)

    @http.route('/quiz/configuration', type="json", auth="user", website=True)
    def quiz_configuration(self, result_id, **kwargs):
        if result_id:
            try:
                result = request.env['op.quiz.result'].sudo().browse(int(result_id))
                quiz = result.quiz_id
                line_ids = result.quiz_id.line_ids
                types = []
                for line in line_ids:
                    types.append(line.que_type)
            except Exception:
                quiz = request.env['op.quiz'].browse(int(result_id))

            data = {
                'prev_allow': 1 if quiz.prev_allow else 0,
                'prev_readonly': 1 if quiz.prev_readonly else 0,
                'que_required': 1 if quiz.que_required else 0,
                'single_que': 1 if quiz.single_que else 0,
                'question_types': types,
            }
            return data
        return {}


class CustomerPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):
        """ Add sales documents to main account page """
        response = super(CustomerPortal, self).home(**kw)
        user = request.env['res.users'].browse(request.env.uid)
        quiz_count = request.env['op.quiz.result'].sudo().search_count(
            [('user_id', '=', user.id), ('state', '=', 'done')])
        response.qcontext.update({
            'quiz_count': quiz_count
        })
        return response
