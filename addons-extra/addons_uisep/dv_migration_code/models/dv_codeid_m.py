# -*- coding: utf-8 -*-
# Modelos para seguimiento de ID
from odoo import fields, models

class ResCompany(models.Model):
    _inherit="res.company"
    m_code= fields.Integer(string="ID origen", help="Este codigo parsarlo por medio de import y export en companias")

class ResPartner(models.Model):
    _inherit="res.partner"
    m_code= fields.Integer(string="ID origen")

class CrmLead(models.Model):
    _inherit="crm.lead"
    m_code= fields.Integer(string="ID origen")

class SaleOrder(models.Model):
    _inherit="sale.order"
    m_code= fields.Integer(string="ID origen")

class SaleOrder(models.Model):
    _inherit="product.template"
    m_code= fields.Integer(string="ID origen")
