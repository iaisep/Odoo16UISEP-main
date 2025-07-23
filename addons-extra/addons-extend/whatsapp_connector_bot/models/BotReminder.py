# -*- coding: utf-8 -*-
import logging
import random
from pytz import timezone
from datetime import datetime
from odoo import fields, models, api, _, tools
from odoo.tools import safe_eval
from odoo.addons.whatsapp_connector.tools import date2sure_write
_logger = logging.getLogger(__name__)


class BotReminders(models.Model):
    _name = 'acrux.chat.bot.reminder'
    _description = 'Reminders and Actions'
    _order = 'minutes, id'

    name = fields.Char('Description', required=True)
    bot_id = fields.Many2one('acrux.chat.bot', string='Bot', required=True, ondelete='cascade')
    minutes = fields.Integer('If inactive (Minutes)', help='Time since last sent message.')
    code = fields.Text('Message (Python Code)', default='text = "Hello %s" % conv_id.name\nret = {"send_text": text}')
    exit_bot = fields.Boolean('Exit from Bot')
    to_done = fields.Boolean('End Chat')

    _sql_constraints = [
        ('reminder_minutes_uniq', 'unique (bot_id, minutes)', _('Minutes has to be unique.'))
    ]

    @api.model
    def reminder_cron(self):
        log = []

        def add_log(txt, bot_log):
            bot_log and log.append(txt)

        Bot = self.env['acrux.chat.bot'].sudo().with_context(active_test=False)
        Conversation = self.env['acrux.chat.conversation'].sudo()
        Activities = self.env['acrux.chat.conversation.activities'].sudo()
        now = fields.Datetime.now()
        self.env.cr.execute('''
            SELECT A.conversation_id, A.id, A.rec_id, A.create_date
            FROM acrux_chat_conversation_activities A
            JOIN acrux_chat_conversation C ON C.id = A.conversation_id
            WHERE A.ttype = 'bot_thread' AND C.status IN ('new', 'done')
            ORDER BY A.id DESC''')
        activities = self.env.cr.dictfetchall()
        num = 0
        skip = []
        for activity in activities:
            id_conv = activity.get('conversation_id')
            if id_conv in skip:
                continue
            skip.append(id_conv)
            id_bot = activity.get('rec_id')
            create_date = date2sure_write(activity.get('create_date'))
            bot_id = Bot.search([('id', '=', id_bot), ('reminder_ids', '!=', False)])
            rem_ids = bot_id.reminder_ids
            if rem_ids:
                rem_ids = rem_ids.sorted(lambda r: r.minutes, reverse=True)
                log.append('==========\n%s reminder | BOT: %s' % (len(rem_ids), bot_id.name))
                conv_id = Conversation.search([('id', '=', id_conv)])
                conv_id = conv_id.with_context(self._get_connector_context(conv_id.connector_id))
                bot_log = conv_id.connector_id.bot_log
                add_log('Chat: %s' % conv_id.name, bot_log)
                for rem_id in rem_ids:
                    rem_date = fields.Datetime.subtract(now, minutes=int(rem_id.minutes)) if rem_id.minutes else now
                    requirements = self.requirements_to_exec(conv_id, rem_id, rem_date, create_date)
                    add_log('- Analyzing Reminder: %s (%s minutes)' % (rem_id.name, rem_id.minutes), bot_log)
                    add_log('  - Bot mess. date: %s' % create_date, bot_log)
                    add_log('  - Reminder  date: %s' % rem_date, bot_log)
                    add_log('  - Applicable by date? %s' % ('YES' if requirements else 'NO'), bot_log)
                    if requirements:
                        domain = [('conversation_id', '=', conv_id.id),
                                  ('ttype', '=', 'bot_mute_rem'),
                                  ('rec_id', '=', rem_id.id)]
                        mute_rem_ids = Activities.search(domain)
                        add_log('    - Reminder already applied (mute)?: %s' %
                                ('YES' if mute_rem_ids else 'NO'), bot_log)
                        if not mute_rem_ids:
                            add_log('    *** Executing > exit_bot: %s - to_done: %s ***' %
                                    (rem_id.exit_bot, rem_id.to_done), bot_log)
                            Activities.create({'conversation_id': conv_id.id,
                                               'ttype': 'bot_mute_rem',
                                               'rec_id': rem_id.id})
                            num += 1
                            self.reminder_exec(rem_id, conv_id)
                            self.env.cr.commit()
                        break
        _logger.info('________ | cron_reminders > Executing: %s' % num)
        if log:
            _logger.info('________ | DEBUG:\n%s' % '\n'.join(log))

    @api.model
    def requirements_to_exec(self, conv_id, rem_id, rem_date, create_date):
        return bool(create_date < rem_date)

    @api.model
    def reminder_exec(self, rem_id, conv_id):
        bus_js_dict = False
        if rem_id.exit_bot:
            self.env['acrux.chat.conversation.activities'].sudo().search([
                ('conversation_id', '=', conv_id.id),
                ('ttype', '=', 'bot_thread'),
                ]).unlink()
        if rem_id.code:
            message = self._build_dict(rem_id, conv_id)
            if message:
                bus_js_dict = conv_id.send_message(message, check_access=False)
        if rem_id.to_done and conv_id.status == 'new':
            conv_id.release_conversation_bot()  # set_to_done
        if not rem_id.to_done and conv_id.status == 'new' and bus_js_dict:
            data_to_send = conv_id.build_dict(limit=0)
            data_to_send[0]['messages'] = bus_js_dict
            conv_id._sendone(conv_id.get_bus_channel(), 'new_messages', data_to_send)

    @api.model
    def _build_dict(self, rem_id, conversation_id):
        results = self._eval_answer(rem_id, conversation_id)
        ret = {}
        for res in results:
            if res.get('send_text'):
                ret = {'ttype': 'text',
                       'from_me': True,
                       'contact_id': conversation_id.id,
                       'text': res.get('send_text')}
        return ret

    @api.model
    def _eval_answer(self, rem_id, conversation_id):
        out_code = []
        code = rem_id.code and rem_id.code.strip()
        if code:
            local_dict = self._get_eval_context(conversation_id)
            safe_eval.safe_eval(code, locals_dict=local_dict, mode='exec', nocopy=True)
            out_code = local_dict.get('ret', [])  # ret: list of dicts
            if isinstance(out_code, dict):
                out_code = [out_code]
        return out_code

    def _get_eval_context(self, conversation_id):
        eval_context = {
            'env': self.env,
            'now_local': fields.Datetime.context_timestamp(conversation_id, datetime.today()),
            'datetime': safe_eval.datetime,
            'dateutil': safe_eval.dateutil,
            'timezone': timezone,
            'random_choice': random.choice,
            'email_re': tools.email_re,
            'conv_id': conversation_id,
            'ret': [],
        }
        return eval_context

    @api.model
    def _get_connector_context(self, connector_id):
        ctx = {
            'tz': connector_id.tz,
            'lang': connector_id.company_id.partner_id.lang,
            'allowed_company_ids': [connector_id.company_id.id],
        }
        return ctx
