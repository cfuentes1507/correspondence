
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

def _get_recipient_department_domain(self):
    """Devuelve un dominio para excluir el departamento del usuario actual."""
    # Esta restricción solo debe aplicarse al crear un nuevo documento,
    # no al visualizar registros existentes, para evitar conflictos con las reglas de seguridad.
    if self.env.context.get('form_view_ref') and self.env.user.department_id:
        return [('id', '!=', self.env.user.department_id.id)]
    return [] # Sin restricción al ver listas o registros existentes

class correspondence_document(models.Model):
    _name = 'correspondence_document'
    _description = 'Documento de Correspondencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    correlative = fields.Char(string='Correlativo', required=True, copy=False, default='Nuevo')
    name = fields.Char(string='Asunto', required=True)
    date = fields.Date(string='Fecha', default=fields.Date.context_today, required=True)
    author_id = fields.Many2one('res.users', string='Autor', default=lambda self: self.env.user, required=True, readonly=True)
    send_department_id = fields.Many2one(related='author_id.department_id', string="Departamento Remitente", store=True, readonly=True)
    correspondence_type = fields.Many2one('correspondence_type', string='Tipo de Correspondencia', required=True)
    recipient_department_ids = fields.Many2many('correspondence_department', string='Departamentos Destinatarios', required=True, domain=_get_recipient_department_domain)
    descripcion = fields.Text(string='Descripción', required=True)
    observaciones = fields.Text(string='Observaciones')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('signed', 'Firmado'),
        ('sent', 'Enviado'),
        ('read', 'Leído'),
        ('replied', 'Respondido')
    ], string='Estado', default='draft', tracking=True)
    
    is_recipient_user = fields.Boolean(
        string="Es usuario destinatario", compute='_compute_is_recipient_user')

    def _compute_is_recipient_user(self):
        for doc in self:
            # Comprueba si el departamento del usuario actual está en la lista de departamentos destinatarios
            doc.is_recipient_user = self.env.user.department_id in doc.recipient_department_ids

    def action_sign(self):
        self.write({'state': 'signed'})

    def action_send(self):
        self.write({'state': 'sent'})

    def action_read(self):
        self.write({'state': 'read'})
    
    def action_generate_report(self):
        return self.env.ref('correspondence.action_report_correspondence_document').report_action(self)

    def action_reply(self):
        self.ensure_one()
        # Prepara el contexto con valores por defecto para la respuesta
        ctx = {
            'default_parent_document_id': self.id,
            'default_recipient_department_ids': [(6, 0, self.send_department_id.ids)],
            'default_name': f"Re: {self.correlative} - {self.name}",
            'default_correspondence_type': self.correspondence_type.id,
        }
        return {
            'name': 'Responder Correspondencia',
            'type': 'ir.actions.act_window',
            'res_model': 'correspondence_document',
            'view_mode': 'form',
            'target': 'new',  # Abrir en una ventana emergente (pop-up)
            'context': ctx,
        }


    document_file = fields.Binary(string='Archivo', attachment=True, copy=False, help="El documento firmado y sellado.")
    file_name = fields.Char(string="Nombre de Archivo")

    def name_get(self):
        result = []
        for doc in self:
            name = f"{doc.correlative or 'Nuevo'} - {doc.name}"
            result.append((doc.id, name))
        return result

    parent_document_id = fields.Many2one('correspondence_document', string='En respuesta a')
    child_document_ids = fields.One2many('correspondence_document', 'parent_document_id', string='Respuestas')

    parent_author_id = fields.Many2one(
        'res.users',
        string="Respuesta a",
        related='parent_document_id.author_id',
        store=True)
