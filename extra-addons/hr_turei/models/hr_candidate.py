from odoo import api, models, fields, _

class HrCandidate(models.Model):
    _inherit = 'hr.candidate'

    # -------------------------------------------------------------------------
    # DATOS PERSONALES
    # -------------------------------------------------------------------------
    age = fields.Integer(string='Age')
    gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
        ],
        string='Gender',
    )
    marital_status = fields.Selection(
        selection=[
            ('single', 'Single'),
            ('married', 'Married'),
            ('divorced', 'Divorced'),
            ('widowed', 'Widowed'),
            ('consensual_union', 'Consensual Union'),
        ],
        string='Marital Status',
    )
    birthplace = fields.Char(string='Birthplace')
    identity_number = fields.Char(string='Identity Number')
    home_address = fields.Char(string='Home Address')
    municipality = fields.Char(string='Municipality')
    province = fields.Char(string='Province')

    # Organizaciones a las que pertenece
    belongs_pcc = fields.Boolean(string='PCC')
    belongs_ujc = fields.Boolean(string='UJC')
    belongs_cdr = fields.Boolean(string='CDR')
    belongs_fmc = fields.Boolean(string='FMC')
    belongs_bpd = fields.Boolean(string='BPD')
    belongs_ur = fields.Boolean(string='UR')
    belongs_ctc = fields.Boolean(string='CTC')
    other_organizations = fields.Char(string='Other Organizations')

    # Tallas
    shoe_size = fields.Char(string='Shoe Size')
    skirt_pants_size = fields.Char(string='Skirt/Pants Size')
    blouse_shirt_size = fields.Char(string='Blouse/Shirt Size')

    # Datos familiares
    family_member_ids = fields.One2many(
        comodel_name='hr.candidate.family.member',
        inverse_name='candidate_id',
        string='Family Members',
        copy=True,
    )

    # -------------------------------------------------------------------------
    # NIVEL DE ESCOLARIDAD
    # -------------------------------------------------------------------------
    educational_level = fields.Selection(
        selection=[
            ('chiv', 'Chiv.'),
            ('technical_medium', 'Technical Medium'),
            ('2nd_grade', '2nd Grade'),
            ('9th_grade', '9th Grade'),
            ('6th_grade', '6th Grade'),
            ('illiterate', 'Illiterate'),
        ],
        string='Educational Level',
    )
    specialty = fields.Char(string='Specialty')
    other_studies = fields.Text(string='Other Studies')
    self_taught_knowledge = fields.Text(string='Self-taught Knowledge and Skills')

    # -------------------------------------------------------------------------
    # DATOS LABORALES
    # -------------------------------------------------------------------------
    currently_employed = fields.Boolean(string='Currently Employed')
    years_of_experience = fields.Integer(string='Years of Work Experience')
    current_workplace = fields.Char(string='Current Workplace')
    work_address = fields.Char(string='Work Address')
    work_phone = fields.Char(string='Work Phone')
    work_municipality = fields.Char(string='Work Municipality')
    work_province = fields.Char(string='Work Province')
    current_position = fields.Char(string='Current Position')
    current_salary = fields.Float(string='Current Salary')

    # Historial de otros centros laborales
    work_experience_ids = fields.One2many(
        comodel_name='hr.candidate.work.experience',
        inverse_name='candidate_id',
        string='Work Experience',
        copy=True,
    )

    # -------------------------------------------------------------------------
    # OTROS DATOS DE INTERÉS
    # -------------------------------------------------------------------------
    last_resignation_reason = fields.Text(string='Reason for Last Resignation')
    has_held_management_position = fields.Boolean(string='Has Held Management Position')

    # Cargos de dirección
    management_position_ids = fields.One2many(
        comodel_name='hr.candidate.management.position',
        inverse_name='candidate_id',
        string='Management Positions',
        copy=True,
    )

    work_achievements = fields.Text(string='Work Achievements')
    # motivation_for_position = fields.Text(string='Motivation for Position')


class HrCandidateFamilyMember(models.Model):
    _name = 'hr.candidate.family.member'
    _description = 'Candidate Family Member'

    candidate_id = fields.Many2one(
        comodel_name='hr.candidate',
        string='Candidate',
        required=True,
        ondelete='cascade',
    )
    relation_type = fields.Selection(
        selection=[
            ('father', 'Father'),
            ('mother', 'Mother'),
            ('spouse', 'Spouse'),
            ('cohabitant', 'Cohabitant'),
            ('child', 'Child'),
        ],
        string='Relation Type',
        required=True,
    )
    name = fields.Char(string='Name')
    alive = fields.Boolean(string='Alive')
    age = fields.Integer(string='Age')
    relationship = fields.Char(string='Relationship')


class HrCandidateWorkExperience(models.Model):
    _name = 'hr.candidate.work.experience'
    _description = 'Candidate Work Experience'

    candidate_id = fields.Many2one(
        comodel_name='hr.candidate',
        string='Candidate',
        required=True,
        ondelete='cascade',
    )
    company_name = fields.Char(string='Company Name')
    position = fields.Char(string='Position')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    current = fields.Boolean(string='Current')


class HrCandidateManagementPosition(models.Model):
    _name = 'hr.candidate.management.position'
    _description = 'Candidate Management Position'

    candidate_id = fields.Many2one(
        comodel_name='hr.candidate',
        string='Candidate',
        required=True,
        ondelete='cascade',
    )
    company_name = fields.Char(string='Company Name')
    position = fields.Char(string='Position')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')