from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from collections import OrderedDict
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.tools import date_utils, groupby as groupbyelem
from operator import itemgetter
from odoo.addons.portal.controllers.mail import _message_post_helper
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.osv.expression import OR

import json
import base64

class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user = request.env.user
        Attachment = request.env['ir.attachment'].sudo()
        if 'documents_count' in counters:
            domain = []        
            domain += [('res_model', 'not in', ['ir.ui.view','ir.module.module'])]
            domain += [('public','=',True),('folder_id','!=',False)]
            documents_count = Attachment.sudo().search_count(domain) \
                if Attachment.sudo().check_access_rights('read', raise_exception=False) else 0
            values['documents_count'] = documents_count if documents_count else '0'
        return values
    
    @http.route(['/my/documents', '/my/documents/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_documents(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        Attachment = request.env['ir.attachment'].sudo()
        
        domain = [
            ('res_model', 'not in', ['ir.ui.view','ir.module.module']),
            ('public','=',True),('folder_id','!=',False)]        
        
        
        searchbar_sortings = {
            'date': {'label': _('Nuevo'), 'order': 'id desc'},
            'name': {'label': _('Nombre'), 'order': 'name asc, id asc'},
        }
        
        # default sortby order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Buscar en todo')},
            'name': {'input': 'name', 'label': _('Buscar en nombre')},
            'description': {'input': 'description', 'label': _('Buscar en descripción')},
            'folder_id': {'input': 'folder_id', 'label': _('Buscar en folder')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'folder_id': {'input': 'folder_id', 'label': _('Folder')},        
        }
        
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('description', 'all'):
                search_domain = OR([search_domain, [('description', 'ilike', search)]])            
            if search_in in ('folder_id', 'all'):
                search_domain = OR([search_domain, [('folder_id', 'ilike', search)]])
            domain += search_domain
    
        # count for pager
        documents_count = Attachment.search_count(domain)
        
        # default filter by value
        if not filterby:
            filterby = 'all'
        
        # make pager
        pager = portal_pager(
            url="/my/documents",
            url_args={'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in, 'search': search},
            total=documents_count,
            page=page,
            step=self._items_per_page
        )
        
        if groupby == 'folder_id':
            order = "folder_id, %s" % order
                
        # search the dcouemnts to display, according to the pager data
        documents = Attachment.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        
        if groupby == 'none':
            grouped_documents = []
            if documents:
                grouped_documents = [documents]
        else:
            grouped_documents = [Attachment.sudo().concat(*g) for k, g in groupbyelem(documents, itemgetter('folder_id'))]
        
        
        request.session['my_documents_history'] = documents.ids[:100]
        values.update({
            'documents': documents.sudo(),
            'grouped_documents': grouped_documents,
            'page_name': 'documents',
            'default_url': '/my/documents',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,                        
            'base_url': http.request.env["ir.config_parameter"].sudo().get_param("web.base.url"),
        })
        return request.render("isep_documents_portal.portal_my_documents", values)
        
    