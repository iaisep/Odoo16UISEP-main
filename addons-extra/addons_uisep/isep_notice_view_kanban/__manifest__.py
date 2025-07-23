
{
    'name': 'Isep notice board',
    'version': '6.0',
    'summary': 'Agregar una imagen a la notice boardi',
    'description': '',
    'category': '',
    'author': 'Eduardo',
    'website': '',
    'depends': ['base','openeducat_notice_board_enterprise'],
    'data': [
       # 'security/ir.model.access.csv',
        'views/notice_board_image.xml',
        'views/notice_board.xml',
        'views/notice_board_circular.xml',
        
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
