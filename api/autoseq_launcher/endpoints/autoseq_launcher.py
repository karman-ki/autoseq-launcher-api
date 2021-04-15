import logging
from flask_restplus import Resource
from api.restplus import api
from api.autoseq_launcher.business import *
# from api.autoseq_launcher.serializers import *
from api.autoseq_launcher.parsers import *
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

@ctm.route('/upload_orderform')
@api.response(200, 'Barcode generated successfully')
@api.response(400, 'No data found')
class LeaderboardUploadOrdeform(Resource):
    @api.expect(upload_file_arguments, validate=True)
    def post(self):
        """
        Save the sample list in the sequence table
        ```

        ```
        """
        args = upload_file_arguments.parse_args()
        project_name = args['project_name']
        sample_arr = args['sample_arr']
        file_name = args['file_name']
        result, errorcode = upload_orderform(project_name, sample_arr, file_name)
        return result, errorcode 

@ctm.route('/sample_generate_barcode')
@api.response(200, 'Barcode generated successfully')
@api.response(400, 'Database connection failed')               
class GenerateProjectBarcode(Resource):
    @api.expect(processing_step_arguments, validate=True)       
    def post(self):
        """
        Generate the barcode file for sample list
        ```

        ```
        """
        args = processing_step_arguments.parse_args()
        project_name = args['project_name']
        ssid = args['ssid']
        sid = args['sid']
        germline = args['germline']
        result, errorcode = sample_generate_barcode(project_name, ssid, sid, germline)
        return result, errorcode

# @ctm.route('/generate_barcode')
# @api.response(200, 'Barcode generated successfully')
# @api.response(400, 'Database connection failed')               
# class GenerateProjectBarcode(Resource):
#     @api.expect(generate_barcode_arguments, validate=True)       
#     def post(self):
#         """
#         Generate the barcode file for sample list
#         ```

#         ```
#         """
#         args = generate_barcode_arguments.parse_args()
#         project_name = args['project_name']
#         search_pattern = args['search_pattern']
#         sample_arr = args['sample_arr']
#         file_name = args['file_name']
#         result, errorcode = generate_barcodes(project_name, search_pattern, sample_arr, file_name)
#         return result, errorcode


@ctm.route('/generate_config')
@api.response(200, 'Generate Config successfully')
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
        result, errorcode = generate_config_file(barcode_id)
        return result, errorcode

@ctm.route('/start_pipline')
@api.response(200, 'Pipeline started successfully')
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

@ctm.route('/view_analysis_info')
@api.response(200, 'Get the analysis information')
@api.response(400, 'No data found')
class ViewAnalysisInfo(Resource):
    @api.expect(start_pipeline_arguments, validate=True)       
    def post(self):
        """
        Fetch all analysis information
        ```

        ```
        """
        args = start_pipeline_arguments.parse_args()
        project_id = args['project_id']
        result, errorcode = view_analysis_info(project_id)
        return result, errorcode 

@ctm.route('/edit_analysis_info')
@api.response(200, 'Edit the analysis information')
@api.response(400, 'No data found')
class EditAnalysisInfo(Resource):
    @api.expect(start_pipeline_arguments, validate=True)       
    def post(self):
        """
        Edit the cores and machine type in the analysis
        ```

        ```
        """
        args = start_pipeline_arguments.parse_args()
        project_id = args['project_id']
        result, errorcode = edit_analysis_info(project_id)
        return result, errorcode 

@ctm.route('/update_analysis_info')
@api.response(200, 'Update the analysis information')
@api.response(400, 'No data found')
class UpdateAnalysisInfo(Resource):
    @api.expect(update_pipeline_arguments, validate=True)       
    def post(self):
        """
        Save the analysis info in the projects table
        ```

        ```
        """
        args = update_pipeline_arguments.parse_args()
        project_id = args['project_id']
        cores = args['cores']
        machine_type = args['machine_type']
        result, errorcode = update_analysis_info(project_id, cores, machine_type)
        return result, errorcode

@ctm.route('/view_pipeline_log')
@api.response(200, 'Get the pipeline log information')
@api.response(400, 'No data found')
class ViewAnalysisLogInfo(Resource):
    @api.expect(view_pipeline_log_arguments, validate=True)       
    def post(self):
        """
        Get the pipeline log information
        ```

        ```
        """
        args = view_pipeline_log_arguments.parse_args()
        job_id = args['job_id']
        result, errorcode = view_log_analysis_info(job_id)
        return result, errorcode 


@ctm.route('/get_job_status')
@api.response(200, 'Update the sample information')
@api.response(400, 'No data found')
class GetJobStatusInfo(Resource):
    @api.expect(view_pipeline_log_arguments, validate=True)       
    def post(self):
        """
        Save the sample list in the sequence table
        ```

        ```
        """
        args = view_pipeline_log_arguments.parse_args()
        job_id = args['job_id']
        result, errorcode = get_job_status_info(job_id)
        return result, errorcode  