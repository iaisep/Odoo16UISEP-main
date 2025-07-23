# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################
import os
import re
import pickle
import logging

from odoo import tools, models
from odoo.exceptions import UserError
from odoo.http import root

_logger = logging.getLogger(__name__)


class ResConfigSettingsRedis(models.TransientModel):
    _inherit = 'res.config.settings'

    def button_convert_werkzeug_to_redis(self):
        session = root.session_store
        if hasattr(session, 'redis'):
            path = tools.config.session_dir
            for fname in os.listdir(path):
                path_1 = os.path.join(path, fname)
                try:
                    try:
                        f = open(path_1, 'rb')
                    except IOError:
                        data = {}
                    else:
                        try:
                            try:
                                data = pickle.load(f)
                            except Exception:
                                data = {}
                        finally:
                            f.close()
                        session_key = re.sub('\\.sess$', '', fname)
                        session.redis.set(
                            session_key, pickle.dumps(data), ex=session.expire)
                    os.unlink(path_1)
                except OSError:
                    pass
        else:
            _logger.error(
                'This button will work only when sessions are stores in Redis.')
