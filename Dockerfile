# Imagen base oficial de Odoo 16
FROM odoo:16

# Copiar addons personalizados
COPY ./addons-extra /mnt/extra-addons

# Copiar archivo de configuración
COPY ./etc/odoo/osoo.conf /etc/odoo/odoo.conf

# Crear directorio de logs si no existe y dar permisos
RUN mkdir -p /var/log/odoo && \
    chown -R odoo:odoo /mnt/extra-addons /etc/odoo /var/log/odoo

# (opcional) Expone el puerto que usará odoo si no lo hace la imagen base
EXPOSE 8069
