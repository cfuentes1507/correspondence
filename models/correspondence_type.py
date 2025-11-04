
# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class correspondence_type(models.Model):
    _name = 'correspondence_type'
    _description = 'Tipos de Correspondencia'
    """Modelo para catalogar los diferentes tipos de correspondencia que se pueden generar.
    Ejemplos: Memorando, Circular, Oficio, etc."""

    name = fields.Char('Nombre')
    report_action_id = fields.Many2one(
        'ir.actions.report',
        string="Acción de Reporte",
        help="Seleccione la acción de reporte a utilizar para este tipo de correspondencia.")

    def action_preview_report(self):
        self.ensure_one()
        if not self.report_action_id:
            raise UserError(_("Por favor, seleccione una 'Acción de Reporte' antes de previsualizar."))

        # Para previsualizar, necesitamos un registro existente.
        # Buscamos el primer documento de correspondencia que encontremos.
        sample_document = self.env['correspondence_document'].search([], limit=1)

        if not sample_document:
            raise UserError(_(
                "No se encontraron documentos de correspondencia para generar una previsualización. "
                "Por favor, cree al menos un documento de ejemplo."
            ))

        # Usamos el documento de ejemplo para llamar a la acción de reporte.
        # Esto abrirá el reporte en una nueva pestaña o lo descargará.
        return self.report_action_id.report_action(sample_document)
