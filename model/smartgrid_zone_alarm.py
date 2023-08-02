# -*- coding: utf-8 -*-


from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import Warning
from openerp.tools import ( DEFAULT_SERVER_DATETIME_FORMAT as DSDF)
import dateutil.parser
import requests
import logging

_logger = logging.getLogger(__name__)


class SmartZoneAlarm(models.Model):
    _name = "sg.zone.alarm"
    _order = "request_timestamp"

    @api.one
    @api.depends('smartmeter_sn')
    def _get_smartmeter(self):
        obj_smartmeter=None
        if self.smartmeter_sn is not None:
            obj_smartmeter = self.env['sg.smartmeter'].search([('name', '=', self.smartmeter_sn)])
        else: self.smartmeter_id = None

        if obj_smartmeter.id is not False:
            self.smartmeter_id = obj_smartmeter.id
        else: self.smartmeter_id = None

    @api.one
    @api.depends('offline_smartmeter')
    def _not_offline_smartmeter(self):

        if self.offline_smartmeter == True:
            self.not_offline_smartmeter = False
        else:
            self.not_offline_smartmeter = True

    @api.one
    def _not_power_treshold_exceeded(self):

        if self.power_treshold_exceeded == True:
            self.not_power_treshold_exceeded = False
        else:
            self.not_power_treshold_exceeded = True

    @api.one
    @api.depends('tampering')
    def _not_tampering(self):

        if self.tampering == True:
            self.not_tampering = False
        else:
            self.not_tampering = True

    @api.one
    @api.depends('smartmeter_id')
    def _get_partner(self):

        if self.smartmeter_id is not None:
            obj_relation= self.env['sg.smartmeter.contract'].search([('smartmeter_id', '=', self.smartmeter_id.id)])
            if obj_relation.id is not False:
                self.client_name = obj_relation.contract_id.partner_id.name
        else: self.client_name = None


    @api.one
    @api.depends('smartmeter_id')
    def _get_pod_code(self):

        if self.smartmeter_id is not None:
            obj_relation= self.env['sg.smartmeter.contract'].search([('smartmeter_id', '=', self.smartmeter_id.id)])
            if obj_relation.id is not False:
                self.pod_code = obj_relation.contract_id.pod_code
        else:
            self.pod_code = None

    @api.one
    @api.depends('smartmeter_id')
    def _get_type(self):

        if self.smartmeter_id is not None:
            type = self.smartmeter_id.type
            if type == 'w':
                self.type = 'Withdrawal'
            elif type == 'e':
                self.type = 'Exchange'
            elif type == 'p':
                self.type = 'Production'
            elif type == 'op':
                self.type = 'Only Production'

        else:
            self.type = None


    smartmeter_sn = fields.Char(string='S/N Smartmeter', required=True)
    client_name = fields.Char(string="Client name", compute='_get_partner')
    pod_code = fields.Char(string="POD", compute='_get_pod_code')
    type = fields.Char(string="Type", compute='_get_type')
    request_timestamp = fields.Datetime(string='Check Time', required=True)

    zone_id = fields.Many2one('sg.zone', 'SmartGrid Zone', required=True)
    offline_smartmeter = fields.Boolean('Offline Smartmeter')
    not_offline_smartmeter= fields.Boolean('Offline Smartmeter', compute='_not_offline_smartmeter')

    power_treshold_exceeded = fields.Boolean('Power treshold exceeded')
    not_power_treshold_exceeded = fields.Boolean('Power treshold exceeded', compute='_not_power_treshold_exceeded')

    tampering = fields.Boolean('Tampering')
    not_tampering = fields.Boolean('Tampering', compute='_not_tampering')

    smartmeter_id = fields.Many2one('sg.smartmeter', string='Meter', store=True, compute='_get_smartmeter')


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
    def _get_alarm_values(self, api_url, token, zone_id, recall=None):
        headers = {'Authorization': 'Bearer %s' % token}
        params = {'zone_id': zone_id}
        res = {}
        r = requests.get(
            api_url + '/erp/grid/alarms',
            params=params,
            headers=headers
        )



        if r.status_code == 403:
            if recall:
                raise Warning(_('Permission Denied!'))
            token = self._get_auth_token(api_url)
            return self._get_alarm_values(api_url, token, zone_id, recall=True)
        # FIXME: to fix with new sql queries
        elif r.status_code == 500:
            _logger.info('Status code for alarm lines: %d' % r.status_code)
            return res
        # r.raise_for_status()
        jsonString = r.json()
        _logger.info("REQUEST RESULT *****************************************")
        _logger.info(jsonString)

        if jsonString['data'] is not None:
            if 'data' in jsonString:
                if 'timestamp' in jsonString['data']:
                    timestamp = jsonString['data']['timestamp']
                    current_date = dateutil.parser.parse(timestamp)
                    res['request_timestamp'] = current_date.strftime(DSDF)
                if 'sm_id' in jsonString['data']:
                    res['smartmeter_sn'] = jsonString['data']['sm_id']
                if 'offline' in jsonString['data']:
                    res['offline_smartmeter'] = jsonString['data']['offline']
                if 'manumission' in jsonString['data']:
                    res['tampering'] = jsonString['data']['manumission']
                if 'excess_power' in jsonString['data']:
                    res['power_treshold_exceeded'] = jsonString['data']['excess_power']
    #        _logger.info(res)
        return res


    @api.model
    def _get_alarm(self):
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

            toclean_zone_alarms = self.env['sg.zone.alarm'].search([])

            if len(toclean_zone_alarms) > 0:
                _logger.info('NUMERO DI RECORD DA CANCELLARE: %d' % len(toclean_zone_alarms))

                for alarmToDelete in toclean_zone_alarms:
                    obj_to_clean = self.env['sg.zone.alarm'].search([('id', '=', alarmToDelete.id)])
                    _logger.info('STO CANCELLANDO IL RECORD: %d' % obj_to_clean.id)
                    obj_to_clean.unlink()

            for zone in zones:
                res = self._get_alarm_values(
                    api_url,
                    token,
                    zone.name
                )
                if not res:
                    continue
                last_zone_alarm = self.env['sg.zone.alarm'].search(
                    [
                        ('zone_id', '=', zone.id)
                    ],
                    order='request_timestamp desc',
                    limit=1)
                if last_zone_alarm:
                    last_zone_alarm.write(res)
                else:
                    res['zone_id'] = zone.id
                    self.env['sg.zone.alarm'].create(res)
        return True


    @api.one
    def name_get(self):
        return self.id, self.request_timestamp

