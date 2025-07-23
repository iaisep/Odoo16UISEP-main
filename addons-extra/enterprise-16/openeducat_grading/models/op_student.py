# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


from odoo import _, models


class OpStudent(models.Model):
    _inherit = "op.student"

    def open_grade_book_grid(self):
        self.ensure_one()
        value = {
            'type': 'ir.actions.client',
            'name': _('GradeBook'),
            'tag': 'grade_book_grade_book_grid',
            'target': 'current',
            'params': {'grade_book': self.id},
            'domain': []
        }
        return value
