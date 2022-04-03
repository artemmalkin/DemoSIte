from flask import url_for, abort
from flask_admin import AdminIndexView, Admin, helpers as admin_helpers
from flask_admin.contrib import sqla
from flask_security import SQLAlchemyUserDatastore, Security, current_user
from werkzeug.utils import redirect

from app import app, db
from models import Role, User, Notification

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


class BaseView(sqla.ModelView):
    can_export = True
    can_view_details = True

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('login'))


class RegularView(BaseView):
    def is_accessible(self):
        # set accessibility...
        if not current_user.is_authenticated:
            return False

        # roles not tied to ascending permissions...
        if not current_user.has_role('export'):
            self.can_export = False

        # roles with ascending permissions...
        if current_user.has_role('admin'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            self.can_export = True
            return True
        if current_user.has_role('supervisor'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = False
            return True
        if current_user.has_role('user'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = False
            return True
        if current_user.has_role('create'):
            self.can_create = True
            self.can_edit = False
            self.can_delete = False
            return True
        if current_user.has_role('read'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True
        return False


class LookupView(BaseView):
    def is_accessible(self):
        # set accessibility...
        if not current_user.is_authenticated:
            return False

        # roles not tied to ascending permissions...
        if not current_user.has_role('export'):
            self.can_export = False

        # roles with ascending permissions...
        if current_user.has_role('admin'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            self.can_export = True
            return True
        if current_user.has_role('supervisor'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = False
            return True
        if current_user.has_role('user'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True
        if current_user.has_role('create'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True
        if current_user.has_role('read'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True
        return False


class SuperView(BaseView):
    can_export = True

    def is_accessible(self):
        if not current_user.is_authenticated:
            return False
        if current_user.has_role('admin'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True
        return False


# class MyAdminIndexView(AdminIndexView):
#
#     @expose('/')
#     def index(self):
#         if current_user.is_authenticated:
#             return super(MyAdminIndexView, self).index()
#         return redirect(url_for('login'))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )


admin = Admin(app, name='DemoSite', index_view=AdminIndexView(), template_mode='bootstrap3')


class UserView(SuperView):
    column_exclude_list = ['password']
    column_searchable_list = ['login']
    column_editable_list = ['login']


admin.add_view(SuperView(Role, db.session, name='Роли'))
admin.add_view(UserView(User, db.session, name='Пользователи'))
admin.add_view(RegularView(Notification, db.session, name='Уведомления'))
