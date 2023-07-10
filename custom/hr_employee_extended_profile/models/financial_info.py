from odoo import models, fields, api


class EmployeeFinancialInfo(models.Model):
    _inherit = "hr.employee"

    currency_id = fields.Many2one(related='contract_id.currency_id')
    employment_contract_start_date = fields.Date(
        string='Employment contract valid from',
        related='employment_contract_id.date_start',
    )
    employment_contract_end_date = fields.Date(
        string='Employment contract valid until',
        related='employment_contract_id.date_end',
    )
    contract_registration_date = fields.Date(
        string='Date of employment contract registration',
        related='employment_contract_id.registration_date',
    )
    employment_contract_number = fields.Char(
        string='Employment contract conclusion number',
        related='employment_contract_id.employee_contract_number',
    )
    employment_order_number = fields.Char(
        string='No. of the employment order',
        related='employment_contract_id.order_number',
    )
    room_number = fields.Char(
        string='Room'
    )
    registration_information = fields.Char(
        string='Registration Information'
    )
    probationary_period = fields.Integer(
        string='Probationary period (in months)',
        related='contract_id.probationary_period',
        store=True, readonly=False
    )
    probationary_period_end_date = fields.Date(
        string='End of probation',
        related='contract_id.probationary_period_end_date',
        store=True, readonly=False
    )
    monthly_salary = fields.Monetary(
        string='Wages',
        related='contract_id.wage',
        readonly=False, store=True
    )
    hourly_salary = fields.Monetary(
        string='Salary (hourly work)',
        related='contract_id.hourly_wage',
        readonly=False, store=True
    )
    payroll_fund = fields.Integer(string='Payroll fund')
    surcharge = fields.Integer(
        related='contract_id.surcharge',
        readonly=False, store=True
    )

    tariff_category = fields.Selection(
        related='contract_id.tariff_category',
        string='Tariff category',
        readonly=False, store=True)
    payment_type = fields.Many2one(
        related='contract_id.payment_type',
        string='Payment type',
        readonly=False, store=True
    )
    formatted_employment_contract_start_date = fields.Char(
        compute="_compute_formatted_employment_contract_start_date"
    )
    formatted_employment_contract_end_date = fields.Char(
        compute='_compute_formatted_employment_contract_end_date'
    )
    bank = fields.Many2one(
        comodel_name="res.bank", 
        string="Bank"
    )
    card_number = fields.Char(
        string="Card number"
    )
    card_account_validity_start_date = fields.Date(
        string="Period (the beginning of the validity of the card account)"
    )
    accrual = fields.Selection(
        selection=[
            ("salary", "Salary"),
            ("hourly", "Hourly"),
        ],
        string="Accrual",
        default="salary",
        tracking=True,
    )
    tax = fields.Selection(
        selection=[
            ("with", "With Tax"),
            ("without", "Without Tax"),
        ],
        string="Tax",
        default="with",
    )
    timesheet_number = fields.Char(
        string="Timesheet number", 
        compute="_compute_timesheet_number", 
        readonly=True
    )

    # Additional (financial) information
    mandatory_pension_contribution = fields.Boolean(
        string='Mandatory Pension Contribution'
    )
    mandatory_social_insurance_contribution = fields.Boolean(
        string='Mandatory Social insurance contribution'
    )
    minimal_wage_deduction = fields.Boolean(
        string='Standard 14 MCI (1 Minimal wage)'
    )
    disabled_and_veteran_deduction = fields.Boolean(
        string='Standard deduction (disabled, war veterans)'
    )
    disabled_and_adoptive_child_parent_deduction = fields.Boolean(
        string='Standard deduction (parents of disabled, adoptive parents)'
    )
    voluntary_pension_contribution = fields.Boolean(
        string='Voluntary pension contribution'
    )
    medical_expenses = fields.Boolean(
        string='Medical expenses'
    )
    mortgage_reward_expenses = fields.Boolean(
        string='Mortgage reward expenses'
    )
    insurance_premium = fields.Boolean(
        string='Insurance premium'
    )

    @api.depends("name")
    def _compute_timesheet_number(self):
        for record in self:
            record.timesheet_number = record.id

    @api.depends('employment_contract_start_date')
    def _compute_formatted_employment_contract_start_date(self):
        for record in self:
            split_date = record.employment_contract_start_date.split('/')
            record.formatted_employment_contract_start_date = split_date[1] + '.' + split_date[0] + '.' + split_date[2]

    @api.depends('employment_contract_end_date')
    def _compute_formatted_employment_contract_end_date(self):
        for record in self:
            split_date = record.employment_contract_end_date.split('/')
            record.formatted_employment_contract_end_date = split_date[1] + '.' + split_date[0] + '.' + split_date[2]

