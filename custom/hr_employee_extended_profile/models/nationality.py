from odoo import fields, models


class HrEmployeeNationality(models.Model):
    _name = "hr.employee.nationality"
    _description = "HR Employee nationality"

    name = fields.Char(string="Nationality", translate=True)
