
import logging
# from mailchimp3 import MailChimp
from odoo import api, fields, models, _
from odoo.models import expression
from odoo.exceptions import UserError, ValidationError
import multiprocessing as mp

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    user_id = fields.Many2one(domain='_domain_operating_users')
    is_untraceable = fields.Boolean(string='Ilocalizable', compute='_is_untraceable', store=True)


    domain='_domain_package_type'

    @api.model
    def _domain_operating_users(self):
        users = self.env['res.users'].with_context(active_test=False).search([('active_isep', '=', True)])




    @api.depends('call_ids','call_ids.state')
    def _is_untraceable(self):
        """
        pool = mp.Pool(mp.cpu_count())
        args = (rec for rec in self)
        pool.map_async(_finaluntraceable,args)
        pool.close()
        pool.join()
        """        
        for rec in self:
            flag = False
            if rec.call_ids:
                for call in rec.call_ids:
                    if call.state and call.state == 'done':
                        flag = True
                        break
                rec.is_untraceable = not flag
        """
    def _finaluntraceable(self,args):
        flag = False
        if args.call_ids:
            for call in args.call_ids:
                if call.state and call.state == 'done':
                    flag = True
                    break
            rec.is_untraceable = not flag
        """


