# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Innoviu srl (<http://www.innoviu.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
from openerp.tools import (
    DEFAULT_SERVER_DATETIME_FORMAT as DSDF)

import logging

_logger = logging.getLogger(__name__)


class SmartGridAlarm(models.Model):
    _name = "sg.alarm"

    label = fields.Char( string='Alarm Name', required=True,readonly=False)
    description = fields.Text('Alarm Description')

    sg_alarm_id = fields.Many2one('sg.zone.alarm', 'Zone Alarm', required=True)
#    smartmeter_ids = fields.Many2many('sg.smartmeter', string='Smartmeter', required=True)
#     smartmeter_sn = fields.Char( string='Smartmeter ID', required=True,readonly=True)
#
#     offline_smartmeter = fields.Boolean('Offline Smartmeter',default=False)
#     power_treshold_exceeded = fields.Boolean('Power treshold exceeded', default=False)
#     tampering = fields.Boolean('Tampering', default=False)

    _sql_constraints = [
        ('name_label_uniq', 'unique(label)',
            'Label must be unique!'),
    ]


