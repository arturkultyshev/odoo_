{
    'name': 'Employee Extended Profile',
    'version': '15.0.1.0.1',
    'summary': """Manages Employee Extended Profile""",
    'description': """This module is used to tracking employee's extended profile""",
    'category': "Generic Modules/Human Resources",
    'author': 'Norsec Tech',
    'company': 'Norsec Tech',
    'website': "https://www.norsec.tech",
    'depends': ['base', 
                'hr', 
                'hr_skills', 
                'hr_contract', 
                'base_address_city', 
            ],
    'data': [
        'security/ir.model.access.csv',
        'data/res_country_data.xml',
        'data/schedule_actions.xml',
        'data/banks.xml',
        'data/payment_type.xml',
        'data/languages.xml',
        'data/language_level.xml',
        'data/nationality.xml',
        'data/res_country_state.xml',
        'data/veteran_status.xml',
        'data/res_city.xml',
        'data/work_locations.xml',
        'views/res_user_view_extended.xml',
        'views/extended_profile.xml',
        'views/personal_info.xml',
        'views/family_members_info.xml',
        'views/education.xml',
        'views/military_duty.xml',
        'views/work_information.xml',
        'views/kanban_view.xml',
        'views/list_view.xml',
        'views/hr_contract_views.xml',
        'views/wages.xml',
        'views/hr_language_views.xml',
        'views/payment_type_views.xml',
        'views/hr_employee_nationality_views.xml',
        'views/hr_language_level_views.xml',
        'views/hr_employee_veteran_status_views.xml',
        'views/configuration_menuitem.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
