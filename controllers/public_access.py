# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CorrespondencePublicAccess(http.Controller):

    @http.route('/correspondence/public/<int:doc_id>', type='http', auth='public', website=True)
    def public_correspondence_view(self, doc_id, **kw):
        """
        Proporciona una página web pública para ver los detalles de un documento de correspondencia.
        """
        # Usamos sudo() para saltar las reglas de acceso para el usuario público.
        document = request.env['correspondence_document'].sudo().browse(doc_id)
        
        if not document.exists():
            return request.render('website.404')

        # Preparamos los valores para la plantilla.
        values = {
            'doc': document,
        }
        
        # Renderizamos la plantilla pública.
        return request.render('correspondence.public_correspondence_template', values)