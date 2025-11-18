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

    @http.route('/correspondence/download/attachment/<int:attachment_id>', type='http', auth='public', website=True)
    def download_attachment(self, attachment_id, **kwargs):
        """
        Handles attachment download requests.
        - If the user is public, shows an access denied page.
        - If the user is logged in, redirects to the actual download URL.
        """
        # Check if the user is the public user (not logged in)
        if request.env.user.id == request.env.ref('base.public_user').id:
            return request.render('correspondence.public_access_denied_template')

        # For logged-in users, redirect to the standard Odoo download URL
        attachment = request.env['ir.attachment'].browse(attachment_id).exists()
        if not attachment:
            return request.not_found()
        
        return request.redirect(f'/web/content/{attachment.id}?download=true')