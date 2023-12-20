from celery import current_app
from markupsafe import Markup
from wtforms.validators import DataRequired
from wtforms import TextAreaField, FileField

from calendarapi.admin.base_admin import AdminModelView
from calendarapi.admin.commons.formatters import ThumbnailFormatter, format_as_markup
from calendarapi.admin.commons.validators import ImageValidator
from calendarapi.commons.exeptions import (
    DATA_REQUIRED,
    REQ_HTML_M,
    REQ_IMAGE,
    REQ_MAX_LEN,
)
from calendarapi.commons.utils import custom_update_file

MAIN_PAGE_INFO = "Відображається на головній сторінці під блоком Hero."
OUR_TEAM_PAGE_INFO = 'Відображається на сторінці "Про компанію".'


class AboutCompanyModelView(AdminModelView):
    can_set_page_size = True
    can_create = False
    can_delete = False

    column_labels = {
        "main_page_photo_path": "Фото(головна)",
        "our_team_page_photo_path": "Фото(про компанію)",
        "main_page_description": "Опис(головна)",
        "our_team_page_description": "Опис(про компанію)",
    }
    column_list = [
        "main_page_photo_path",
        "our_team_page_photo_path",
        "main_page_description",
        "our_team_page_description",
    ]
    form_columns = [
        "main_page_description",
        "our_team_page_description",
        "main_page_photo_path",
        "our_team_page_photo_path",
    ]
    column_descriptions = {
        "main_page_photo_path": MAIN_PAGE_INFO,
        "our_team_page_photo_path": OUR_TEAM_PAGE_INFO,
        "main_page_description": MAIN_PAGE_INFO,
        "our_team_page_description": OUR_TEAM_PAGE_INFO,
    }

    column_formatters = {
        "main_page_photo_path": ThumbnailFormatter(),
        "our_team_page_photo_path": ThumbnailFormatter(),
        "our_team_page_description": format_as_markup,
    }

    form_extra_fields = {
        "main_page_photo_path": FileField(
            label="Виберіть фото для головної сторінки.",
            validators=[ImageValidator()],
            description=f"{MAIN_PAGE_INFO} {REQ_IMAGE}",
        ),
        "our_team_page_photo_path": FileField(
            'Виберіть фото для сторінки "Наша компанія".',
            validators=[ImageValidator()],
            description=f"{OUR_TEAM_PAGE_INFO} {REQ_IMAGE}",
        ),
        "main_page_description": TextAreaField(
            label="Короткий опис для головної сторінки. ",
            render_kw={"class": "form-control", "rows": 5, "maxlength": 500},
            validators=[DataRequired(message=DATA_REQUIRED)],
            description=f"{MAIN_PAGE_INFO} {REQ_MAX_LEN % 500}",
        ),
        "our_team_page_description": TextAreaField(
            'Опис для сторінки "Наша компанія".',
            render_kw={"class": "form-control", "rows": 5, "maxlength": 3000},
            validators=[DataRequired(message=DATA_REQUIRED)],
            description=Markup(
                f"{OUR_TEAM_PAGE_INFO} {REQ_MAX_LEN % 3000} {REQ_HTML_M}"
            ),
        ),
    }

    def on_model_change(self, form, model, is_created):
        custom_update_file(model, form, field_name="main_page_photo_path")
        custom_update_file(model, form, field_name="our_team_page_photo_path")
        return super().on_model_change(form, model, is_created)
