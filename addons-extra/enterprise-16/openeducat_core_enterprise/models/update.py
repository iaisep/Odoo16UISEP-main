# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


from odoo import api
from odoo.models import AbstractModel


class PublisherWarrantyContract(AbstractModel):
    _inherit = "publisher_warranty.contract"

    @api.model
    def _get_message_logs(self):

        res = super(PublisherWarrantyContract, self)._get_message_logs()
        IrParamSudo = self.env['ir.config_parameter'].sudo()
        openeducat_instance_key = IrParamSudo.get_param(
            'database.openeducat_instance_key')
        openeducat_instance_hash_key = IrParamSudo.get_param(
            'database.openeducat_instance_hash_key')
        openeducat_hash_validate_date = IrParamSudo.get_param(
            'database.hash_validated_date')
        openeducat_expiration_date = IrParamSudo.get_param(
            'database.openeducat_expire_date')

        res.update({
            "openeducat_hash_validate_date": openeducat_hash_validate_date,
            "enterprise_code": str(openeducat_instance_key
                                   ) + "," + str(openeducat_instance_hash_key),
            "openeducat_expire_date": openeducat_expiration_date,
        })
        return res
