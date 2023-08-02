{
    'name': "Smartgrid",
    'version': "1.0",
    'description': """This module integrates Smartgrid in module Fatturazione""",
    'author': "Roberta B, roberta@enermed.it",
    'website': "http://www.innoviu.com",
    'category': "Other",
    'summary': 'Fatturazione, Electric, Smartgrid',
    'depends': ['energy_people', 'attachment_amazon_s3'],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/smartgrid_security.xml',
        'security/ir.model.access.csv',

        'data/smartgrid_data.xml',

        'views/view_alarm.xml',
        'views/view_ir_attachment.xml',
        'views/view_message.xml',
        'views/view_smartmeter.xml',

        'views/view_smartgrid_board.xml',
        'views/view_smartgrid_data.xml',
        'views/view_smartgrid_ep_contract.xml',
        'views/view_smartgrid_ep_meter_readings.xml',
        'views/view_smartgrid_res_partner.xml',
        'views/view_smartgrid_simcard.xml',
        'views/view_smartgrid_smartmeter_contract.xml',
        'views/view_smartgrid_url.xml',
        'views/view_smartgrid_zone.xml',
        'views/view_smartgrid_zone_alarm.xml',
        'views/view_smartgrid_zone_power.xml',
        'views/view_smartgrid_res_company.xml',

        'wizard/view_smartgrid_customer_kwh_line_wizard.xml',
        'wizard/view_smartgrid_customer_kwh_wizard.xml',
        'wizard/view_smartgrid_get_data.xml',
        'wizard/smartgrid_console_view.xml',
        'views/menu.xml'
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True
}
