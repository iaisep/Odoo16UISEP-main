# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


from odoo import fields, models


class MsOpCourse(models.Model):

    _inherit = 'op.course'

    webhook_url = fields.Char(string="Webhook URL")


class MsOpSubject(models.Model):

    _inherit = 'op.subject'

    webhook_url = fields.Char(string="Webhook URL")
