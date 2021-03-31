import logging
from flask_restplus import Resource
from api.restplus import api
from api.task_manager.business import *
# from api.task_manager.serializers import *
from api.task_manager.parsers import *
from flask import request



log = logging.getLogger(__name__)
ctm = api.namespace('CTM', description='API')

@ctm.route('/connection')
@api.response(200, 'Database connected successfully')
@api.response(400, 'Database connection failed')               
class DBConnection(Resource):           
    def get(self):
        """
        Check the database connection
        ```

        ```
        """
        result, errorcode = check_db_connection()
        return result, errorcode



@ctm.route('/barcode_list')
@api.response(200, 'Database connected successfully')
@api.response(400, 'Database connection failed')               
class GetBarcodeList(Resource):           
    def get(self):
        """
        Get the barcode generate information
        ```

        ```
        """
        result, errorcode = get_barcode_list()
        return result, errorcode


@ctm.route('/project_list')
@api.response(200, 'Database connected successfully')
@api.response(400, 'Database connection failed')               
class GetProjectList(Resource):           
    def get(self):
        """
        Get the project information
        ```

        ```
        """
        result, errorcode = get_project_list()
        return result, errorcode

@ctm.route('/job_list')
@api.response(200, 'Database connected successfully')
@api.response(400, 'Database connection failed')               
class GetJobList(Resource):           
    def get(self):
        """
        Get the Job information
        ```

        ```
        """
        result, errorcode = get_job_list()
        return result, errorcode

@ctm.route('/save/ordeform')
@api.response(200, 'Update the sample information')
@api.response(400, 'No data found')
class LeaderboardSaveOrdeform(Resource):
    @api.expect(save_file_arguments, validate=True)
    def post(self):
        """
        Save the sample list in the sequence table
        ```

        ```
        """
        args = save_file_arguments.parse_args()
        result, errorcode = save_orderform(args['data'])
        return result, errorcode 

@ctm.route('/generate_barcode')
@api.response(200, 'Database connected successfully')
@api.response(400, 'Database connection failed')               
class GenerateProjectBarcode(Resource):
    @api.expect(generate_barcode_arguments, validate=True)       
    def post(self):
        """
        Generate the barcode file for sample list
        ```

        ```
        """
        args = generate_barcode_arguments.parse_args()
        project_name = args['project_name']
        search_pattern = args['search_pattern']
        sample_arr = args['sample_arr']
        file_name = args['file_name']
        result, errorcode = generate_barcodes(project_name, search_pattern, sample_arr, file_name)
        return result, errorcode


@ctm.route('/generate_config')
@api.response(200, 'Database connected successfully')
@api.response(400, 'Database connection failed')               
class GenerateProjectConfig(Resource):
    @api.expect(generate_config_arguments, validate=True)       
    def post(self):
        """
        Generate the config file for the barcode
        ```

        ```
        """
        args = generate_config_arguments.parse_args()
        barcode_id = args['barcode_id']
        result, errorcode = generate_configs(barcode_id)
        return result, errorcode

@ctm.route('/start_pipline')
@api.response(200, 'Database connected successfully')
@api.response(400, 'Database connection failed')               
class GenerateStartPipeline(Resource):
    @api.expect(start_pipeline_arguments, validate=True)       
    def post(self):
        """
        Generate the pipeline
        ```

        ```
        """
        args = start_pipeline_arguments.parse_args()
        project_id = args['project_id']
        result, errorcode = start_pipeline(project_id)
        return result, errorcode