from odoo import fields, models


class ResCityLocality(models.Model):
    _name = "res.locality"
    _description = "Locality"

    name = fields.Char("Locality", translate=True, noupdate=True)
    city_id = fields.Many2one('res.city', string='District/City')


class ResCityExtended(models.Model):
    _inherit = 'res.city'

    locality_ids = fields.One2many('res.locality', 'city_id', string='Locality')


class ResCountryStateExtended(models.Model):
    _inherit = 'res.country.state'

    name = fields.Char(translate=True)
