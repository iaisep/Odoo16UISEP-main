from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
class CustomCrmBand(models.Model):

    _inherit = 'crm.lead'
    #si la bandera esta el false se crea el lead en mautic 
    mautic_export=fields.Boolean('Mautic export', default=False)
    #si la bandera esta en true se actualiza el lead en mautic
    mautic_update=fields.Boolean('Mautic actualizado', default=False)
    
    def write(self, vals):
        vals['mautic_update']=True
        res=super(CustomCrmBand, self).write(vals)
        return res






    

