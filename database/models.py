from database import db as pssql

class CTMBarcode(pssql.Model):
    __tablename__ = "barcodes_t"
    b_id = pssql.Column(pssql.Integer, primary_key=True, nullable=False)
    project_name  = pssql.Column(pssql.String)
    search_pattern = pssql.Column(pssql.String)
    barcode_path = pssql.Column(pssql.String)
    bar_status  = pssql.Column(pssql.String)
    create_time  = pssql.Column(pssql.String)
    update_time  = pssql.Column(pssql.String)

    # def __init__(self, row_dict):

    #     self.b_id = row_dict.get('b_id', None)
    #     self.project_name = row_dict.get('project_name', None)
    #     self.search_pattern = row_dict.get('search_pattern', None)
    #     self.barcode_path = row_dict.get('barcode_path', None)
    #     self.bar_status = row_dict.get('bar_status', None)
    #     self.create_time = row_dict.get('create_time', None)
    #     self.update_time = row_dict.get('update_time', None)

    def __repr__(self): 
        return "<CTMBarcode (b_id='%s', project_name='%s', search_pattern='%s',)>" % (self.b_id,self.project_name,self.search_pattern)


class CTMProject(pssql.Model):
    __tablename__ = "projects_t"
    p_id = pssql.Column(pssql.Integer, primary_key=True, nullable=False)
    barcode_id = pssql.Column(pssql.Integer, nullable=False)
    sample_id = pssql.Column(pssql.String, nullable=False)
    config_path = pssql.Column(pssql.String)
    pro_status  = pssql.Column(pssql.String, nullable=False)
    cores = pssql.Column(pssql.Integer, nullable=False)
    create_time  = pssql.Column(pssql.String, nullable=False)
    update_time  = pssql.Column(pssql.String, nullable=False)

    def __init__(self, row_dict):

        self.p_id = row_dict.get('p_id', None)
        self.barcode_id = row_dict.get('barcode_id', None)
        self.sample_id = row_dict.get('sample_id', None)
        self.config_path = row_dict.get('config_path', None)
        self.pro_status = row_dict.get('pro_status', None)
        self.cores = row_dict.get('cores', None)
        self.create_time = row_dict.get('create_time', None)
        self.update_time = row_dict.get('update_time', None)

    def __repr__(self): 
        return "<CTMProject (p_id='%s', barcode_id='%s', sample_id='%s', pro_status='%s', config_path='%s')>" % (self.p_id,self.barcode_id,self.sample_id,self.pro_status,self.config_path)