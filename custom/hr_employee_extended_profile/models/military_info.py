from odoo import fields, models


class HrEmployeeMilitaryDuty(models.Model):
    _inherit = "hr.employee"

    military_service_attitude = fields.Selection(
        string="Attitude towards military service",
        selection=[
            ("conscript", "Conscript"),
            ("liable", "Liable for the military"),
            ("not_liable", "Not liable for the military"),
        ],
    )
    accounting_group = fields.Char(
        string="Accounting Group"
    )
    accounting_category = fields.Char(
        string="Accounting Category"
    )
    military_rank = fields.Char(
        string="Military Rank"
    )
    military_composition = fields.Char(
        string="Composition (profile)"
    )
    accounting_specialty = fields.Char(
        string="Military Accounting Specialty"
    )
    military_fitness = fields.Char(
        string="Fitness for Military Service"
    )
    military_registration = fields.Char(
        string="Military registration and enlistment office"
    )
    military_registration_attitude = fields.Char(
        string="Attitude to military registration"
    )
    military_registration_record = fields.Char(
        string="Record of military registration data"
    )
    military_id_scan = fields.Binary(
        string="Military ID scan"
    )
    war_veteran = fields.Many2one(
        comodel_name="hr.employee.veteran.status",
        string="War veteran"
    )


class VeteranStatus(models.Model):
    _name = "hr.employee.veteran.status"
    _description = "Veteran Status"

    name = fields.Char(string="Name", required=True, translate=True)