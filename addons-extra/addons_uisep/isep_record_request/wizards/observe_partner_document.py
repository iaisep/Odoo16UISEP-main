from odoo import fields, models

REASON_FOR_OBSERVATION_SELECTION = [
    ('incorrect_format', 'No está cargado en un formato correcto'),
    ('poor_readability', 'Legibilidad deficiente'),
    ('incorrect_document', 'Documento incorrecto'),
    ('incomplet_document', 'Documento incompleto'),
    ('certification_missing', 'Falta certificar ante notario público'),
    ('apostille_missing', 'Falta apostillar'),
    ('certification_apostille_missing', 'Falta certificar ante notario público y apostillar')
]


class ObservePartnerDocumentWizard(models.TransientModel):
    _name = 'observe.partner.document.wizard'
    _description = 'Asistente para observar un documento del contacto.'

    attachment_id = fields.Many2one(comodel_name='ir.attachment')
    reason_for_observation = fields.Selection(selection=REASON_FOR_OBSERVATION_SELECTION,
                                              string='Motivo de observación', required=True)

    def add_comment(self):
        '''
            Creates a record in mail.message with the comment added in the wizard.
            Modify the state of attachment to observed.
            :return: None
        '''
        partner_id = self.attachment_id.partner_id
        reason_for_observation = dict(self._fields['reason_for_observation'].selection)\
            .get(self.reason_for_observation, '')
        body = '''
            <p>Observación en adjunto: <strong>{}</strong></p>
            <p>Detalle:</p>
            <p class="text-danger"><strong>{}</strong></p>
        '''.format(self.attachment_id.document, reason_for_observation)
        self.env['mail.message'].create({
            'message_type': 'comment',
            'model': 'res.partner',
            'res_id': partner_id.id,
            'subject': partner_id.name,
            'subtype_id': self.env.ref('mail.mt_comment').id,
            'author_id': partner_id.id,
            'body': body
        })
        self.attachment_id.sudo().write({
            'state': 'observed',
            'reason_for_observation': self.reason_for_observation
        })
