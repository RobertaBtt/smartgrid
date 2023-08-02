# -*- coding: utf-8 -*-

__author__ = 'roberta@enermed.it'

from openerp import fields, models, api, _, SUPERUSER_ID
import requests

class SmartgridApi:


    def getUltimaLetturaSmartmeter(self, environment, user, smartMeterObject):

        api_url = self._get_api_url(environment)
        token = self.get_token(environment, user, api_url)

        headers = {'Authorization': 'Bearer %s' % token}
        if smartMeterObject.phases == '1':
            table = 'sg_21'
            nome_campo_select = 'energia_attiva_prelievo'
        elif smartMeterObject.phases == '3':
            table = 'sg_18'
            nome_campo_select = 'energia_attiva_prelievo_sum'

        params = {
                'nome_campo_select': nome_campo_select,
                'nome_tabella': table,
                'nome_campo_where': 'sender_id',
                'valore_campo_where': smartMeterObject.name,
        }
        r = requests.get(api_url + '/erp/get_data',
                         params=params,
                         headers=headers)

        if r.status_code == 403:
            raise Warning(_('Permission Denied!'))

        elif r.status_code == 404:
            raise Warning(_('Smartmeter %s not found!' % str(smartMeterObject.name)))
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

    def getAllSmartmeters(self, environment, user, smartmeters_table):

        api_url = self._get_api_url(environment)
        token = self.get_token(environment, user, api_url)

        headers = {'Authorization': 'Bearer %s' % token}
        params = {'nome_tabella': smartmeters_table }


    #     url(r'^erp/smartmeters_scan/', ApiErpScanSmartmeters.as_view()),
    #     url(r'^erp/smartmeter_getdata/', ApiErpGetSmartmeterData.as_view()),
    #
        r = requests.get(api_url + '/erp/smartmeters_scan', params=params, headers=headers)





        if r.status_code == 403:
            raise Warning(_('Permission Denied!'))
        elif r.status_code == 404:
            raise Warning(_('Not found'))
        elif r.status_code == 400:
            raise Warning(_('Invalid Parameter!'))
        elif r.status_code == 500:
            raise Warning(_('Wrong response, internal error!'))
        else:
            r.raise_for_status()
        smartmeters_values = r.json()
        if not smartmeters_values['success']:
            raise Warning(_('Wrong response from api!'))

        return smartmeters_values['data']

    def getSmartmeterData(self, environment, user, table, sender_id,  data_da, data_a):

        api_url = self._get_api_url(environment)
        token = self.get_token(environment, user, api_url)

        headers = {'Authorization': 'Bearer %s' % token}
        params = {'nome_tabella': table,
                  'sender_id': sender_id,
                  'data_da': data_da,
                  'data_a': data_a }


        r = requests.get(api_url + '/erp/smartmeter_getdata', params=params, headers=headers)

        if r.status_code == 403:
            raise Warning(_('Permission Denied!'))
        elif r.status_code == 404:
            raise Warning(_('Not found'))
        elif r.status_code == 400:
            raise Warning(_('Invalid Parameter!'))
        elif r.status_code == 500:
            raise Warning(_('Wrong response, internal error!'))
        else:
            r.raise_for_status()
        smartmeter_data = r.json()
        if not smartmeter_data['success']:
            raise Warning(_('Wrong response from api!'))

        return smartmeter_data['data']

    def getTransmissionsCount(self, environment, user, table, data_da, data_a):

        api_url = self._get_api_url(environment)
        token = self.get_token(environment, user, api_url)

        headers = {'Authorization': 'Bearer %s' % token}
        params = {'nome_tabella': table,
                  'data_da': data_da,
                  'data_a': data_a }

        r = requests.get(api_url + '/erp/smartmeters/transmissions_count', params=params, headers=headers)

        if r.status_code == 403:
            raise Warning(_('Permission Denied!'))
        elif r.status_code == 404:
            raise Warning(_('Not found'))
        elif r.status_code == 400:
            raise Warning(_('Invalid Parameter!'))
        elif r.status_code == 500:
            raise Warning(_('Wrong response, internal error!'))
        else:
            r.raise_for_status()

        smartmeter_data = r.json()

        if not smartmeter_data['success']:
            raise Warning(_('Wrong response from api!'))

        return smartmeter_data['data']

    def getLastTransmission(self, environment, user, table, sender_id):

        api_url = self._get_api_url(environment)
        token = self.get_token(environment, user, api_url)

        headers = {'Authorization': 'Bearer %s' % token}
        params = {'nome_tabella': table,
                  'sender_id': sender_id }


        r = requests.get(api_url + '/erp/smartmeters/transmission_last', params=params, headers=headers)

        if r.status_code == 403:
            raise Warning(_('Permission Denied!'))
        elif r.status_code == 404:
            raise Warning(_('Not found'))
        elif r.status_code == 400:
            raise Warning(_('Invalid Parameter!'))
        elif r.status_code == 500:
            raise Warning(_('Wrong response, internal error!'))
        else:
            r.raise_for_status()

        smartmeter_data = r.json()

        if not smartmeter_data['success']:
            raise Warning(_('Wrong response from api!'))

        return smartmeter_data['data']

    def _get_api_url(self, environment):
        api_url = environment['ir.config_parameter'].get_param('smartgrid.api.url.parameter')
        return api_url

    def get_token(self, environment, userId, api_url):

        user = environment['res.users'].search([('id', '=', userId)])

        token = user.company_id.sg_temp_api_token or \
            self._get_token(environment, api_url, userId)
        return token


    def _get_token(self, environment, apiUrl, userId):

        client_id = environment['ir.config_parameter'].get_param('smartgrid.client.id')
        client_secret = environment['ir.config_parameter'].get_param('smartgrid.client.secret')

        params = dict(
            client_id=client_id,
            client_secret=client_secret,
            grant_type='client_credentials',
            scope='erp'
        )

        r = requests.post(apiUrl + '/o/token/', params=params)

        r.raise_for_status()
        token_response = r.json()
        if 'access_token' not in token_response:
            raise Warning(_('Token not present!'))

        valid_token = r.json()['access_token']

        vals = {'sg_temp_api_token': valid_token}

        user = environment['res.users'].search([('id', '=', userId)])

        company = user.company_id

        company.write(vals)

        return valid_token
