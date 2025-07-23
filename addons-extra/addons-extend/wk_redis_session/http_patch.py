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
# PLEASE REFER THE FOLLOWING DOCS -
# https://buildmedia.readthedocs.org/media/pdf/redis-py-cluster/unstable/redis-py-cluster.pdf

import odoo
import contextlib
import glob
import pickle
import os
import time
import logging
import collections

from odoo.tools import config
from odoo.service import security, model as service_model
from odoo.exceptions import UserError, warnings
from odoo.tools.func import lazy_property
from odoo.tools._vendor import sessions
from odoo.http import Application, Session, SESSION_LIFETIME, root, FilesystemSessionStore as FSS
from odoo.http import request

_logger = logging.getLogger(__name__)
REDIS_STATUS = False
try:
    import redis
    REDIS_STATUS = True
except BaseException:
    _logger.info(
        "< ERROR : Redis not found in server, run camand pip install redis. >")


class RedissystemSessionStore(sessions.FilesystemSessionStore):
    def __init__(
            self,
            host,
            port,
            expire,
            db,
            ssl_ca_certs,
            session_class=None,
            redis_key_template='werkzeug_%s'):
        sessions.SessionStore.__init__(self, session_class)
        self.port = port
        self.host = host
        self.db = db
        self.redis_key_template = redis_key_template
        self.ssl_ca_certs = ssl_ca_certs
        self.redis = self._getRedisObj()
        self.expire = expire

    def __getitem__(self, item):
        if item == 'geoip':
            warnings.warn('request.session.geoip have been moved to request.geoip', DeprecationWarning)
            return request.geoip if request else {}
        return self.data[item]

    def __setitem__(self, item, value):
        if item not in self.data or self.data[item] != value:
            self.is_dirty = True
        self.data[item] = value


    def __delitem__(self, item):
        del self.data[item]
        self.is_dirty = True

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)


    def _getRedisObj(self):
        try:
            redisObj = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                ssl=self.ssl_ca_certs and True or False,
                ssl_ca_certs=self.ssl_ca_certs or None,
            )
            redisObj.ping()
            _logger.debug('REDIS CONNECTION SUCCESSFULL !! HURRAY ENJOY :)')
            return redisObj
        except Exception as e:
            _logger.error('REDIS CONNECTION EXCEPTION : %r', e)
            return False

    def save(self, session):
        try:
            self._saveRedisSession(session)
        except Exception as e:
            _logger.debug('%r', e)

    def _renameSessionKey(self, sid):
        return (self.redis_key_template % sid)

    def _saveRedisSession(self, session):
        session_key = self._renameSessionKey(session.sid)
        return self.redis.set(
            session_key, pickle.dumps(
                dict(session)), ex=self.expire)

    def get(self, sid):
        try:
            data = self._getRedisKey(sid)
            redis_key = self._renameSessionKey(sid)
            self.redis.set(redis_key, data, ex=self.expire)
            data = pickle.loads(data)
        except BaseException:
            data = {}
        return self.session_class(data, sid, False)

    def _getRedisKey(self, sid):
        session_key = self._renameSessionKey(sid)
        return self.redis.get(session_key)

    def delete(self, session):
        try:
            self.redis.delete(session.sid)
        except Exception as e:
            _logger.debug('%r', e)


    def rotate(self, session, env):
        self.delete(session)
        session.sid = self.generate_key()
        if session.uid and env:
            session.session_token = security.compute_session_token(session, env)
        session.should_rotate = False
        self.save(session)
        
    def vacuum(self, max_lifetime=SESSION_LIFETIME):
        if not hasattr(root.session_store, 'redis'):
            threshold = time.time() - SESSION_LIFETIME
            for fname in glob.iglob(os.path.join(root.session_store.path, '*', '*')):
                path = os.path.join(root.session_store.path, fname)
                with contextlib.suppress(OSError):
                    if os.path.getmtime(path) < threshold:
                        os.unlink(path)
                    

@lazy_property
def session_store(self):
    if config.get('redis_session') and REDIS_STATUS:
        host = config.get('redis_host') or 'localhost'
        port = config.get('redis_port') or 6379
        expire = config.get('redis_expire') or 60 * \
            60 * 24 * 5
        ssl_ca_certs = config.get('redis_ssl_ca_certs') or None
        session = RedissystemSessionStore(session_class=Session,
                                          host=host,
                                          port=port,
                                          expire=int(expire),
                                          ssl_ca_certs=ssl_ca_certs,
                                          db=0
                                          )
    else:
        path = odoo.tools.config.session_dir
        _logger.debug('HTTP sessions stored in: %s', path)
        session = sessions.FilesystemSessionStore(
            path, session_class=Session, renew_missing=True)
    return session

Application.session_store = session_store

# def vacuum(self):
#     if not hasattr(root.session_store, 'redis'):
#         threshold = time.time() - SESSION_LIFETIME
#         for fname in glob.iglob(os.path.join(root.session_store.path, '*', '*')):
#             path = os.path.join(root.session_store.path, fname)
#             with contextlib.suppress(OSError):
#                 if os.path.getmtime(path) < threshold:
#                     os.unlink(path)

# FSS.vacuum = vacuum
