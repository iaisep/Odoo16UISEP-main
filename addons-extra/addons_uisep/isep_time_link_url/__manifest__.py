
{
    'name': 'iseptime_meeting_url_openeducat',
    'version': '6.0',
    'summary': 'ruta o link para runiones',
    'description': '',
    'category': '',
    'author': 'Eduardo',
    'website': '',
    'depends': ['base','openeducat_timetable_enterprise'],
    'data': [
       # 'security/ir.model.access.csv',
        'views/op_time_urls.xml',
        'views/time_url.xml',
        
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
