import os
# Basic config with security for forms and session cookie

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
CSRF_ENABLED = True
SECRET_KEY = 'thisismyscretkey'


AUTH_TYPE = 1 # Database Authentication
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = 'Public'
FAB_PASSWORD_COMPLEXITY_ENABLED = True

# Config for Flask-WTF Recaptcha necessary for user registration
RECAPTCHA_PUBLIC_KEY = '6Ldbx8scAAAAALdg3nyp3P6epVWaVo24h_taOYBn'
RECAPTCHA_PRIVATE_KEY = '6Ldbx8scAAAAAElA7Rfs547xk0WUPlO7ltH2PH3q'

# Config for Flask-Mail necessary for user registration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_USE_TLS = True
MAIL_PORT = 587
MAIL_USERNAME = 'choralcanvas@gmail.com'
MAIL_PASSWORD = 'dbljrjhzcepscqdb'
MAIL_DEFAULT_SENDER = ("Choral Canvas Registration", 'choralcanvas+registration@gmail.com')
