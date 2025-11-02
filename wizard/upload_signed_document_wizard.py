# -*- coding: utf-8 -*-

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
            document.write({
                'document_file': self.signed_file,
                'file_name': self.file_name,
                'state': 'signed'
            })
        return {'type': 'ir.actions.act_window_close'}
