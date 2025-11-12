
# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError

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
    correlative = fields.Char(string='Correlativo', required=True, copy=False, default='Nuevo', readonly=True)
    name = fields.Char(string='Asunto', required=True)
    date = fields.Date(string='Fecha', default=fields.Date.context_today, required=True)
    author_id = fields.Many2one('res.users', string='Autor', default=lambda self: self.env.user, required=True, readonly=True)
    send_department_id = fields.Many2one(related='author_id.department_id', string="Departamento Remitente", store=True, readonly=True)
    correspondence_type = fields.Many2one('correspondence_type', string='Tipo de Correspondencia', required=True, readonly=True, states={'draft': [('readonly', False)]})
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

    public_url = fields.Char(
        string="URL Pública", compute='_compute_public_url', help="URL para la verificación pública del documento.")

    @api.depends('recipient_department_ids', 'read_status_ids.department_id')
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
        self.ensure_one()

        # 1. Obtener la acción de reporte
        report_action = self.correspondence_type.report_action_id
        if not report_action:
            report_action = self.env.ref('correspondence.action_report_correspondence_document', raise_if_not_found=False)
        
        if not report_action:
            raise UserError(_("No se ha definido una acción de reporte para este tipo de correspondencia ni una acción de fallback."))

        # 2. Generar el PDF
        pdf_content, _file_type = report_action._render_qweb_pdf(self.id)

        # 3. Construir el nombre del archivo
        file_name = f"{self.correlative}-{self.name}.pdf"

        # 4. Adjuntar el PDF y cambiar el estado
        self.write({
            'document_file': base64.b64encode(pdf_content),
            'file_name': file_name,
            'state': 'signed'
        })

        # 5. Recargar la vista para reflejar los cambios
        return {'type': 'ir.actions.client', 'tag': 'reload'}

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
        # Solución Definitiva: Asegurar que 'correspondence_type' esté en 'vals'.
        # Al responder, el tipo viene en el contexto pero no en vals. Lo añadimos explícitamente.
        if 'correspondence_type' not in vals and self.env.context.get('default_correspondence_type'):
            vals['correspondence_type'] = self.env.context.get('default_correspondence_type')

        # Paso 1: Crear el documento con un correlativo temporal.
        new_document = super(correspondence_document, self).create(vals)

        # Paso 2: Generar y escribir el correlativo final ahora que tenemos el registro completo.
        if new_document.correlative == 'Nuevo':
            # Forzamos una relectura del registro para asegurarnos de que todos los campos
            # relacionales (Many2one, related) estén cargados y no haya problemas de caché.
            doc = self.browse(new_document.id)

            department = doc.send_department_id
            corr_type = doc.correspondence_type

            if department and corr_type:
                corr_type_id = corr_type.id
                correlative_obj = self.env['correspondence.department.correlative'].search([
                    ('department_id', '=', department.id),
                    ('correspondence_type_id', '=', corr_type_id)
                ], limit=1)

                if not correlative_obj:
                    correlative_obj = self.env['correspondence.department.correlative'].create({
                        'department_id': department.id,
                        'correspondence_type_id': corr_type_id,
                        'last_sequence': 0
                    })

                new_sequence = correlative_obj.last_sequence + 1
                correlative_obj.last_sequence = new_sequence

                new_correlative = f"{department.correlative_prefix}-{corr_type.prefix or ''}-{fields.Date.today().strftime('%y')}-{new_sequence}"
                new_document.write({'correlative': new_correlative})

        # Si este nuevo documento es una respuesta a otro (tiene un padre)
        if new_document.parent_document_id:
            # Cambiamos el estado del documento padre a 'Respondido'
            new_document.parent_document_id.write({'state': 'replied'})

        return new_document

    def unlink(self):
        """
        Sobrescribe el método de eliminación para permitirla solo en estado 'borrador'.
        """
        for doc in self:
            if doc.state != 'draft':
                raise UserError(_('No se puede eliminar un documento de correspondencia que no esté en estado "Borrador".'))
        return super(correspondence_document, self).unlink()

    document_file = fields.Binary(string='Archivo', attachment=True, copy=False, help="El documento firmado y sellado.")
    file_name = fields.Char(string="Nombre de Archivo")

    def action_open_signed_document(self):
        """
        Genera una acción para descargar el documento firmado.
        Si no existe, abre el formulario como fallback.
        """
        self.ensure_one()
        if self.document_file:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{self._name}/{self.id}/document_file/{self.file_name}?download=true',
                'target': 'new',
            }
        # Si no hay archivo, informamos al usuario en lugar de abrir el formulario.
        raise UserError(_("Este documento no tiene un archivo firmado adjunto para descargar."))

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

    def _compute_public_url(self):
        """Genera la URL pública para el documento."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for doc in self:
            if doc.id:
                doc.public_url = f"{base_url}/correspondence/public/{doc.id}"
            else:
                doc.public_url = False

    @api.model
    def action_open_outbox(self):
        """
        Esta función es llamada por el menú 'Bandeja de Salida'.
        Construye y devuelve una acción de ventana con un dominio dinámico
        que filtra los documentos por el departamento del usuario actual.
        """
        user_department_id = self.env.user.department_id.id
        if not user_department_id:
            raise UserError(_("Tu usuario no tiene un departamento asignado. Por favor, contacta a un administrador."))

        action = self.env['ir.actions.act_window']._for_xml_id('correspondence.action_correspondence_document_tree')
        action['display_name'] = _('Bandeja de Salida')
        action['name'] = _('Bandeja de Salida')
        action['domain'] = [('send_department_id', '=', user_department_id)]
        action['context'] = {} # Limpiamos el contexto para evitar filtros no deseados
        return action

    @api.model
    def action_open_archive(self):
        """
        Esta función es llamada por el menú 'Archivo'.
        Construye y devuelve una acción de ventana con un dominio dinámico
        que filtra los documentos enviados o recibidos por el departamento del usuario.
        """
        user_department_id = self.env.user.department_id.id
        if not user_department_id:
            raise UserError(_("Tu usuario no tiene un departamento asignado. Por favor, contacta a un administrador."))

        action = self.env['ir.actions.act_window']._for_xml_id('correspondence.action_correspondence_document_archive_base')
        
        # Construimos el dominio para mostrar documentos enviados O recibidos por el departamento del usuario
        domain = [
            '|',
                ('send_department_id', '=', user_department_id),
                ('recipient_department_ids', 'in', [user_department_id])
        ]
        action['domain'] = domain
        return action
