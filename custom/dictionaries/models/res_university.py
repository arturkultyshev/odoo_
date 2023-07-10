from odoo import fields, models


class ResUniversity(models.Model):
    _name = "res.university"
    _description = "University"

    name = fields.Char(string="Name", translate=True)
