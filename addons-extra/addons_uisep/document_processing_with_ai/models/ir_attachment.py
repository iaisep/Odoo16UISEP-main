from odoo import models, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    _description = ("Extended to include automated document processing. Triggers AI-powered analysis upon file "
                    "creation or modification.")

    @api.model
    def create(self, vals):
        """
        Sobrescribimos el método create para analizar el documento
        después de que se cree un nuevo archivo.
        """
        attachment = super(IrAttachment, self).create(vals)
        attachment._process_document()
        return attachment

    def write(self, vals):
        """
        Sobrescribimos el método write para analizar el documento
        si el campo 'datas' o cualquier otro relevante se modifica.
        """
        result = super(IrAttachment, self).write(vals)
        if 'datas' in vals:  # Verificar si el campo 'datas' fue actualizado
            self._process_document()
        return result

    def _process_document(self):
        """
        Método privado para analizar el documento con la lógica proporcionada.
        """
        for file in self:
            try:
                # Buscar el partner relacionado
                partner = self.env['res.partner'].search([('ir_attachment_ids', 'in', [file.id])], limit=1)

                # Validar condiciones antes de procesar el archivo
                if partner and (file.state == 'on_hold'):
                    if file.mimetype == 'application/pdf':
                        self.env['document_processing_ai']._escribir_log("-" * 50)
                        self.env['document_processing_ai']._escribir_log(f"{file.name}")
                        self.env['document_processing_ai'].main__(file)
                    elif file.mimetype != 'application/octet-stream':
                        self.env['document_processing_ai'].add_comment(file, 'incorrect_format')
                else:
                    pass

            except:
                self.env['document_processing_ai'].add_comment(file, 'incorrect_format')
