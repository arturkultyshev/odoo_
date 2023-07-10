from odoo import fields, models, api


class InheritResourceResource(models.Model):
    _inherit = "resource.resource"
    name = fields.Char(required=False)


class EmployeeExtended(models.Model):
    _inherit = "hr.employee"
    _description = "HR Employee extended"
    _rec_name = "full_name"
    _translate = True
    full_name = fields.Char(
        string="Full name", compute="_compute_full_name", store=True
    )
    first_name = fields.Char(
        string="First name",
        default="",
        compute="_compute_split_name",
        inverse="_inverse_split_name",
        store=True,
    )
    last_name = fields.Char(
        string="Last name",
        default="",
        compute="_compute_split_name",
        inverse="_inverse_split_name",
        store=True,
    )
    middle_name = fields.Char(
        string="Middle name",
        default="",
        compute="_compute_split_name",
        inverse="_inverse_split_name",
        store=True,
    )
    # Displays FIO in И.О. Фамилия
    formatted_full_name= fields.Char(
        compute="_compute_formatted_full_name"
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute="_compute_employee_department_id",
        store=True,
        readonly=True
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        domain="[('company_id', '=', company_id)]",
        compute="_compute_employee_project_id",
        store=True,
        readonly=True,
    )
    label = fields.Selection(
        selection=[
            ("working", "Working"),
            ("fired", "Fired"),
            ("reserve", "Reserve"),
        ],
        string="Status",
        default="working"
    )
    personnel_type = fields.Selection(
        selection=[
            ("site", "Site"),
            ("outstaffing", "Outstaffing"),
            ("administrative", "Administrative"),
        ],
        string="Personnel Type",
        default="site",
    )
    outstaff_company = fields.Selection(
        [
            ("tm", "TM"),
            ("fcca", "FCCA"),
        ],
        string="Outstaffing Company",
    )
    employee_type = fields.Selection(
        selection=[("direct", "Direct"), ("indirect", "Indirect")],
        string="Employee Type",
        default="direct",
    )
    foreign_specialist = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No")
        ],
        string="Foreign specialist"
    )

    @api.depends(
            "first_name",
            "last_name",
            "middle_name"
        )
    def _compute_formatted_full_name(self):
        for record in self:
            if record.middle_name:
                record.formatted_full_name = f"{record.last_name} {record.first_name[0]}.{record.middle_name[0]}."
            else:
                record.formatted_full_name = f"{record.last_name} {record.first_name[0]}."

    @api.depends('job_id')
    def _compute_employee_department_id(self):
        for record in self:
            record.department_id = record.job_id.department_id.id or None

    @api.depends('job_id')
    def _compute_employee_project_id(self):
        for record in self:
            if record.project_id:
                record.project_id = record.job_id.project_id.id or None

    def change_state(self):
        self.show_information = not self.show_information

    @api.depends("name")
    def _compute_split_name(self):
        for record in self:
            x = record.name.split()
            words = []
            for word in x:
                temp = ""
                for letters in word:
                    temp += letters
                words.append(temp)
            words.append("")

            if len(words) == 3:
                record.first_name = words[1]
                record.last_name = words[0]
            if len(x) == 3:
                words.append("")
                record.first_name = words[1]
                record.last_name = words[0]
                record.middle_name = words[2]

    def _inverse_split_name(self):
        for record in self:
            record.name = str(record.first_name)

    @api.depends("first_name", "last_name")
    def _compute_full_name(self):
        for record in self:
            record.full_name = (
                    str(record.last_name or "")
                    + " "
                    + str(record.first_name or "")
                    + " "
                    + str(record.middle_name or "")
            )

    @api.depends("first_name_latin", "last_name_latin", "middle_name_latin")
    def _compute_full_name_latin(self):
        for record in self:
            record.full_name_latin = (
                    str(record.last_name_latin) + " " +
                    str(record.first_name_latin) + " " + str(record.middle_name_latin)
            )

    @api.depends("name_latin")
    def _compute_split_latin_name(self):
        for record in self:
            if not record.name_latin:
                continue
            splitted_latin_name = str(record.name_latin).split(" ")
            record.first_name_latin = (
                splitted_latin_name[1] if len(splitted_latin_name) > 1 else ""
            )
            record.last_name_latin = (
                splitted_latin_name[0] if len(splitted_latin_name) > 0 else ""
            )
            record.middle_name_latin = (
                splitted_latin_name[2] if len(splitted_latin_name) > 2 else ""
            )

    @api.onchange('country_of_birth')
    def _birth_country_onchange(self):
        for record in self:
            return {'domain': {'birth_region': [('country_id', '=', record.country_of_birth.id)]},
                    'value': {'birth_region': False}}

    @api.onchange('registration_country_id')
    def _registration_country_onchange(self):
        for record in self:
            return {'domain': {'registration_region': [('country_id', '=', record.registration_country_id.id)]},
                    'value': {'registration_region': False}}

    @api.onchange('residence_country_id')
    def _residence_country_onchange(self):
        for record in self:
            return {'domain': {'residence_region': [('country_id', '=', record.residence_country_id.id)]},
                    'value': {'residence_region': False}}

    @api.onchange('birth_region')
    def _birth_region_onchange(self):
        for record in self:
            return {'domain': {'birth_district': [('state_id', '=', record.birth_region.id)]},
                    'value': {'birth_district': False, 'birth_locality': False}
                    }

    @api.onchange('birth_district')
    def _birth_district_onchange(self):
        for record in self:
            return {'domain': {'birth_locality': [('city_id', '=', record.birth_district.id)]},
                    'value': {'birth_locality': False}}

    @api.onchange('registration_region')
    def _registration_region_onchange(self):
        for record in self:
            return {'domain': {'registration_district': [('state_id', '=', record.registration_region.id)]},
                    'value': {'registration_district': False, 'registration_locality': False}}

    @api.onchange('residence_region')
    def _residence_region_onchange(self):
        for record in self:
            return {'domain': {'residence_district': [('state_id', '=', record.residence_region.id)]},
                    'value': {'residence_district': False, 'residence_locality': False}}

    @api.onchange('registration_district')
    def _registration_district_onchange(self):
        for record in self:
            return {'domain': {'registration_locality': [('city_id', '=', record.registration_district.id)]},
                    'value': {'registration_locality': False}}

    @api.onchange('residence_district')
    def _residence_district_onchange(self):
        for record in self:
            return {'domain': {'residence_locality': [('state_id', '=', record.residence_district.id)]},
                    'value': {'registration_locality': False}}

    @api.depends('residence_apartment', 'residence_building', 'residence_house', 'residence_street',
                 'residence_locality', 'residence_district', 'residence_region', 'residence_country_id')
    def _compute_full_residence_address(self):
        for record in self:
            address = [
                record.residence_country_id.name or '',
                record.residence_region.name or '',
                record.residence_district.name or '',
                record.residence_locality.name or '',
                record.residence_street or '',
                record.residence_house or '',
                record.residence_building or '',
                record.residence_apartment or '',
            ]
            address = list(filter(None, address))
            record.full_residence_address = ', '.join(address)

    @api.depends('registration_apartment', 'registration_building', 'registration_house', 'registration_street',
                 'registration_locality', 'registration_district', 'registration_region', 'registration_country_id')
    def _compute_full_registration_address(self):
        for record in self:
            address = [
                record.registration_country_id.name or '',
                record.registration_region.name or '',
                record.registration_district.name or '',
                record.registration_locality.name or '',
                record.registration_street or '',
                record.registration_house or '',
                record.registration_building or '',
                record.registration_apartment or '',
            ]
            address = list(filter(None, address))
            record.full_registration_address = ', '.join(address)
