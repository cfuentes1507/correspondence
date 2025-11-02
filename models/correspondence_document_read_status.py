# -*- coding: utf-8 -*-

from odoo import models, fields

class CorrespondenceDocumentReadStatus(models.Model):
    _name = 'correspondence.document.read_status'
    _description = 'Estado de Lectura de Documento por Departamento'
    _rec_name = 'department_id'

    document_id = fields.Many2one('correspondence_document', string='Documento', required=True, ondelete='cascade')
    department_id = fields.Many2one('correspondence_department', string='Departamento', required=True)
    read_by_user_id = fields.Many2one('res.users', string='Leído por', required=True)
    read_date = fields.Datetime(string='Fecha de Lectura', default=fields.Datetime.now, required=True)

    _sql_constraints = [
        ('document_department_uniq', 'unique(document_id, department_id)', 'Un departamento solo puede marcar como leído un documento una vez.')
    ]