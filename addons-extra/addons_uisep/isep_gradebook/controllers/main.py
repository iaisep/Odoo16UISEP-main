import base64
import logging

import werkzeug

import odoo.http as http
from odoo.http import request
from odoo.tools import plaintext2html
from odoo import _, api, fields, models, tools
from odoo.addons.website_profile.controllers.main import WebsiteProfile
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from operator import itemgetter
from collections import defaultdict
from odoo.tools.misc import OrderedSet, format_date, groupby as tools_groupby
from odoo.exceptions import UserError
import json



_logger = logging.getLogger(__name__)


class WebsitePortalGradebook(WebsiteProfile):
    """Display current user gradebook"""


    def _survey_user_input_get_groupby_mapping(self):
        return {
            "Asignatura": "slide_id.channel_id.name",
        }
      

    @http.route(["/campus/gradebook"], type="http", auth="user", website=True)
    def portal_my_gradebook(self, sortby=None, search="", search_in="All", groupby='none', **post):
        """Display current user gradebook"""

        if not groupby:
            groupby = 'none'
        searchbar_sortings = {
            "struct_id": {"label": "name", "order": "name desc"}
        }
        searchbar_inputs = {
            "All": {
                "label": "All",
                "input": "All",
                "domain": [
                    ("survey_id", "ilike", search),
                ],
            },
            "Name": {
                "label": "Name",
                "input": "Name",
                "domain": [("survey_id", "ilike", search)],
            },
        }

        groupby_list = {
            "course_id": {
                "input": "course_id",
                "label": "Programa",
                "order": 1,
            },
            "op_subject_id": {
                "input": "op_subject_id",
                "label": "Asignatura",
                "order": 2,
            },

        }
        if not sortby:
            sortby = "struct_id"
        search_domain = searchbar_inputs[search_in]["domain"]
        partner_id = request.env.user.partner_id

        admission_ids =  False
        admission_ids = request.env['op.admission'].sudo().search([('state','=','done'),('partner_id','=', partner_id.id)])

        gradebook = request.env['app.gradebook.student'].sudo().search([('partner_id','=',partner_id.id), ('admission_id','in', admission_ids.ids) ])
        

        user_id = request.env.user.id
        user = self._check_user_profile_access(user_id)
        values = self._prepare_user_values(**post)
        params = self._prepare_user_profile_parameters(**post)
        values.update(self._prepare_user_profile_values(user, **params))


        values.update({
                "gradebook_ids": gradebook,
                "searchbar_sortings": searchbar_sortings,
                "searchbar_inputs": searchbar_inputs,
                "sortby": sortby,
                "search": search,
                "search_in": search_in,
                "page_name": "gradebook",
                'group_by': groupby,
            })
        
        return http.request.render( "isep_gradebook.portal_my_gradebook",values)

    