# -*- coding: utf-8 -*-

from openerp import fields, models, api, _, SUPERUSER_ID
from openerp.exceptions import Warning
from openerp.addons.energy_people.model.ep_contract import PROFILE
import requests
import logging

_logger = logging.getLogger(__name__)



class CustomerKwh(models.TransientModel):


    """Smartgrid Customer kWh Infos"""
    _name = "sg.customer.kwh.wizard"

    zone_id = fields.Many2one('sg.zone','SmartGrid Zone',help="Gets target and threshold values")

    name = fields.Many2one('ep.contract',  string="Contract", required=True, domain=[('active', '=', True)])
    profile = fields.Selection(PROFILE, string='Profile',  related='name.profile', store=True, readonly=True, copy=False)
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer','=',True), ('has_smartmeter', '=', True)])

    # 'doc_source': fields.reference('Source Document', required=True, selection=_get_document_types, size=128, help="User can choose the source document on which he wants to create documents"),

    kwh_lines = fields.One2many('sg.customer.kwh.line.wizard', 'wizard_id', 'kWh Values for each Smartmeter', readonly=True)
    request_time = fields.Datetime('Date Time Measure ', readonly=True)
    withdrawal_id = fields.Many2one('sg.smartmeter', string='Meter', store=False,compute='_compute_withdrawal')
    production_id = fields.Many2one('sg.smartmeter',string='Meter', store=False, compute='_compute_production')

    pr = fields.Float(string="Reactive Power",digits=(6, 8),required=False, readonly=True)
    pp = fields.Float(string="Produced Power", digits=(6, 8), required=False, readonly=True)
    pa = fields.Float(string="Active Power", digits=(6, 8), required=False, readonly=True)
    pau = fields.Float(string="Auto-consumed Power", digits=(6, 8), required=False, readonly=True)
    data_acquired = fields.Boolean(string='Datas acquired')



    @api.one
    @api.depends('request_time', 'name')
    def _compute_withdrawal(self):
        for smartmeter_contract in self.name.smartmeter_contract_ids:
            if smartmeter_contract.smartmeter_id.type in ('w', 'e'):
                # returns only the first sm found
                self.withdrawal_id = smartmeter_contract.smartmeter_id
                return True
        self.withdrawal_id = False

    @api.one
    @api.depends('request_time', 'name')
    def _compute_production(self):
        for smartmeter_contract in self.name.smartmeter_contract_ids:
            if smartmeter_contract.smartmeter_id.type in ('p', 'op'):
                # returns only the first sm found
                self.production_id = smartmeter_contract.smartmeter_id
                return True
        self.production_id = False

    @api.model
    def _get_auth_token(self, api_url):
        """
            Called by action methods and cron methods
        """
        client_id = self.env['ir.config_parameter'].get_param('smartgrid.client.id')
        client_secret = self.env['ir.config_parameter'].get_param( 'smartgrid.client.secret')

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

    # Here we use 2 different methods instead of a single one
    # because api may change in time
    @api.model
    def _get_energy_values(self, api_url, token, contract_id, recall=None):
        headers = {'Authorization': 'Bearer %s' % token}
        params = {'contract_id': contract_id}
        # TODO Aggiungere parametro Database

        r = requests.get(api_url + '/erp/measures',
                         params=params,
                         headers=headers)
        if r.status_code == 403:
            if recall:
                raise Warning(_('Permission Denied!'))
            token = self._get_auth_token(api_url)
            return self._get_energy_values(
                api_url, token, contract_id, recall=True)
        elif r.status_code == 404:
            raise Warning(_('Contract %s not found!' % str(contract_id)))
        elif r.status_code == 400:
            raise Warning(_('Invalid Parameter!'))
        elif r.status_code == 500:
            raise Warning(_('Wrong response, internal error!'))
        else:
            r.raise_for_status()
        values = r.json()
        if not values['success']:
            raise Warning(_('Wrong response from api!'))
        return values

    @api.model
    def _get_power_values(self, api_url, token, contract_id, recall=None):
        headers = {'Authorization': 'Bearer %s' % token}
        params = {'contract_id': contract_id}
        r = requests.get(api_url + '/erp/powers',
                         params=params,
                         headers=headers)
        if r.status_code == 403:
            if recall:
                raise Warning(_('Permission Denied!'))
            token = self._get_auth_token(api_url)
            return self._get_energy_values(
                api_url, token, contract_id, recall=True)
        elif r.status_code == 404:
            raise Warning(_('Contract %s not found!' % str(contract_id)))
        elif r.status_code == 400:
            raise Warning(_('Invalid Parameter!'))
        elif r.status_code == 500:
            raise Warning(_('Wrong response, internal error!'))
        else:
            r.raise_for_status()
        pvalues = r.json()
        if not pvalues['success']:
            raise Warning(_('Wrong response from api!'))
        return pvalues

    @api.one
    def data_get(self):
        wizard_vals = {}
        api_url = self.env['ir.config_parameter'].get_param(
            'smartgrid.api.url.parameter'
        )
        user = self.env['res.users'].search([('id', '=', self._uid)])
        token = user.company_id.sg_temp_api_token or \
            self._get_auth_token(api_url)
        # Energy
        values = self._get_energy_values(api_url,
                                         token,
                                         self.name.id)
        customer_kwh_lines = self.env['sg.customer.kwh.line.wizard']
        _logger.info(values['data'])
        start = 0
        if 'data' in values:
            for value in values['data']:
                line = {}

                if 'h' in value:
                    if int(value['h']) == 22:
                        line['measure_time'] = 0
                        _logger.info('Start Yesterday or Today')
                        start += 1

                    elif int(value['h']) == 23:
                        line['measure_time'] = 1
                    else:
                        line['measure_time'] = int(value['h'])+2


                if 'h' in value and 'p' in value and 'n' in value and start:
                    line['day'] = start == 1 and 'yesterday' or 'today'
                    line['sequence'] = int(value['n'])
                    line['kwh'] = value['p']
                elif start:
                    raise Warning(_('Error! no kWh to show.'))
                else:
                    continue
                line['wizard_id'] = self.id
                customer_kwh_lines.create(line)
        else:
            raise Warning(_('Error! no kWh to show.'))

        # Power
        pvalues = self._get_power_values(api_url,
                                         token,
                                         self.name.id)
        _logger.info(pvalues)
        wizard_vals['request_time'] = fields.Datetime.now()
        # TODO: check values based on meter type
        # we consider only the first element of data
        if 'data' in pvalues and len(pvalues['data']) > 0:
            if 'pa' in pvalues['data']:
                wizard_vals['pa'] = pvalues['data']['pa']
            if 'pp' in pvalues['data']:
                wizard_vals['pp'] = pvalues['data']['pp']
            if 'pr' in pvalues['data']:
                wizard_vals['pr'] = pvalues['data']['pr']
            if 'pau' in pvalues['data']:
                wizard_vals['pau'] = pvalues['data']['pau']
        wizard_vals['data_acquired'] = True
        self.write(wizard_vals)
        return True

    @api.multi
    def get_graph(self):
        ids = [pl.id for pl in self[0].kwh_lines]
        return {
            'name': _('Customer kWh by Smartmeter'),
            'view_type': 'tree',
            "view_mode": 'graph,tree',
            'res_model': 'sg.customer.kwh.line.wizard',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', ids)],
            'target': 'new',
        }
