{
    'name': 'ISEP - Custom Planning',
    'version': '16.0',
    'category': 'Planning',
    'summary': 'Se añade un el campo Task_id',
    'license':'LGPL-3',
    'description': "Se añade un el campo Task_id",
    'author' : 'HFoc',
    'depends': [
        'project_forecast',
        'planning',
        'project'
    ],
    'data': [
        'views/planning_slot.xml',
    ],
    "installable": True,
    "application": False,

}
