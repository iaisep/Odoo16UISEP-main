import base64

from odoo import _, http
from odoo.exceptions import UserError
from odoo.http import request


class WebData(http.Controller):
    @http.route('/quiz/config', type='json', auth='user', website=True)
    def anti_cheating(self, result_id, **kwargs):
        screenshot = 0
        if result_id:
            try:
                result = request.env['op.quiz.result'].sudo().browse(int(result_id))
                quiz = result.sudo().quiz_id
                if quiz.take_screenshot == 'random':
                    screenshot = 0
                elif quiz.take_screenshot == 'time_interval':
                    screenshot = 1

            except Exception:
                quiz = request.env['op.quiz'].sudo().browse(int(result_id))
                if quiz.take_screenshot == 'random':
                    screenshot = 0
                elif quiz.take_screenshot == 'time_interval':
                    screenshot = 1
            data = {
                'face_tracking': 1 if quiz.face_tracking else 0,
                'copy_paste_allow': 1 if quiz.copy_paste_allow else 0,
                'take_screenshot': screenshot,
                'question_count': len(quiz.line_ids),
                'question_time_out': quiz.question_time_out,
                'warning_limit': quiz.warning_limit,
                'warning_state': quiz.warning_state,
                'sensitivity': quiz.face_sensitivity,
                'random_start': quiz.random_start,
                'random_end': quiz.random_end,
                'result_warning_state': quiz.state,
                'particular_interval': quiz.particular_interval,
            }
            return data
        return {}

    @http.route(['/check/state'],
                type='json', auth="user", website=True)
    def check_state(self, result_id):
        result = request.env['op.quiz.result'].sudo().browse(int(result_id))
        if result.state == 'hold':
            return {'state': result.state}
        else:
            return False

    @http.route(['/quiz/hold'], type='http',
                auth='public', website=True)
    def cancel(self):
        return http.request.render('openeducat_quiz_anti_cheating.quiz_hold')

    @http.route(['/create/attachment'],
                type='json', auth="user", website=True)
    def create_attachment(self, file, file_name, name, exam):
        res = bytes(file, 'utf-8')
        converted_string = base64.decodebytes(res)
        request.env['ir.attachment'].sudo().create({
            'name': file_name,
            'type': 'binary',
            'datas': converted_string,
            'res_model': 'op.quiz.result',
            'res_id': exam
        })
        return True

    @http.route(['/warning/quite'],
                type='json', auth="user", website=True)
    def warning_quite(self, result_id, warning_state):
        result = request.env['op.quiz.result'].sudo().browse(int(result_id))
        for res in result:
            res.state = warning_state
        return True

    @http.route(['/camera/access'],
                type='json', auth="user", website=True)
    def camera_access(self):
        raise UserError(_('Camera access required.'))

    @http.route(['/warning/line'],
                type='json', auth="user", website=True)
    def create_warning_line(self, warning_no, w_name, result_id, time, file):
        request.env['op.quiz.result.warning'].sudo().create({
            'result_id': result_id,
            'warning_no': warning_no,
            'warning_name': w_name,
            'time': time,
            'warning_attachment': file,
        })

        return True
