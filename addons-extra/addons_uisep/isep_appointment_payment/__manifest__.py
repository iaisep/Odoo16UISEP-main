# -*- coding: utf-8 -*-

{
    'name': 'Pago de Citas en el Sitio Web',
    'version': '16.0.1.0.0',
    'category': 'Website',
    'summary': 'Este módulo extiende la funcionalidad de la gestión de citas en Odoo para incluir opciones de pago anticipado y tarifas asociadas a las citas.',
    'description': """Las principales características incluyen:

Tarifas de Citas:

Permite configurar un producto específico como tarifa de cita en el modelo appointment.type.
Si una cita tiene configurado un producto con un precio, se muestra esta tarifa en las tarjetas de las citas y en el formulario de creación de citas.
Pago Anticipado:

Agrega la opción de requerir un pago anticipado para confirmar una cita.
Si el pago es requerido, el botón "Confirmar Cita" es reemplazado por un botón "Proceder al Pago".
Integra métodos de pago configurados en Odoo para gestionar este proceso.
Visualización de Tarifas:

Muestra el precio de las citas en el formulario y las tarjetas de citas, usando un formato monetario vinculado a la moneda configurada en el producto.
Configuración de Métodos de Pago:

Añade una plantilla para administrar los métodos de pago disponibles para las citas.
Proporciona un enlace directo para configurar métodos de pago en caso de no estar disponibles.
Interfaz de Usuario Personalizada:

Modifica las vistas existentes, como las tarjetas de citas y el formulario de citas, para incluir información de tarifas y opciones de pago de forma clara.
Configuración en el Modelo de Tipo de Cita:

Añade los campos:
has_payment_step: Define si la cita requiere pago anticipado.
product_id: Vincula un producto como tarifa de la cita.
Estos campos permiten una gestión detallada de las tarifas asociadas a las citas.""",
    'author': 'ISEP',
    'company': 'ISEP',
    'maintainer': 'ISEP',
    'website': 'https://www.isep.com',
    'depends': ['sale', 'base', 'website_appointment'],
    'data': [
        'data/appoinment_product_demo.xml',
        'views/templates.xml',
        'views/views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
