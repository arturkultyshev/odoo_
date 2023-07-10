from odoo import fields, models, api


class EmployeeLanguage(models.Model):
    _name = "hr.employee.language"
    _description = "HR Employee language"

    language = fields.Many2one(
        "hr.language",
        string="Language",
        ondelete='cascade'
    )
    language_level = fields.Many2one(
        "hr.language.level",
        string="Language level",
        ondelete='cascade'
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        ondelete='cascade'
    )


class Languages(models.Model):
    _name = "hr.language"
    _description = "HR languages"

    name = fields.Char(string="Language", translate=True)


class LanguageLevel(models.Model):
    _name = "hr.language.level"
    _description = "HR language level"

    name = fields.Char(string="Language level", translate=True)
