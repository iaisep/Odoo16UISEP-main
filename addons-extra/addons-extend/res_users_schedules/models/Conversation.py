
from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError
import pytz
import logging
_logger = logging.getLogger(__name__)

class AcruxChatConversation(models.Model):
    _inherit = 'acrux.chat.conversation'

    def conversation_verify_to_new(self, conn_id):
        res = super(AcruxChatConversation, self).conversation_verify_to_new(conn_id)
        datetime_n = datetime.now()
        user_tz = pytz.timezone(self.agent_id.tz)
        name_day = pytz.utc.localize(datetime_n).astimezone(user_tz).strftime("%A")
        datetime_now_hour = pytz.utc.localize(datetime_n).astimezone(user_tz).hour
        datetime_now_min = pytz.utc.localize(datetime_n).astimezone(user_tz).minute
        min_total = datetime_now_hour * 60 + datetime_now_min
        hour_now = min_total/60
        is_work = False

        if self.agent_id.employee_id.is_schedules:
            for user in self.agent_id.employee_id.schedules_ids:
                min_in = (user.entry_time * 60 + conn_id.time_to_reasign)/60
                if user.day_selected == name_day:
                    if min_in <= hour_now <= user.departure_time:
                        is_work = True                        
            if is_work:
                return res
            else:
                return self.env['acrux.chat.conversation']
        else:
            return res