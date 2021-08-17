from flask_restplus import reqparse

generate_barcode_arguments = reqparse.RequestParser()
generate_barcode_arguments.add_argument('project_name', choices=('PROBIO', 'PSFF'), required=True,
                              help="valid Project names: 'PROBIO', 'PSFF'")
generate_barcode_arguments.add_argument('search_pattern', type=str, required=True,  help='example : PN20210210')
generate_barcode_arguments.add_argument('sample_arr',  type=str, required=True, help="Jsondata")
generate_barcode_arguments.add_argument('file_name',  type=str, required=True, help="Upload file name")

generate_config_arguments = reqparse.RequestParser()
generate_config_arguments.add_argument('barcode_id', type=str, required=True)

get_pipeline_arguments = reqparse.RequestParser()
get_pipeline_arguments.add_argument('project_id', type=str, required=True)

stop_pipeline_arguments = reqparse.RequestParser()
stop_pipeline_arguments.add_argument('project_id', type=str, required=True)

upload_file_arguments = reqparse.RequestParser()
upload_file_arguments.add_argument('project_name', choices=('PROBIO', 'PSFF'), required=True,
                              help="valid Project names: 'PROBIO', 'PSFF'")
upload_file_arguments.add_argument('anch_user',  type=str, required=True, help="Provide anchorage user")
upload_file_arguments.add_argument('anch_pwd',  type=str, required=True, help="Provide anchorage password")
upload_file_arguments.add_argument('sample_arr',  type=str, required=True, help="Jsondata")
upload_file_arguments.add_argument('file_name',  type=str, required=True, help="Upload file name")

processing_step_arguments = reqparse.RequestParser()
processing_step_arguments.add_argument('project_name', choices=('PROBIO', 'PSFF'), required=True,
                              help="valid Project names: 'PROBIO', 'PSFF'")
processing_step_arguments.add_argument('anch_user',  type=str, required=True, help="Provide anchorage user")
processing_step_arguments.add_argument('anch_pwd',  type=str, required=True, help="Provide anchorage password")
processing_step_arguments.add_argument('samples', type=str, required=True,  help='[] String')

update_pipeline_arguments = reqparse.RequestParser()
update_pipeline_arguments.add_argument('project_id', type=str, required=True)
update_pipeline_arguments.add_argument('cores', type=str, required=True)
update_pipeline_arguments.add_argument('machine_type', type=str, required=True)

get_job_id_arguments = reqparse.RequestParser()
get_job_id_arguments.add_argument('job_id', type=str, required=True)

view_out_log_arguments = reqparse.RequestParser()
view_out_log_arguments.add_argument('out_path', type=str, required=True)

sync_data_arguments = reqparse.RequestParser()
sync_data_arguments.add_argument('project_name', type=str, required=True)
sync_data_arguments.add_argument('cutm_id', type=str, required=True)
sync_data_arguments.add_argument('anch_user',  type=str, required=True, help="Provide anchorage user")
sync_data_arguments.add_argument('anch_pwd',  type=str, required=True, help="Provide anchorage password")