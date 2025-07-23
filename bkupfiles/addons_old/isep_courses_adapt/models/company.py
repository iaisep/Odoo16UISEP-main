# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
import json
import requests


class ResCompany(models.Model):
    _inherit = "res.company"

    access_token = fields.Char(string="Access Token")
    request_url = fields.Char(string="Request URL")

    def get_credential(self):
        moodle_id=False
        if len(self)==1:
            moodle_id=self.env['moodle.credential'].search([('company_ids','=',self.id)])
        else:
            raise UserError("Revise la compiña que requiere consultar")
        if len(moodle_id)>1:
            raise UserError( "Revise que su compañia este registrado en una sola instancia de moodle")
        elif not moodle_id:
            raise UserError("No se ha definido una instancia de moodle para la compañia %s"%(self.name))
        return moodle_id