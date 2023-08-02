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
import time
import dateutil.parser
import requests
import logging

_logger = logging.getLogger(__name__)


class SmartZonePower(models.Model):
    _name = "sg.zone.power"
    _order = "name"

    name = fields.Datetime(string='Measure Date', required=True)
    color = fields.Integer(string='Color Index')
    zone_id = fields.Many2one('sg.zone', 'SmartGrid Zone', required=True)
    meter_number = fields.Integer(string="Number of Meters", required=True)
    active_power_in = fields.Integer(string='Active Power Input', default=0)
    active_power_out = fields.Integer(string='Active Power Drawn', default=0)

    @api.one
    @api.depends('active_alarm_number')
    def _get_alarm_number(self):
        total_alarms = self.env['sg.zone.alarm'].search([('zone_id', '=', self.zone_id.id)])
        _logger.info('NUMERO TOTALE DI ALLARMI PER LA ZONA %d: %d', self.zone_id.id, len(total_alarms))
        if len(total_alarms) > 0:
            self.active_alarm_number = len(total_alarms)
            # _logger.info('ACTIVE ALARMS NUMBER DIVENTA: %d', len(total_alarms))
        else:
            self.active_alarm_number = 0
            # _logger.info('ACTIVE ALARMS NUMBER RIMANE A ZERO')

    @api.one
    @api.depends('offline_meter_number')
    def _get_offline_meters(self):
        offline_meters = self.env['sg.zone.alarm'].search([('zone_id', '=', self.zone_id.id), ('offline_smartmeter', '=', True)])
        _logger.info('NUMERO TOTALE DI METER OFFLINE PER LA ZONA %d: %d', self.zone_id.id, len(offline_meters))
        if len(offline_meters) > 0:
           self.offline_meter_number = len(offline_meters)
           # _logger.info('OFFLINE METERS NUMBER DIVENTA: %d', len(offline_meters))
        else:
           self.offline_meter_number = 0
           # _logger.info('OFFLINE METERS NUMBER RIMANE A ZERO')

    @api.one
    @api.depends('online_meter_number')
    def _get_online_meters(self):
       self.online_meter_number = self.meter_number - self.offline_meter_number
       _logger.info('NUMERO TOTALE DI METER ONLINE PER LA ZONA %d: %d', self.zone_id.id, self.online_meter_number)
       # _logger.info('ONLINE METERS NUMBER DIVENTA: %d', self.online_meter_number)

    # contract_number = fields.Integer(related='zone_id.contract_number',
    #                                  store=False,
    #                                  readonly=True,
    #                                  copy=False)
    max_active_power_in = fields.Integer(string='Max Active Power Input', default=25)
    max_active_power_out = fields.Integer(string='Max Active Power Drawn', default=32)
    offline_meter_number = fields.Integer(string="Number of Offline Meters",required=True,compute='_get_offline_meters')
    active_alarm_number = fields.Integer(string="Number of Active Alarms", required=True, compute='_get_alarm_number')
    online_meter_number = fields.Integer(string="Number of Online Meters", required=True, compute='_get_online_meters')

    _sql_constraints = [
        ('name_zone_uniq', 'unique(name, zone_id)',
            'Date and Zone must be unique!'),
    ]

    @api.model
    def _get_auth_token(self, api_url):
        """
            Called by action methods and cron methods
        """
        client_id = self.env['ir.config_parameter'].get_param(
            'smartgrid.client.id')
        client_secret = self.env['ir.config_parameter'].get_param(
            'smartgrid.client.secret')
        # TODO: move scope and grant_type in configurations
        params = dict(
            client_id=client_id,
            client_secret=client_secret,
            grant_type='client_credentials',
            scope='erp'
        )
        r = requests.post(api_url + '/o/token/', params=params)
        # Rises if status != 200
        # FIXME: it needs more love
        r.raise_for_status()
        token_response = r.json()
        if 'access_token' not in token_response:
            raise Warning(_('Token not present!'))
        valid_token = r.json()['access_token']
        vals = {'sg_temp_api_token': valid_token}
        user = self.env['res.users'].search([('id', '=', self._uid)])
        company = user.company_id
        company.write(vals)
        return valid_token

    @api.model
    def _get_power_values(self, api_url, token, zone_id, recall=None):
        headers = {'Authorization': 'Bearer %s' % token}
        params = {'zone_id': zone_id}
        res = {}
        r = requests.get(
            api_url + '/erp/grid/stats',
            params=params,
            headers=headers
        )
        if r.status_code == 403:
            if recall:
                raise Warning(_('Permission Denied!'))
            token = self._get_auth_token(api_url)
            return self._get_power_values(api_url, token, zone_id, recall=True)
        # FIXME: to fix with new sql queries
        elif r.status_code == 500:
            _logger.info('Status code for power lines: %d' % r.status_code)
            return res
        # r.raise_for_status()
        values = r.json()
        _logger.info(res)
        if 'data' in values:
            if 'timestamp' in values['data']:
                timestamp = values['data']['timestamp']
                current_date = dateutil.parser.parse(timestamp)
                res['name'] = current_date.strftime(DSDF)
            if 'meters_no' in values['data']:
                res['meter_number'] = values['data']['meters_no']
            if 'pot_attiva_immessa' in values['data']:
                res['active_power_in'] = values['data']['pot_attiva_immessa']
            if 'pot_attiva_prelevata' in values['data']:
                res['active_power_out'] = values['data']['pot_attiva_prelevata']
            if 'pot_immessa_max' in values['data']:
                res['max_active_power_in'] = values['data']['pot_immessa_max']
            if 'pot_prelevata_max' in values['data']:
                res['max_active_power_out'] = values['data']['pot_prelevata_max']
            if 'meter_no_online' in values['data']:
                res['online_meter_number'] = values['data']['meter_no_online']
            if 'meter_no_offline' in values['data']:
                res['offline_meter_number'] = values['data']['meter_no_offline']
            # if 'allarmi_no' in values['data']:
            #     res['active_alarm_number'] = values['data']['allarmi_no']
        _logger.info(res)
        return res

    @api.model
    def _get_power(self):
        """
            GET /GRID/STATS
        """
        zones = self.env['sg.zone'].search([])
        if len(zones):
            api_url = self.env['ir.config_parameter'].get_param(
                'smartgrid.api.url.parameter'
            )
            user = self.env['res.users'].search([('id', '=', self._uid)])
            token = user.company_id.sg_temp_api_token or \
                self._get_auth_token(api_url)
            for zone in zones:
                res = self._get_power_values(
                    api_url,
                    token,
                    zone.name
                )
                if not res:
                    continue
                last_zone_power = self.env['sg.zone.power'].search(
                    [
                        ('zone_id', '=', zone.id)
                    ],
                    order='name desc',
                    limit=1)
                if last_zone_power:
                    last_zone_power.write(res)
                else:
                    res['zone_id'] = zone.id
                    self.env['sg.zone.power'].create(res)
        return True

    @api.multi
    def new_message(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sg.message',
            'view_mode': 'form,tree',
            'view_type': 'form',
            'name': 'New Message',
            'context': {'default_zone_id': self[0].zone_id.id}
        }
