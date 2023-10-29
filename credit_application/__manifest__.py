# -*- coding: utf-8 -*-
{
    'name': "Credit Application",
    'summary': """
        The module will accept credit applications from a website form and create leads automatically from the form information.""",

    'description': """
        The module will accept credit applications from a website form and create leads automatically from the form information.
    """,
    'author': "EisaA",
    'license': 'LGPL-3',
    'website': "https://www.fiverr.com/eisaahmed63",
    'category': 'Human Resources',
    'version': '1',
    'depends': ['base', 'mail', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/view_application.xml',
        'views/view_business_owner.xml',
        'views/view_funds.xml',
        'wizard/wizard.xml'
    ],
    'application': True
}
