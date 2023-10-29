# -*- coding: utf-8 -*-
{
    # Application Information
    'name' : 'Credit App Report',
    'version' : '16.0.6',
    'category' : 'Administration',
    'description' : """ 
        Credit App Report
    """,
    'summary' : """
        Credit App Report
    """,
    
    # Author Information
    'author' : 'EisaA',
    
    # Technical Information
    'depends': ['base'],
    'data': [
            'views/template.xml',
            'views/module_report.xml',
            ],
    
    # App Technical Information
    'installable': True,
    'auto_install': False,
    'application' : True,
    'active': True,
}
