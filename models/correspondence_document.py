
# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError

def _get_recipient_department_domain(self):
    """Devuelve un dominio para excluir el departamento del usuario actual."""
    # Esta restricción solo debe aplicarse al crear un nuevo documento,
    # no al visualizar registros existentes, para evitar conflictos con las reglas de seguridad.    
    domain = [('can_receive_correspondence', '=', True)]
    if self.env.context.get('form_view_ref') and self.env.user.employee_id.department_id:
        domain.append(('id', '!=', self.env.user.employee_id.department_id.id))
    
    return domain

class correspondence_document(models.Model):
    _name = 'correspondence_document'
    _description = 'Documento de Correspondencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('correlative_uniq', 'unique(correlative)', 'El correlativo del documento debe ser único. Ya existe un documento con este número.'),
    ]

    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)
    correlative = fields.Char(string='Correlativo', required=True, copy=False, default='Nuevo', readonly=True)
    name = fields.Char(string='Asunto', required=True)
    date = fields.Date(string='Fecha', default=fields.Date.context_today, required=True)
    author_id = fields.Many2one('res.users', string='Autor', default=lambda self: self.env.user, required=True, readonly=True)
    send_department_id = fields.Many2one('hr.department', string="Departamento Remitente", compute='_compute_send_department_id', store=True, readonly=False)
    correspondence_type = fields.Many2one('correspondence_type', string='Tipo de Correspondencia', required=True, readonly=True, states={'draft': [('readonly', False)]})
    recipient_department_ids = fields.Many2many('hr.department', string='Departamentos Destinatarios', required=True, domain=_get_recipient_department_domain)
    descripcion = fields.Html(string='Descripción', required=True)
    observaciones = fields.Text(string='Observaciones')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('signed', 'Firmado'),
        ('received', 'Recibido'),
        ('assigned', 'Asignado'),
        ('sent', 'Enviado (Interno)'),
        ('dispatched', 'Despachado (Externo)'),
        ('replied', 'Respondido'),
    ], string='Estado', default='draft', tracking=True)
    
    correspondence_flow = fields.Selection([
        ('internal', 'Interna'),
        ('incoming', 'Entrante (Externa recibida)'),
        ('outgoing', 'Saliente (Externa enviada)'),
    ], string="Flujo de Correspondencia", default='internal', required=True, index=True, tracking=True, readonly=True, states={'draft': [('readonly', False)], 'received': [('readonly', False)]})
    
    # Campo para vincular con la entidad externa (res.partner)
    external_partner_id = fields.Many2one('res.partner', string="Entidad Externa")
    # Campo relacionado para mostrar la dirección del partner, útil en los reportes.
    external_address = fields.Char(string="Dirección Externa", related='external_partner_id.contact_address', readonly=True)


    # Campo para correspondencia saliente
    shipping_method = fields.Selection([
        ('email', 'Correo Electrónico'),
        ('courier', 'Courier / Mensajería'),
        ('certified_mail', 'Correo Certificado'),
        ('in_person', 'Entrega en Persona'),
    ], string="Método de Envío")

    read_status_ids = fields.One2many('correspondence.document.read_status', 'document_id', string='Estados de Lectura')
    
    is_current_user_recipient = fields.Boolean(
        string="¿Usuario actual es destinatario?", compute='_compute_is_current_user_recipient')
    
    already_read_by_my_department = fields.Boolean(
        string="¿Ya leído por mi departamento?", compute='_compute_is_current_user_recipient')

    user_facing_state = fields.Char(
        string="Estado (Usuario)", compute='_compute_user_facing_state')

    public_url = fields.Char(
        string="URL Pública", compute='_compute_public_url', help="URL para la verificación pública del documento.")

    @api.depends('author_id', 'author_id.employee_id.department_id')
    def _compute_send_department_id(self):
        """
        Establece el departamento del autor como valor por defecto,
        pero permite que sea modificado.
        """
        for doc in self:
            doc.send_department_id = doc.author_id.employee_id.department_id

    @api.depends('recipient_department_ids', 'read_status_ids.department_id')
    def _compute_is_current_user_recipient(self):
        for doc in self:
            user_department = self.env.user.employee_id.department_id
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
            is_recipient = self.env.user.employee_id.department_id in doc.recipient_department_ids

            if doc.state == 'sent':
                if is_author:
                    doc.user_facing_state = _('Enviado')
                elif is_recipient:
                    doc.user_facing_state = _('Recibido')
                else:
                    doc.user_facing_state = _('En Gestión') # Fallback para otros usuarios (ej. admin)
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

    def action_assign(self):
        """Acción para correspondencia entrante. Cambia el estado a 'Asignado'."""
        self.ensure_one()
        if self.correspondence_flow != 'incoming':
            raise UserError(_("Esta acción solo es válida para correspondencia entrante."))
        self.write({'state': 'assigned'})

    def action_dispatch(self):
        """Acción para correspondencia saliente. Cambia el estado a 'Despachado'."""
        self.ensure_one()
        self.write({'state': 'dispatched'})

    def action_read(self):
        self.ensure_one()
        user_department = self.env.user.employee_id.department_id

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
        # Prepara el contexto base con valores por defecto para la respuesta
        ctx = {
            'default_parent_document_id': self.id,
            'default_name': f"Re: {self.correlative} - {self.name}",
            'default_correspondence_type': self.correspondence_type.id,
        }

        # Si estamos respondiendo a un documento ENTRANTE, la respuesta debe ser SALIENTE
        if self.correspondence_flow == 'incoming':
            ctx['default_correspondence_flow'] = 'outgoing'
            ctx['default_external_partner_id'] = self.external_partner_id.id
        # Si estamos respondiendo a un documento INTERNO, la respuesta sigue siendo INTERNA
        else:
            ctx['default_correspondence_flow'] = 'internal'
            ctx['default_recipient_department_ids'] = [(6, 0, self.send_department_id.ids)]

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
        # Determinar el estado inicial basado en el flujo
        if vals.get('correspondence_flow') == 'incoming':
            vals['state'] = 'received'
        else:
            vals.setdefault('state', 'draft')

        # Asignar correlativo temporal
        if 'correlative' not in vals:
            vals['correlative'] = _('Nuevo')

        new_document = super(correspondence_document, self).create(vals)

        # Generar correlativo final
        if new_document.correlative == _('Nuevo'):
            new_correlative = ''
            if new_document.correspondence_flow == 'incoming':
                # Usar una secuencia global para correspondencia entrante
                sequence = self.env['ir.sequence'].next_by_code('correspondence.incoming')
                new_correlative = f"ENT-{sequence}" if sequence else _('Error de Secuencia')

            elif new_document.correspondence_flow in ['internal', 'outgoing']:
                # Usar la lógica existente para interna y saliente
                department = new_document.send_department_id
                corr_type = new_document.correspondence_type

                if department and corr_type:
                    correlative_obj = self.env['correspondence.department.correlative'].search([
                        ('department_id', '=', department.id),
                        ('correspondence_type_id', '=', corr_type.id)
                    ], limit=1)

                    if not correlative_obj:
                        correlative_obj = self.env['correspondence.department.correlative'].create({
                            'department_id': department.id,
                            'correspondence_type_id': corr_type.id,
                            'last_sequence': 0
                        })

                    new_sequence = correlative_obj.last_sequence + 1
                    correlative_obj.last_sequence = new_sequence
                    year = fields.Date.today().strftime('%y')
                    new_correlative = f"{department.correlative_prefix or 'S-PRE'}-{corr_type.prefix or ''}-{year}-{str(new_sequence).zfill(4)}"

            if new_correlative:
                new_document.write({'correlative': new_correlative})

        # Si este nuevo documento es una respuesta a otro (tiene un padre)
        if new_document.parent_document_id:
            # Cambiamos el estado del documento padre a 'Respondido'
            new_document.parent_document_id.write({'state': 'replied'})

        return new_document

    def unlink(self):
        """
        Sobrescribe el método de eliminación para impedirla en todos los casos.
        Los documentos de correspondencia no se pueden eliminar para mantener la integridad de los correlativos y el historial.
        """
        raise UserError(_('Los documentos de correspondencia no pueden ser eliminados. Si es necesario, considere archivar o cancelar el documento en lugar de borrarlo.'))

    document_file = fields.Binary(string='Archivo', attachment=True, copy=False, help="El documento firmado y sellado.")
    file_name = fields.Char(string="Nombre de Archivo")

    extra_attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='correspondence_document_extra_attachment_rel',
        column1='document_id',
        column2='attachment_id',
        string="Archivos Adjuntos Adicionales"
    )

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
        user_department_id = self.env.user.employee_id.department_id.id
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
        user_department_id = self.env.user.employee_id.department_id.id
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
