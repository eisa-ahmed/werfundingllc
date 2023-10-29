# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vicidial_api_url = fields.Char(string='Vicidial API URL',
                                   help="Enter only the IP address. The rest of the URL will be constructed automatically.")
    vicidial_api_login = fields.Char(string='Vicidial API Login')
    vicidial_api_password = fields.Char(string='Vicidial API Password')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('vicidial.api_url', self.vicidial_api_url)
        self.env['ir.config_parameter'].sudo().set_param('vicidial.api_login', self.vicidial_api_login)
        self.env['ir.config_parameter'].sudo().set_param('vicidial.api_password', self.vicidial_api_password)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            vicidial_api_url=self.env['ir.config_parameter'].sudo().get_param('vicidial.api_url'),
            vicidial_api_login=self.env['ir.config_parameter'].sudo().get_param('vicidial.api_login'),
            vicidial_api_password=self.env['ir.config_parameter'].sudo().get_param('vicidial.api_password')
        )
        return res
