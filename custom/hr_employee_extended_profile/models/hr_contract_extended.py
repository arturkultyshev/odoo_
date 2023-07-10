from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

from odoo import fields, models, _, api, tools


class PaymentType(models.Model):
    _name = "payment.type"
    _description = "Payment Type"

    name = fields.Char(string="Name", translate=True)
    code = fields.Char(string="Code")


class WorkRestOption(models.Model):
    _name = 'work.rest.model'
    _description = 'Work and Rest Options'

    name = fields.Char()


class HrContractExtended(models.Model):
    _inherit = 'hr.contract'

    def _get_default_order_number(self):
        order_number = self.env['hr.contract'].search_count([])
        return f'{order_number + 1}'

    order_number = fields.Char(
        string='Order Number',
        default=_get_default_order_number
    )
    state = fields.Selection(
        selection_add=[('terminated', 'Terminated')],
        ondelete={'draft': 'set default'}
    )
    employment_type = fields.Selection(
        selection=[
            ('primary_employment', 'Primary Employment'),
            ('combination', 'Combination'),
        ],
        string="Type of employment",
    )

    contract_concluded = fields.Selection([
        ('1', 'For the duration of the working permit'),
        ('2', 'For the duration of certain works'),
        ('3', 'It is simply concluded for 1 calendar year')],
        string='Contract concluded',
    )
    name = fields.Char(compute='_compute_name', store=True, readonly=False, required=False)

    _sql_constraints = [
        (
            'order_number_uniq',
            'UNIQUE (order_number)',
            'All order numbers must be unique'
        )
    ]
    contract_type = fields.Selection([
        ('primary', 'Primary'),
        ('additional', 'Additional'),
    ], string='Contract Type', default='primary', required=True)
    surcharge = fields.Integer(string='Surcharge')

    @api.depends('employee_id', 'date_start', 'order_number', 'contract_type')
    def _compute_name(self):
        for contract in self:
            if contract.contract_type == 'primary':
                contract.name = f'Трудовой договор №{contract.order_number} от {contract.date_start}'
            else:
                contract.name = f'Дополнительное соглашение №{contract.order_number} от {contract.date_start}'

    employment_contract_start_date = fields.Date(related='date_start')
    date_start = fields.Date(required=False)
    employment_contract_end_date = fields.Date(related='date_end')
    registration_date = fields.Date(string='Registration Date')
    employee_contract_number = fields.Char(string='Employee Contract Number')
    working_rest_time = fields.Many2one('work.rest.model', 'Work and Rest time')
    work_schedule_type = fields.Selection([
        ('five_days', 'Five days'),
        ('six_days', 'Six days'),
        ('shift', 'Shift'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('changing', 'Changing'),
    ], 'Schedule Type',
        compute='_compute_work_schedule_type',
        store=True,
        readonly=False,
    )

    @api.depends('employee_id')
    def _compute_work_schedule_type(self):
        for contract in self:
            contract.work_schedule_type = contract.employee_id.work_schedule_type

    probationary_period = fields.Integer(
        string='Probationary period (in months)',
        default=3,
    )
    probationary_period_end_date = fields.Date(
        related='trial_date_end',
    )
    trial_date_end = fields.Date(
        compute='_compute_trial_end_date',
        store=True,
        readonly=False,
    )

    @api.depends('date_start', 'probationary_period')
    def _compute_trial_end_date(self):
        for contract in self.filtered('date_start'):
            contract.trial_date_end = contract.date_start + relativedelta(months=contract.probationary_period)

    previous_contract_id = fields.Many2one('hr.contract', compute='_compute_previous_contract')

    @api.depends('employee_id.contract_ids', 'employee_id.contract_ids.date_start', 'date_start')
    def _compute_previous_contract(self):
        for record in self:
            contract_ids = record.employee_id.contract_ids.filtered(
                lambda c: c.id != record.id and c.date_start < record.date_start
            ).sorted('date_start')
            record.previous_contract_id = contract_ids[-1] if contract_ids else False

    tariff_category = fields.Selection([
        ('salary', 'Salary'),
        ('tariff', 'Tariff'),
    ], string='Tariff category', default='salary', compute='_compute_tariff')

    payment_type = fields.Many2one(
        comodel_name='payment.type',
        string='Payment Type',
        # domain="[('code', 'in', ['monthly_salary', 'hourly_salary'])]"
    )
    work_rate = fields.Float(string='Work rate', default=1.0)
    hourly_wage = fields.Monetary(string='Hourly wage')
    wage = fields.Monetary(required=False)
    wage75 = fields.Monetary(string='75% of wage', compute='_compute_wage')
    wage25 = fields.Monetary(string='25% of wage', compute='_compute_wage')
    location = fields.Many2one('hr.work.location', string='Location')

    @api.depends('payment_type')
    def _compute_tariff(self):
        for record in self:
            print(record.payment_type.code, record.payment_type.name)
            if record.payment_type.id == 1:
                record.tariff_category = 'salary'
            elif record.payment_type.id == 2:
                record.tariff_category = 'tariff'
            else:
                record.tariff_category = False

    @api.depends('wage')
    def _compute_wage(self):
        for record in self:
            record.wage75 = record.wage * 0.75
            record.wage25 = record.wage * 0.25

    @api.depends('probationary_period', 'employment_contract_start_date')
    def _compute_probationary_period_end_date(self):
        for employee in self:
            if employee.probationary_period and employee.employment_contract_start_date:
                employee.probationary_period_end_date = fields.Date.from_string(
                    employee.employment_contract_start_date) + relativedelta(months=employee.probationary_period)

    def set_contract_data(self):
        all_contracts = self.env['hr.contract'].search([])
        for record in all_contracts:
            if not record.work_schedule_type:
                record.work_schedule_type = record.employee_id.work_schedule_type
            if not record.department_id:
                record.department_id = record.employee_id.department_id
            if not record.job_id:
                record.job_id = record.employee_id.job_id

        return True

    # overriding _check_current_contract to allow multiple contracts
    @api.constrains('employee_id', 'state', 'kanban_state', 'date_start', 'date_end')
    def _check_current_contract(self):
        # ensure that there is only one primary contract per employee
        for contract in self:
            if contract.state == 'open' and contract.contract_type == 'primary':
                domain = [
                    ('employee_id', '=', contract.employee_id.id),
                    ('state', '=', 'open'),
                    ('contract_type', '=', 'primary'),
                    ('id', '!=', contract.id),
                ]
                if self.search_count(domain):
                    raise ValidationError(_('There can be only one primary contract for an employee.'))
        return True

    def update_moving_date_job(self):
        for record in self:
            if not record.date_start:
                record.date_start = '2000-01-01'
        return True

    def order_number_recompute(self):
        index = 0
        all_contracts = self.env['hr.contract'].search([('company_id', '=', self.env.company.id)])
        for record in all_contracts:
            record.order_number = index
            index = index + 1


class HrContractHistory(models.Model):
    _inherit = 'hr.contract.history'

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # Reference contract is the one with the latest start_date.
        self.env.cr.execute("""CREATE or REPLACE VIEW %s AS (
            WITH contract_information AS (
                SELECT DISTINCT employee_id,
                                company_id,
                                FIRST_VALUE(id) OVER w_partition AS id,
                                MAX(CASE
                                    WHEN state='open' THEN 1
                                    WHEN state='draft' AND kanban_state='done' THEN 1
                                    ELSE 0 END) OVER w_partition AS is_under_contract
                FROM   hr_contract AS contract
                WHERE  contract.state <> 'cancel'
                AND contract.active = true
                WINDOW w_partition AS (
                    PARTITION BY contract.employee_id, contract.company_id
                    ORDER BY
                        CASE
                            WHEN contract.state = 'open' THEN 0
                            WHEN contract.state = 'draft' THEN 1
                            WHEN contract.state = 'close' THEN 2
                            ELSE 3 END,
                        contract.date_start DESC
                    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                )
            )
            SELECT     employee.id AS id,
                       employee.id AS employee_id,
                       employee.active AS active_employee,
                       contract.id AS contract_id,
                       contract_information.is_under_contract::bool AS is_under_contract,
                       employee.first_contract_date AS date_hired,
                       %s
            FROM       hr_contract AS contract
            INNER JOIN contract_information ON contract.id = contract_information.id
            RIGHT JOIN hr_employee AS employee
                ON  contract_information.employee_id = employee.id
                AND contract.company_id = employee.company_id
        )""" % (self._table, self._get_fields()))
