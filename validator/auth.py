from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validate,
    validates,
    validates_schema,
)
from sqlalchemy import func


class UserRegisValidator(Schema):
    password = fields.String(required=False, validate=[validate.Length(min=1, max=255)], default=None)
    email = fields.Email(required=True)
    username = fields.String(required=True, validate=[validate.Length(min=1, max=255)])
    full_name = fields.String(required=True, validate=[validate.Length(min=1, max=255)])
    phone_number = fields.String(required=True, validate=[validate.Length(min=1, max=255)])

    # @validates("signature_path")
    # def validate_signature_path(self, value):
    #     if value != None:
    #         if is_file_exists(path=f"tmp/{value}") == False:
    #             raise ValidationError("signature_path not exists")

    # @validates_schema
    # def validate_password_and_confirm_password_must_be_same(self, data, **kwargs):
    #     if data["password"] != data["confirm_password"]:
    #         raise ValidationError(
    #             message="field password and confirm_password must be same"
    #         )
