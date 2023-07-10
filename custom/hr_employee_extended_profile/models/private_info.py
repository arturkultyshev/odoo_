from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class EmployeePrivateInformation(models.Model):
    _inherit = "hr.employee"

    # Private info
    iin = fields.Char(
        string="IIN",
        size=12,
        required=True
    )
    name_latin = fields.Char(
        string="Latin name"
    )
    first_name_latin = fields.Char(
        string="Latin first name"
    )
    last_name_latin = fields.Char(
        string="Latin last name"
    )
    middle_name_latin = fields.Char(
        string="Latin middle name"
    )
    full_name_latin = fields.Char(
        compute="_compute_full_name_latin"
    )
    nationality = fields.Many2one(
        comodel_name="hr.employee.nationality", 
        string="Nationality"
    )
    citizenship = fields.Many2one(
        comodel_name="res.country", 
        string="Citizenship"
    )
    pension = fields.Selection(selection=[
        ("yes", "Yes"), 
        ("no", "No")
    ], string="Pension", 
    default="no"
    )
    pension_date = fields.Char(
        string="Pension date", 
        compute="_compute_pension_date", 
        store=True
    )
    formated_pension_date = fields.Char(
        string="Formatted penstion date", 
        compute="_compute_formatted_pension_date",                                
        store=True
    )
    pension_pay_provide = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string="Provide pension pay"
    )

    @api.depends("birthday", "gender")
    def _compute_pension_date(self):
        for record in self:
            if record.gender and record.birthday:
                if record.gender == 'male':
                    calculated_pensation_date = self._calculate_age_at_retirement(
                        record.birthday, 63)
                    record.pension_date = calculated_pensation_date
                if record.gender == 'female':
                    time_ranges = {
                        "61": ['01/01/1900', '31/12/1962'],
                        "61.5": ['01/01/1963', '30/06/1963'],
                        "62": ['01/07/1963', '31/12/1963'],
                        "62.5": ['01/01/1964', '30/06/1964']
                    }
                    birthdate = record.birthday
                    if birthdate > datetime.strptime("01/07/1964", "%d/%m/%Y").date():
                        record.pension_date = self._calculate_age_at_retirement(
                            record.birthday, 63)
                    for key, value in time_ranges.items():
                        start_date = datetime.strptime(value[0], "%d/%m/%Y")
                        end_date = datetime.strptime(value[1], "%d/%m/%Y")
                        if birthdate >= start_date.date() and birthdate <= end_date.date():
                            record.pension_date = self._calculate_age_at_retirement(
                                record.birthday, float(key))
                            break

    def _calculate_age_at_retirement(self, birthday, years):
        if isinstance(years, int):
            years = int(years)
            date_object = datetime.strptime(str(birthday), '%Y-%m-%d')
            return date_object.replace(year=date_object.year + years).date()
        if isinstance(years, float):
            date_object = datetime.strptime(str(birthday), '%Y-%m-%d')
            date_object = date_object.replace(
                year=date_object.year + int(years)).date()
            date_object = date_object + relativedelta(months=+6)
            return date_object
        
    @api.depends("pension_date")
    def _compute_formatted_pension_date(self):
        for record in self:
            if record.pension_date:
                date_object = datetime.strptime(
                    record.pension_date, "%Y-%m-%d")
                record.formated_pension_date = date_object.strftime("%d.%m.%Y")