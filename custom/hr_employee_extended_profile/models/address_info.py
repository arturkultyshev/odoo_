from odoo import models, fields


class EmployeeAddress(models.Model):
    _inherit = "hr.employee"

    # Addresses
    birth_region = fields.Many2one(
        comodel_name="res.country.state", 
        string="Region",
        domain="[('country_id', '=', country_of_birth)]"
    )
    birth_district = fields.Many2one(
        comodel_name='res.city',
        string="District/City",
        domain="[('state_id', '=', birth_region)]"
    )
    birth_locality = fields.Many2one(
        comodel_name='res.locality',
        string="Locality",
        domain="[('city_id', '=', birth_district)]"
    )
    residence_country_id = fields.Many2one(
        comodel_name="res.country", 
        string="Country",
        tracking=True
    )
    residence_region = fields.Many2one(
        comodel_name="res.country.state",
        string="Region",
        domain="[('country_id', '=', residence_country_id)]"
    )
    residence_district = fields.Many2one(
        comodel_name="res.city", 
        string="District/City",
        domain="[('state_id', '=', residence_region)]"
    )
    residence_locality = fields.Many2one(
        comodel_name="res.locality",
        string="Locality",
        domain="[('city_id', '=', residence_district)]"
    )
    residence_street = fields.Char(
        string="Street"
    )
    residence_house = fields.Char(
        string="House"
    )
    residence_building = fields.Char(
        string="Building"
    )
    residence_apartment = fields.Char(
        string="Apartment"
    )
    individual_address_info = fields.Char(
        string="Address for informing individuals"
    )
    registration_country_id = fields.Many2one(
        comodel_name="res.country", 
        string="Country", 
        tracking=True
    )
    registration_region = fields.Many2one(
        comodel_name="res.country.state", 
        string="Region",
        domain="[('country_id', '=', registration_country_id)]"
    )
    registration_district = fields.Many2one(
        comodel_name='res.city', 
        string="District/City",
        domain="[('state_id', '=', registration_region)]"
    )
    registration_locality = fields.Many2one(
        comodel_name='res.locality', 
        string="Locality",
        domain="[('city_id', '=', registration_district)]"
    )
    registration_street = fields.Char(
        string="Street"
    )
    registration_house = fields.Char(
        string="House"
    )
    registration_building = fields.Char(
        string="Building"
    )
    registration_apartment = fields.Char(
        string="Apartment"
    )
    full_residence_address = fields.Char(
        compute="_compute_full_residence_address"
    )
    full_registration_address = fields.Char(
        compute="_compute_full_registration_address"
    )
