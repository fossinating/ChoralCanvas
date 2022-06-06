
SECRET_KEY = 'thisismyscretkey'
WTF_CSRF_SECRET_KEY = "wtfkey"

SECURITY_PASSWORD_HASH = "argon2"

# user registration information
SECURITY_REGISTERABLE = True
SECURITY_USERNAME_ENABLE = True
SECURITY_USERNAME_REQUIRED = True
SECURITY_PASSWORD_CHECK_BREACHED = True
SECURITY_PASSWORD_BREACHED_COUNT = 50
SECURITY_PASSWORD_COMPLEXITY_CHECKER = "zxcvbn"

AUTH_TYPE = 1  # Database Authentication
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
