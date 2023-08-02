# -*- coding: utf-8 -*-

import pytz

from openerp import models, fields, api, _, SUPERUSER_ID
from datetime import timedelta, date, datetime, time
from openerp import tools
import re

class SmartgridConsole(models.TransientModel):
    """Populate the list of smartmeters by scanning the smartgrid database"""

    _name = "smartgrid.console"
    _description = "Smartmeter console"

    sender_id = fields.Many2one('sg.smartmeter',  string="Numero seriale smartmeter")
    data_da = fields.Datetime(string="Data da:")
    data_a = fields.Datetime(string="Data a:")

    @api.multi
    def scan_new_smartmeters(self):

        values = self.env['sg.smartmeter'].get_smartmeters()

        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'sg.smartmeter',
                'context': self._context,
                'domain': [ ('id', 'in', values) ]
            }


    @api.multi
    def get_smartmeter_data(self):


        if self.sender_id.id is False or self.data_a is False or self.data_a is False:
            raise models.except_orm(_('Attenzione'), _('Riempire smartmeter, data da, data a'))

        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)

        src_format = tools.misc.DEFAULT_SERVER_DATETIME_FORMAT

        display_date_result_data_da = datetime.strftime(pytz.utc.localize(datetime.strptime(self.data_da, src_format)).astimezone(local),"%Y-%m-%d %H:%M:%S")
        display_date_result_data_a = datetime.strftime(pytz.utc.localize(datetime.strptime(self.data_a, src_format)).astimezone(local),"%Y-%m-%d %H:%M:%S")


        values = self.env['sg.smartmeter'].get_data_from_smartgrid_db(self.sender_id, display_date_result_data_da, display_date_result_data_a)


        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'sg.data',
                'context': self._context,
                'domain': [ ('id', 'in', values) ],
            }

    @api.multi
    def get_transmission_count(self):

        if self.data_a is False or self.data_a is False:
            raise models.except_orm(_('Attenzione'), _('Riempire data da, data a'))

        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)

        src_format = tools.misc.DEFAULT_SERVER_DATETIME_FORMAT

        display_date_result_data_da = datetime.strftime(pytz.utc.localize(datetime.strptime(self.data_da, src_format)).astimezone(local),"%Y-%m-%d %H:%M:%S")
        display_date_result_data_a = datetime.strftime(pytz.utc.localize(datetime.strptime(self.data_a, src_format)).astimezone(local),"%Y-%m-%d %H:%M:%S")


        values = self.env['sg.smartmeter'].get_transmission_count_from_smartgrid_db(display_date_result_data_da, display_date_result_data_a)


        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'sg.data',
                'context': self._context,
                'domain': [ ('id', 'in', values) ],
            }

    @api.multi
    def get_last_transmission(self):

        if self.sender_id.id is False :
            raise models.except_orm(_('Attenzione'), _('Riempire smartmeter'))

        values = self.env['sg.smartmeter'].get_last_transmission_from_smartgrid_db(self.sender_id)

        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'sg.data',
                'context': self._context,
                'domain': [ ('id', 'in', values) ],
            }







