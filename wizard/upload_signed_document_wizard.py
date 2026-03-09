# -*- coding: utf-8 -*-

import os
import re
from odoo import models, fields

class UploadSignedDocumentWizard(models.TransientModel):
    _name = 'correspondence.upload.signed.document.wizard'
    _description = 'Asistente para Subir Documento Firmado'

    signed_file = fields.Binary(string="Documento Firmado", required=True)
    file_name = fields.Char(string="Nombre del Archivo", required=True)

    def upload_and_sign(self):
        self.ensure_one()
        doc_id = self.env.context.get('active_id')
        document = self.env['correspondence_document'].browse(doc_id)
        
        if document:
            # Obtener la extensión del archivo original.
            _name, extension = os.path.splitext(self.file_name)

            # Sanitizar el asunto para que sea un nombre de archivo válido.
            sanitized_subject = re.sub(r'[\\/*?:"<>|]', "", document.name)

            # Construir el nuevo nombre de archivo usando el correlativo y el asunto.
            new_file_name = f"{document.correlative} - {sanitized_subject}{extension}"

            # SNAPSHOT: Guardamos los nombres de los departamentos para persistencia histórica,
            # igual que en el flujo de firma digital (action_sign).
            static_send = document.send_department_id.name
            static_recipients = ", ".join(document.recipient_department_ids.mapped('name'))

            document.write({
                'document_file': self.signed_file,
                'file_name': new_file_name,
                'state': 'signed',
                'send_department_static': static_send,
                'recipient_departments_static': static_recipients,
            })
        return {'type': 'ir.actions.act_window_close'}
