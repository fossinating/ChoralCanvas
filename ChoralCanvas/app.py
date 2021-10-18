from flask import Flask
from flask_appbuilder import SQLA, AppBuilder

from flask_appbuilder.security.sqla.manager import SecurityManager

import config
import sec_models
from sec_views import MyUserDBModelView


class MySecurityManager(SecurityManager):
    print("hi i am called")
    user_model = sec_models.CustomUser
    userdbmodelview = MyUserDBModelView
    registeruser_model = sec_models.RegisterUser


# init Flask
app = Flask(__name__)


app.config.from_object(config)

# Init SQLAlchemy
db = SQLA(app)
# Init F.A.B.
appbuilder = AppBuilder(app, db.session, security_manager_class=MySecurityManager)


# Run the development server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
