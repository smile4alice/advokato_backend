from flask import current_app
from marshmallow import pre_dump
from calendarapi.models import Reviews
from calendarapi.extensions import fm, ma, db


class ReviewsSchema(fm.SQLAlchemyAutoSchema):
    name = ma.fields.String(
        required=True, validate=ma.fields.validate.Length(min=4, max=100)
    )
    position = ma.fields.String(
        required=True, validate=ma.fields.validate.Length(min=2, max=100)
    )
    photo_path = ma.fields.String(
        required=True, validate=ma.fields.validate.Length(min=2, max=300)
    )
    description = ma.fields.String(
        required=True, validate=ma.fields.validate.Length(min=2, max=1000)
    )

    @pre_dump
    def add_base_url(self, data, **kwargs):
        field_name = "photo_path"
        field_data = getattr(data, field_name, None)
        if field_data:
            setattr(
                data, field_name, f"{current_app.config.get('BASE_URL')}/{field_data}"
            )
        return data

    class Meta:
        model = Reviews
        include_fk = True
        load_instance = True
        sqla_session = db.session
