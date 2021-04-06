from flask_restplus import reqparse

generate_barcode_arguments = reqparse.RequestParser()
generate_barcode_arguments.add_argument('project_name', choices=('PROBIO', 'PSFF'), required=True,
                              help="valid Project names: 'PROBIO', 'PSFF'")
generate_barcode_arguments.add_argument('search_pattern', type=str, required=True,  help='example : PN20210210')
generate_barcode_arguments.add_argument('sample_arr',  type=str, required=True, help="Jsondata")
generate_barcode_arguments.add_argument('file_name',  type=str, required=True, help="Upload file name")

generate_config_arguments = reqparse.RequestParser()
generate_config_arguments.add_argument('barcode_id', type=str, required=True)

start_pipeline_arguments = reqparse.RequestParser()
start_pipeline_arguments.add_argument('project_id', type=str, required=True)

save_file_arguments = reqparse.RequestParser()
save_file_arguments.add_argument('data',  type=str, required=True, help="Jsondata")

update_pipeline_arguments = reqparse.RequestParser()
update_pipeline_arguments.add_argument('project_id', type=str, required=True)
update_pipeline_arguments.add_argument('cores', type=str, required=True)
update_pipeline_arguments.add_argument('machine_type', type=str, required=True)

view_pipeline_log_arguments = reqparse.RequestParser()
view_pipeline_log_arguments.add_argument('job_id', type=str, required=True)