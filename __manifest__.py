# -*- coding: utf-8 -*-
{
    'name': "Correspondencia Institucional",
    'summary': """
        Gestión de correspondencia y comunicados internos.
    """,
    'description': """
        Este módulo tiene como objetivo digitalizar y centralizar el proceso de envío, recepción, seguimiento y archivo de documentos y comunicados internos entre los diferentes departamentos de una organización.
    """,
    'author': "Carlos Fuentes (CFuentes.Dev)",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.2',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'website', 'hr'],
    'data': [
        ## Security
        'security/correspondence_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        ## Data
        'data/correspondence_type_data.xml',
        'data/ir_sequence_data.xml',
        ## Wizards
        #'wizard/upload_signed_document_wizard_view.xml',
        ## Views
        'views/correspondence_type_view.xml',
        'views/correspondence_department_view.xml',
        #'views/correspondence_document_view_form.xml',
        #'views/hr_employee_view.xml',
        #'views/public_correspondence_template.xml',
        ## Reports
        #'report/correspondence_report.xml',
        # Menus
        #'views/menu_views.xml',
    ],
    'demo': [
    ],
}
