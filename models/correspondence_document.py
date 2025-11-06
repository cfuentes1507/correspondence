
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

    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)
    correlative = fields.Char(string='Correlativo', required=True, copy=False, default='Nuevo')
    name = fields.Char(string='Asunto', required=True)
    date = fields.Date(string='Fecha', default=fields.Date.context_today, required=True)
    author_id = fields.Many2one('res.users', string='Autor', default=lambda self: self.env.user, required=True, readonly=True)
    send_department_id = fields.Many2one(related='author_id.department_id', string="Departamento Remitente", store=True, readonly=True)
    correspondence_type = fields.Many2one('correspondence_type', string='Tipo de Correspondencia', required=True)
    recipient_department_ids = fields.Many2many('correspondence_department', string='Departamentos Destinatarios', required=True, domain=_get_recipient_department_domain)
    descripcion = fields.Html(string='Descripción', required=True)
    observaciones = fields.Text(string='Observaciones')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('signed', 'Firmado'),
        ('sent', 'Enviado'),
        ('replied', 'Respondido')
    ], string='Estado', default='draft', tracking=True)
    
    read_status_ids = fields.One2many('correspondence.document.read_status', 'document_id', string='Estados de Lectura')
    
    is_current_user_recipient = fields.Boolean(
        string="¿Usuario actual es destinatario?", compute='_compute_is_current_user_recipient')
    
    already_read_by_my_department = fields.Boolean(
        string="¿Ya leído por mi departamento?", compute='_compute_is_current_user_recipient')

    user_facing_state = fields.Char(
        string="Estado (Usuario)", compute='_compute_user_facing_state')

    def _compute_is_current_user_recipient(self):
        for doc in self:
            user_department = self.env.user.department_id
            doc.is_current_user_recipient = user_department in doc.recipient_department_ids
            doc.already_read_by_my_department = user_department in doc.read_status_ids.mapped('department_id')

    @api.depends('state', 'author_id', 'recipient_department_ids')
    def _compute_user_facing_state(self):
        """
        Calcula la etiqueta del estado que se mostrará al usuario actual
        dependiendo de si es el autor o un destinatario.
        """
        for doc in self:
            is_author = doc.author_id == self.env.user
            is_recipient = self.env.user.department_id in doc.recipient_department_ids

            if doc.state == 'sent':
                if is_author:
                    doc.user_facing_state = _('Enviado')
                elif is_recipient:
                    doc.user_facing_state = _('Recibido')
                else:
                    doc.user_facing_state = _('Enviado') # Fallback para otros usuarios (ej. admin)
            else:
                doc.user_facing_state = doc.get_state_display_name()

    def action_sign(self):
        return {
            'name': _('Subir Documento Firmado'),
            'type': 'ir.actions.act_window',
            'res_model': 'correspondence.upload.signed.document.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_active_id': self.id,
            }
        }

    def action_send(self):
        self.write({'state': 'sent'})

    def action_read(self):
        self.ensure_one()
        user_department = self.env.user.department_id

        # Validación de seguridad: Solo los usuarios de un departamento destinatario pueden marcar como leído.
        if not user_department or user_department not in self.recipient_department_ids:
            raise models.ValidationError(_("Solo los usuarios de un departamento destinatario pueden marcar este documento como leído."))

        self.env['correspondence.document.read_status'].create({
            'document_id': self.id,
            'department_id': user_department.id,
            'read_by_user_id': self.env.user.id,
        })

        # Devolver una acción para recargar la vista y reevaluar los attrs de los botones.
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def action_generate_report(self):
        self.ensure_one()
        # Usar la acción de reporte definida en el tipo de correspondencia.
        # Si no hay ninguna, usar una acción de fallback genérica.
        report_action = self.correspondence_type.report_action_id
        if not report_action:
            # Usamos la acción genérica como fallback
            report_action = self.env.ref('correspondence.action_report_correspondence_document')

        return report_action.report_action(self)

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
            'target': 'current',  # Abrir en la ventana principal
            'context': ctx,
        }

    @api.model
    def create(self, vals):
        # Primero, creamos el nuevo documento de correspondencia
        new_document = super(correspondence_document, self).create(vals)

        # Si este nuevo documento es una respuesta a otro (tiene un padre)
        if new_document.parent_document_id:
            # Cambiamos el estado del documento padre a 'Respondido'
            new_document.parent_document_id.write({'state': 'replied'})

        return new_document

    document_file = fields.Binary(string='Archivo', attachment=True, copy=False, help="El documento firmado y sellado.")
    file_name = fields.Char(string="Nombre de Archivo")

    def name_get(self):
        result = []
        for doc in self:
            name = f"{doc.correlative or 'Nuevo'} - {doc.name}"
            result.append((doc.id, name))
        return result

    def get_state_display_name(self):
        """Método auxiliar para obtener el nombre legible de un campo de selección."""
        self.ensure_one()
        # Obtiene la lista de tuplas (valor, etiqueta) del campo 'state'
        selection_list = self._fields['state'].selection
        # Devuelve la etiqueta que corresponde al valor actual del estado
        return dict(selection_list).get(self.state)

    parent_document_id = fields.Many2one('correspondence_document', string='En respuesta a')
    child_document_ids = fields.One2many('correspondence_document', 'parent_document_id', string='Respuestas')

    parent_author_id = fields.Many2one(
        'res.users',
        string="Respuesta a",
        related='parent_document_id.author_id',
        store=True)
