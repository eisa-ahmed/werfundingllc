# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
import requests
import datetime


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vicidial_lead_id = fields.Char()

    def get_vicidial_params(self):
        vicidial_url = self.env['ir.config_parameter'].sudo().get_param('vicidial.api_url')
        vicidial_login = self.env['ir.config_parameter'].sudo().get_param('vicidial.api_login')
        vicidial_password = self.env['ir.config_parameter'].sudo().get_param('vicidial.api_password')

        if not all([vicidial_url, vicidial_login, vicidial_password]):
            raise UserError("Please ensure all Vicidial configuration parameters are set.")

        VICIDIAL_API_ENDPOINT = f"http://{vicidial_url}/vicidial/non_agent_api.php"
        return VICIDIAL_API_ENDPOINT, vicidial_login, vicidial_password

    def create_lead_in_vicidial(self, vals):

        VICIDIAL_API_ENDPOINT, vicidial_login, vicidial_password = self.get_vicidial_params()

        date_str = vals.get("birth_date", '')
        if date_str:
            try:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                date_str = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                # If it's not in the expected format, you might want to handle it
                date_str = ''

        state_id = vals.get("state_id", '')
        if state_id:
            state_name = self.env['res.country.state'].browse([state_id]).name
        else:
            state_name = ''
        # Construct the query parameters
        params = {
            "source": "odoo",  # You can set this to identify the source of the API call
            "user": vicidial_login,
            "pass": vicidial_password,
            "function": "add_lead",
            "phone_number": vals.get("mobile", ''),
            "first_name": vals.get("name", ''),
            "last_name": vals.get("last_name"),
            "email": vals.get("email", ''),
            "date_of_birth": date_str,
            "postal_code": vals.get("zip", ''),
            "state": state_name,
            "city": vals.get("city", ''),
            "address1": vals.get("street", ''),
            "address2": vals.get("street1", ''),
            "agent_user": self.env.user.name
        }
        # Make the GET request
        try:
            response = requests.get(VICIDIAL_API_ENDPOINT, params=params, timeout=10)  # Added a timeout
            response.raise_for_status()  # Raise an HTTPError if an HTTP error occurred.
        except requests.RequestException as error:
            raise UserError(f"Failed to connect to Vicidial: {error}")

        response_data = response.text.split("|")
        print(response_data)
        # Check if response was successful and extract lead_id
        if "SUCCESS: add_lead" in response_data[0]:
            lead_id = response_data[2]
            return lead_id
        else:
            # Handle the failure scenario appropriately
            return None

    def update_lead_in_vicidial(self, lead_id, vals):

        VICIDIAL_API_ENDPOINT, vicidial_login, vicidial_password = self.get_vicidial_params()

        params = {
            "source": "odoo",
            "user": vicidial_login,
            "pass": vicidial_password,
            "function": "update_lead",
            "lead_id": int(lead_id)
        }

        # Mapping from Odoo field to Vicidial parameter
        fields_mapping = {
            'mobile': 'phone_number',
            'name': 'first_name',
            'last_name': 'last_name',
            'email': 'email',
            'birth_date': 'date_of_birth',
            'zip': 'postal_code',
            'state_id': 'state',
            'city': 'city',
            'street': 'address1',
            'street1': 'address2',
        }
        print(vals)
        for odoo_field, vicidial_param in fields_mapping.items():
            if odoo_field in vals:
                # Process each field value as needed before assigning it
                if odoo_field == "birth_date":
                    value = vals[odoo_field].strftime('%Y-%m-%d')
                elif odoo_field == "state_id":
                    value = self.env['res.country.state'].browse(vals[odoo_field]).name
                else:
                    value = vals[odoo_field]
                params[vicidial_param] = value
        print(params)
        # Send the request with params containing only the updated values
        try:
            response = requests.get(VICIDIAL_API_ENDPOINT, params=params, timeout=10)  # Added a timeout
            response.raise_for_status()  # Raise an HTTPError if an HTTP error occurred.
            response_data = response.text.split("|")
            print(response_data)

        except requests.RequestException as error:
            raise UserError(f"Failed to connect to Vicidial: {error}")

        return True

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        lead_id = res.create_lead_in_vicidial(vals)
        if lead_id:
            res.write({'vicidial_lead_id': lead_id})
        return res

    # def write(self, vals):
    #     # If the context flag is set, we're coming from our own update, so just call the base method
    #     if self.env.context.get('skip_vicidial_update'):
    #         return super(ResPartner, self).write(vals)
    #
    #     res = super(ResPartner, self).write(vals)
    #     for record in self:
    #         if record.vicidial_lead_id:
    #             # Send only the changed values
    #             changed_vals = {k: v for k, v in vals.items() if k in record._fields}
    #             record.with_context(skip_vicidial_update=True).update_lead_in_vicidial(record.vicidial_lead_id,
    #                                                                                    changed_vals)
    #     return res
