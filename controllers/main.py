# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CorrespondencePublicController(http.Controller):

    @http.route('/correspondence/public/<int:doc_id>', type='http', auth='public', website=True, sitemap=False)
    def public_correspondence_view(self, doc_id, **kwargs):
        """
        Renders a public web page for a correspondence document.
        """
        document = request.env['correspondence_document'].sudo().browse(doc_id)
        if not document.exists():
            return request.not_found()

        return request.render('correspondence.public_correspondence_template', {'doc': document})