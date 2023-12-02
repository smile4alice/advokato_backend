import uuid
from flask import redirect, url_for, request, flash
import flask_login as login
from flask_admin import AdminIndexView, helpers, expose
from flask_admin.contrib.sqla import ModelView
from wtforms import form, fields, validators
from calendarapi.extensions import db, pwd_context, mail
from calendarapi.models import User, UserSecurity


class AdminModelView(ModelView):
    extra_css = ["/static/styles/green_mist.css"]

    create_modal = True
    edit_modal = True

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/admin/login")


def configure_login(app):
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


class LoginForm(form.Form):
    login = fields.StringField(label="Логін", validators=[validators.InputRequired()])
    password = fields.PasswordField(
        label="Пароль", validators=[validators.InputRequired()]
    )

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError("Невірний логін")
        # we're comparing hashes
        if not user.password == user.hash_password(self.password.data):
            raise validators.ValidationError("Невірний пароль")

        if not user.is_active:
            raise validators.ValidationError("Користувач не адміністратор")

    def get_user(self):
        return db.session.query(User).filter_by(username=self.login.data).one_or_none()


class ForgotForm(form.Form):
    email = fields.EmailField(
        "Введіть ваш e-mail",
        validators=[
            validators.DataRequired(),
            validators.Email(),
        ],
    )


class PasswordResetForm(form.Form):
    password = fields.PasswordField("password", validators=[validators.DataRequired()])
    confirm_password = fields.PasswordField(
        "confirm password", validators=[validators.DataRequired()]
    )


class CustomAdminIndexView(AdminIndexView):
    extra_css = AdminModelView.extra_css

    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    @expose("/", methods=("GET", "POST"))
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for(".login_view"))

        return super(CustomAdminIndexView, self).index()

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))

        self._template_args["form"] = form
        return super(CustomAdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))

    @expose("/forgot_password/", methods=["GET", "POST"])
    def forgot_password(self):
        if request.method == "POST":
            email = request.form.get("email")
            user = db.session.query(User).filter_by(email=email).one_or_none()
            if user:
                new_token = uuid.uuid4()
                user_security = (
                    db.session.query(UserSecurity)
                    .filter_by(user_id=user.id)
                    .one_or_none()
                )
                if user_security:
                    user_security.token = new_token
                else:
                    user_security = UserSecurity(user_id=user.id, token=new_token)
                    db.session.add(user_security)

                db.session.commit()

                message = f"Ви отримали цей лист через те, що зробили запит на перевстановлення пароля для облікового запису користувача на {request.host_url}admin"
                message += (
                    "\nБудь ласка, перейдіть на цю сторінку, та оберіть новий пароль: "
                )
                message += f"\n{request.host_url}admin/reset_password/?token={user_security.token}\n"
                message += f"\nВаше користувацьке ім'я: {user.username}"
                message += "\n\nДякуємо за користування нашим сайтом!"

                # mail.send(message=message)
                flash(message, "success")  # TODO видалити
            else:
                flash(f"емейл {email} не знайдено", "error")  # TODO видалити

            flash(
                "На ваш email було відправлено повідомлення з інструкціями для зміни паролю.",
                "success",
            )
            return redirect(request.base_url)
        else:
            form = ForgotForm(request.form)
            return self.render("admin/reset_password.html", form=form)

    @expose("/reset_password/", methods=["GET", "POST"])
    def reset_password(self):
        if request.method == "POST":
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            if password == confirm_password:
                token = request.args.get("token", default=None)
                if token:
                    user_security = (
                        db.session.query(UserSecurity)
                        .filter_by(token=token)
                        .one_or_none()
                    )
                    if user_security:
                        user = (
                            db.session.query(User)
                            .filter_by(id=user_security.user_id)
                            .one_or_none()
                        )
                        user.password = password
                        db.session.delete(user_security)
                        db.session.commit()
                        flash("Пароль успішно змінено.", "success")
                    else:
                        flash("Недійсний token", "error")
                else:
                    flash("Не знайдено аргумент: token", "error")
            else:
                flash("Паролі не співпадають", "error")
                return redirect(request.url)
        else:
            token = request.args.get("token", default=None)
            if token:
                user_security = (
                    db.session.query(UserSecurity).filter_by(token=token).one_or_none()
                )
                if user_security:
                    form = PasswordResetForm(request.form)
                    user = (
                        db.session.query(User)
                        .filter_by(id=user_security.user_id)
                        .one_or_none()
                    )
                    flash("Введіть новий пароль", "info")
                    return self.render("admin/reset_password.html", form=form)
                else:
                    flash("Недійсний token", "error")
            else:
                flash("Не знайдено аргумент: token", "error")

        return redirect(f"{request.host_url}admin")
