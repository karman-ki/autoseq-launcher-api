import os

# Flask settings
FLASK_DEBUG = True  # Do not use debug mode in production

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://referral_writer:ProbioWriter@127.0.0.1:5432/autoseq_launcher"
SQLALCHEMY_TRACK_MODIFICATIONS = False

MOUNT_POINT_PROBIO = '/nfs/PROBIO/'
#MOUNT_POINT_PROBIO = '/nfs/PROBIO/launcherTest/'
MOUNT_POINT_PSFF = '/nfs/PSFF/'
MOUNT_POINT_LPC = '/nfs/PROBIO2/high_risk_localized_Ashkan/'

MOUNT_REF_GENOME_PATH = '/nfs/PROBIO/autoseq-genome/autoseq-genome.json'
MOUNT_LIB_PATH = '/nfs/PROBIO/INBOX'
MOUNT_SCRATCH_PATH = '/scratch/tmp/liqbio-tmp/'
LIQBIO_PROD = 'source /nfs/PROBIO/liqbio-dotfiles/.bash_profile'

ANCHORAGE_ADDR = "anchorage.meb.ki.se"
ANCHORAGE_USERNAME = "prosp"
ANCHORAGE_PWD = "Swedishmeatball15"

GRYFFINDOR_ADDR = "c8gryffindor01.ki.se"
GRYFFINDOR_USERNAME = "prosp"
GRYFFINDOR_PWD = "Swedishmeatball15"

VECTOR_ADDR = "vector.meb.ki.se"
VECTOR_USERNAME = "prosp"
VECTOR_PWD = ""
