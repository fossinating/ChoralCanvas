from flask_appbuilder.security.views import UserDBModelView
from flask_babel import lazy_gettext


class MyUserDBModelView(UserDBModelView):
    """
        View that add DB specifics to CustomUser view.
        Override to implement your own custom view.
        Then override userdbmodelview property on SecurityManager
    """

    show_fieldsets = [
        (lazy_gettext('CustomUser info'),
         {'fields': ['display_name', 'username', 'active', 'roles', 'login_count', 'extra']}),
        (lazy_gettext('Personal Info'),
         {'fields': ['email'], 'expanded': True}),
        (lazy_gettext('Audit Info'),
         {'fields': ['last_login', 'fail_login_count', 'created_on',
                     'created_by', 'changed_on', 'changed_by'], 'expanded': False}),
    ]

    user_show_fieldsets = [
        (lazy_gettext('CustomUser info'),
         {'fields': ['display_name', 'username', 'active', 'roles', 'login_count', 'extra']}),
        (lazy_gettext('Personal Info'),
         {'fields': ['email'], 'expanded': True}),
    ]

    add_columns = [
        'display_name'
        'username',
        'active',
        'email',
        'roles',
        'extra',
        'password',
        'conf_password'
    ]
    list_columns = [
        'display_name',
        'username',
        'email',
        'active',
        'roles'
    ]
    edit_columns = [
        'display_name',
        'username',
        'active',
        'email',
        'roles',
        'extra'
    ]