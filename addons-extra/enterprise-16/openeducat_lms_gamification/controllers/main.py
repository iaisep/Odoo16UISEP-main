# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_lms.controllers.main import OpenEduCatLms
from odoo.addons.portal.controllers.portal import CustomerPortal

PPG = 12  # Products Per Page
PPR = 4  # Products Per Row


class GamificationOpenEduCatLms(OpenEduCatLms):

    @http.route()
    def courses(self, search='', category=False, page=0, ppg=False,
                level=False, **post):
        res = super(GamificationOpenEduCatLms, self).courses(search=search,
                                                             category=category,
                                                             page=page, ppg=ppg,
                                                             level=level, **post)
        achievements = request.env['gamification.badge.user'].sudo().search(
            [('badge_id.is_published', '=', True)], limit=5)
        users = request.env['res.users'].sudo().search([
            ('karma', '>', 0),
            ('website_published', '=', True)], limit=5, order='karma desc')
        rr = request.render('openeducat_lms_gamification.my_challenges')

        res.qcontext.update({
            'rr': rr,
            'achievements': achievements,
            'users': users,
            'top3_users': self._get_top3_users()
        })
        return res

    def _get_top3_users(self):
        return request.env['res.users'].sudo().search_read([
            ('karma', '>', 0),
            ('website_published', '=', True),
            ('image_1920', '!=', False)], ['id'], limit=3, order='karma desc')

    @http.route()
    def enroll_course(self, course, **kwargs):
        r = super(GamificationOpenEduCatLms, self).enroll_course(
            course, **kwargs)
        course._action_set_course_done()
        for challenge in course.challenge_ids:

            current_challenge_users = challenge.user_ids.ids
            if request.env.uid not in current_challenge_users:
                current_challenge_users.append(request.env.uid)
                challenge.sudo().user_ids = [(6, 0, current_challenge_users)]
            challenge.sudo().action_start()
        return r

    @http.route()
    def get_course_material(self, course, section=None, material=None,
                            result=None, next_mat=None, **kwargs):
        r = super(GamificationOpenEduCatLms, self).get_course_material(
            course, section, material, result, next_mat, **kwargs)
        for challenge in course.challenge_ids:
            request.env['gamification.goal'].sudo().search(
                [('challenge_id', '=', challenge.id),
                 ('user_id', '=', request.env.uid),
                 ('state', '!=', 'reached')]).sudo().update_goal()
            challenge.sudo()._check_challenge_reward()
        reward = request.render('openeducat_lms_gamification.reward_point_view')
        r.qcontext.update({'reward': reward})
        reward_material = request.env['op.material'].sudo().search([
            ('material_type', '=', 'quiz')])

        if result:
            reward_material._action_set_quiz_material_done()
        return r

    @http.route(['/my/badges'], type='http', auth='public', website=True)
    def my_lms_badges(self, **post):
        badge_ids = request.env['gamification.badge.user'].search(
            [('user_id', '=', request.env.uid)])
        data = {'user': request.env.user}
        data['badge_ids'] = [x.badge_id for x in badge_ids]
        return request.render("openeducat_lms_gamification.my_badges", data)


class CustomerPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):
        """ Add sales documents to main account page """
        response = super(CustomerPortal, self).home(**kw)
        badge_count = request.env[
            'gamification.badge.user'].sudo().search_count(
            [('user_id', '=', request.env.uid)])
        response.qcontext.update({
            'badge_count': badge_count
        })
        return response
