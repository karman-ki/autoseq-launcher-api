import os

# Flask settings
FLASK_DEBUG = True  # Do not use debug mode in production

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'] 
# SQLALCHEMY_BINDS = os.environ['CURATION_DB_URL']
SQLALCHEMY_TRACK_MODIFICATIONS = False

MOUNT_POINT_PROBIO = '/nfs/PROBIO/'
MOUNT_POINT_PSFF = '/nfs/PSFF/'

# MOUNT_POINT_PROBIO = '/home/karman/data/PROBIO/'
# MOUNT_POINT_PSFF = '/home/karman/data/PSFF/'

MOUNT_REF_GENOME_PATH = '/nfs/PROBIO/autoseq-genome/autoseq-genome.json'
MOUNT_LIB_PATH = '/nfs/PROBIO/INBOX'
MOUNT_SCRATCH_PATH = '/scratch/tmp/liqbio-tmp/'

LIQBIO_PROD = '. /nfs/PROBIO/liqbio-dotfiles/.bash_profile'

ANCHORAGE_ADDR = "anchorage.meb.ki.se"
ANCHORAGE_USERNAME = "prosp"
ANCHORAGE_PWD = "16Vinter16"

SCALAR_ADDR = "anchorage.meb.ki.se"
SCALAR_USERNAME = "prosp"
SCALAR_PWD = "16Vinter16"

VECTOR_ADDR = "anchorage.meb.ki.se"
VECTOR_USERNAME = "prosp"
VECTOR_PWD = "16Vinter16"
