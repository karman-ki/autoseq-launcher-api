from flask_restplus import reqparse

generate_barcode_arguments = reqparse.RequestParser()
generate_barcode_arguments.add_argument('project_name', choices=('PROBIO', 'PSFF'), required=True,
                              help="valid Project names: 'PROBIO', 'PSFF'")
generate_barcode_arguments.add_argument('search_pattern', type=str, required=True,  help='example : PN20210210')

generate_config_arguments = reqparse.RequestParser()
generate_config_arguments.add_argument('barcode_id', type=str, required=True)


start_pipeline_arguments = reqparse.RequestParser()
start_pipeline_arguments.add_argument('project_id', type=str, required=True)