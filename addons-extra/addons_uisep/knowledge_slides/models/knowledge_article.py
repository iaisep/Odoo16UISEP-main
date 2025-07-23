# knowledge_article_extension.py
from odoo import models, fields

class KnowledgeArticle(models.Model):
    _inherit = 'knowledge.article'

    generated_from_content = fields.Boolean(string="Generated from Knowledge Content", default=False)
    generated_from_content_root = fields.Boolean(string="root", default=False)