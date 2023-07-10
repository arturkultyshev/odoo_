from odoo import fields, models


class EmployeeFamilyMemberInfo(models.Model):
    _name = "hr.employee.family_member"
    _description = "Family Member Info"

    name = fields.Char()
    date_of_birth = fields.Date()
    relation = fields.Selection(
        string="Type",
        selection=[("parent", "Parent"), ("spouse", "Spouse"), ("child", "Child")],
        help="Relation type",
    )
    employee_id = fields.Many2one("hr.employee", "Employee")


class EmployeeFamilyInfo(models.Model):
    _inherit = "hr.employee"

    family_members_ids = fields.One2many(
        comodel_name="hr.employee.family_member", 
        inverse_name="employee_id"
    )