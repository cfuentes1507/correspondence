# -*- coding: utf-8 -*-

import os
import re
from odoo import models, fields


class UploadScannedDocumentWizard(models.TransientModel):
    _name = 'correspondence.upload.scanned.document.wizard'
    _description = 'Asistente para Subir Documento Escaneado'

    scanned_file = fields.Binary(string="Documento Escaneado", required=True)
    file_name = fields.Char(string="Nombre del Archivo", required=True)

    def upload_scanned(self):
        """Sube el documento escaneado al registro de correspondencia entrante."""
        self.ensure_one()
        doc_id = self.env.context.get('active_id')
        document = self.env['correspondence_document'].browse(doc_id)

        if document:
            # Obtener la extensión del archivo original.
            _name, extension = os.path.splitext(self.file_name)

            # Sanitizar el asunto para generar un nombre de archivo válido.
            sanitized_subject = re.sub(r'[\\/*?:"<>|]', "", document.name)

            # Construir el nombre de archivo usando el correlativo y el asunto.
            new_file_name = f"{document.correlative} - {sanitized_subject}{extension}"

            document.write({
                'document_file': self.scanned_file,
                'file_name': new_file_name,
            })
        return {'type': 'ir.actions.act_window_close'}
