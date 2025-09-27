
# -*- coding: utf-8 -*-

from odoo import models, fields


class correspondence_document(models.Model):
    _name = 'correspondence_document'
    _description = 'Documento de Correspondencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    correlative = fields.Char(string='Correlativo', required=True, copy=False, default='Nuevo')
    name = fields.Char(string='Asunto', required=True)
    date = fields.Date(string='Fecha', default=fields.Date.context_today, required=True)
    author_id = fields.Many2one('res.users', string='Autor', default=lambda self: self.env.user, required=True, readonly=True)
    tipo = fields.Many2one('correspondence_type', string='Tipo de Correspondencia', required=True)
    recipient_department_id = fields.Many2one('correspondence_department', string='Departamento Destinatario', required=True)
    descripcion = fields.Text(string='Descripción')
    observaciones = fields.Text(string='Observaciones')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('signed', 'Firmado'),
        ('sent', 'Enviado'),
        ('read', 'Leído'),
        ('replied', 'Respondido')
    ], string='Estado', default='draft')
    
    document_file = fields.Binary(string='Archivo', attachment=True, copy=False, help="El documento firmado y sellado.")
    file_name = fields.Char(string="Nombre de Archivo")
    
    parent_document_id = fields.Many2one('correspondence_document', string='Documento Padre')
    child_document_ids = fields.One2many('correspondence_document', 'parent_document_id', string='Respuestas')


