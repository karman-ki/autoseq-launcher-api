from flask_restplus import fields
from api.restplus import api

lb_subject_data = api.model('LBSubjectStatus', {
    'id': fields.String(description='Auto increment id for subject record'),
    'subject_id': fields.String(description='Unique subject id of the patient'),
    'dob': fields.String(description='Date of birth of the patient'),
    'enrollment_id': fields.String(description='enrollment id of the patient'),
    'enrollment_status': fields.String(description='enrollment staus of the patient'),
    'process_name': fields.String(description='Process name'),
    'site_name': fields.String(description='Hostpital name'),
    'inclusion': fields.String(description='Binary stautus 1 or 0 '),
    'biobank': fields.String(description='Binary stautus 1 or 0 '),
    'sequencing': fields.String(description='Binary stautus 1 or 0 '),
    'curation': fields.String(description='Binary stautus 1 or 0 '),
    'randomization': fields.String(description='Binary stautus 1 or 0')

})

header = api.model('Subject status header', {'key':fields.String(description='Column name') , 'title': fields.String(description='Column display name')})
leaderboard_sub_data_list = api.model('Subject Staus DB Data', { 'status':fields.Boolean(required=True), 'data': fields.List(fields.Nested(lb_subject_data)), 'header': fields.List(fields.Nested(header)), 'error': fields.String()})


probio_ref_data = api.model('ProbioBloodReferral', {
    'crid': fields.String(description='referral id for reach record'),
    'pnr': fields.String(description='personal number of patient'),
    'rid': fields.String(description='referral id'),
    'datum': fields.String(description='date and of entry'),
    'tid': fields.String(description='tid of sample'),
    'sign': fields.String(description='binary stautus 1 or 0 '),
    'countyletter': fields.String(description='hospital code'),
    'new': fields.String(description='new'),
    'progression': fields.String(description='state of progression'),
    'follow_up': fields.String(description='status to follow_up'),
    'cf_dna1': fields.String(description='proof read 1'),
    'cf_dna2': fields.String(description='proof read 2'),
    'cf_dna3': fields.String(description='proof read 3'),
    'kommentar': fields.String(description='comments of each sample'),
    'filnamn': fields.String(description='path to sample report in pdf '),

})

ref_header = api.model('Probio header', {'key':fields.String(description='Column name') , 'title': fields.String(description='Column display name')})
probio_ref_data_list = api.model('Referral DB Data', { 'status':fields.Boolean(required=True), 'data': fields.List(fields.Nested(probio_ref_data)), 'header': fields.List(fields.Nested(ref_header)), 'error': fields.String()})