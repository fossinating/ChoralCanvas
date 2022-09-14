import secret_manager

SECRET_KEY = secret_manager.SECRET_KEY
WTF_CSRF_SECRET_KEY = secret_manager.WTF_CSRF_SECRET_KEY

SECURITY_PASSWORD_HASH = "argon2"

# user registration information
SECURITY_REGISTERABLE = True
SECURITY_USERNAME_ENABLE = True
SECURITY_USERNAME_REQUIRED = True
SECURITY_PASSWORD_CHECK_BREACHED = True
SECURITY_PASSWORD_BREACHED_COUNT = 50
SECURITY_PASSWORD_COMPLEXITY_CHECKER = "zxcvbn"

# Database information
DB_TYPE = "postgresql"
DB_USERNAME = "postgres"
DB_PASSWORD = secret_manager.DB_PASSWORD
DB_PATH = "localhost"
DB_DATABASE_NAME = "choralcanvas"
SQLALCHEMY_DATABASE_URI = f"{DB_TYPE}://{DB_USERNAME}:{DB_PASSWORD}@{DB_PATH}/{DB_DATABASE_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

AUTH_TYPE = 1  # Database Authentication
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = 'Public'
FAB_PASSWORD_COMPLEXITY_ENABLED = True

# Config for Flask-WTF Recaptcha necessary for user registration
RECAPTCHA_PUBLIC_KEY = secret_manager.RECAPTCHA_PUBLIC_KEY
RECAPTCHA_PRIVATE_KEY = secret_manager.RECAPTCHA_PRIVATE_KEY

# Config for Flask-Mail necessary for user registration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_USE_TLS = True
MAIL_PORT = 587
MAIL_USERNAME = 'choralcanvas@gmail.com'
MAIL_PASSWORD = secret_manager.MAIL_PASSWORD
MAIL_DEFAULT_SENDER = ("Choral Canvas Registration", 'choralcanvas+registration@gmail.com')
