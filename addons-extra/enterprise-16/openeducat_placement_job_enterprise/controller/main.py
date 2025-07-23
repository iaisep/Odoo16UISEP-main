# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_job_enterprise.controller.main import OnlineJob


class WebsitePlacementOffer(http.Controller):

    @http.route('/activity/announcement/detail/<int:activity_id>',
                type='http', auth='public', website=True)
    def Activity_detail(self, activity_id, **kwargs):

        activity = request.env["op.activity.announcement"].sudo().search(
            [('id', '=', activity_id)])
        return http.request.render('openeducat_placement_job_enterprise.'
                                   'activity_detail',
                                   {'activity': activity})

    @http.route(
        '/activity/announcement/apply/<model("op.activity.announcement"):'
        'activity>',
        type='http', auth="public", sitemap=False, website=True)
    def Activity_apply(self, activity, **kwargs):
        return request.render("openeducat_placement_job_enterprise."
                              "activity_apply",
                              {
                                  'activity': activity,
                              })

    @http.route(
        '/website/activity/announcement',
        type='http', auth="public", sitemap=False, website=True)
    def Web_activity_detail(self, **kwargs):

        activity = request.env['op.activity.announcement'].sudo().search([])
        return request.render("openeducat_placement_job_enterprise."
                              "website_announcement",
                              {
                                  'activity': activity,
                              })


class ActivityAnnouncementController(OnlineJob):
    @http.route(
        '/job/post/apply/<model("op.activity.announcement"):'
        'activity>/<model("op.job.post"):'
        'job_post_id>', type='http', auth="user", website=True)
    def activity_apply(self, activity, job_post_id, **kwargs):
        return request.render("openeducat_placement_job_enterprise."
                              "job_post_apply",
                              {
                                  'activity': activity,
                                  'job_post_id': job_post_id,
                              })
