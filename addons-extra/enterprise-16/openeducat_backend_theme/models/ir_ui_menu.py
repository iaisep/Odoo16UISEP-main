# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import base64

from odoo import api, models, tools
from odoo.tools.mimetypes import guess_mimetype


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def load_web_menus(self, debug):
        res = super(IrUiMenu, self).load_web_menus(debug=debug)
        menus = self.load_menus(debug)
        for menu in menus.values():
            if res.get(menu['id']):
                res.get(menu['id']).update({
                    "parentId": menu['parent_id'][0] if menu['parent_id'] else False,
                })
        return res

    @api.model
    @tools.ormcache_context('self._uid', keys=('lang',))
    def load_menus_root(self):
        res = super(IrUiMenu, self).load_menus_root()
        for menu in res.get('children'):
            if menu.get('web_icon_data'):
                menu['mimetype'] = guess_mimetype(
                    base64.b64decode(menu['web_icon_data']))
        return res

    @api.model
    @tools.ormcache_context('self._uid', 'debug', keys=('lang',))
    def load_menus(self, debug):
        res = super(IrUiMenu, self).load_menus(debug)
        for menu_key, menu_val in res.items():
            if menu_key != 'root':
                if menu_val.get('web_icon_data'):
                    menu_val['mimetype'] = guess_mimetype(
                        base64.b64decode(
                            menu_val['web_icon_data']))
        return res
