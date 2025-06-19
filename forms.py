from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class AddProjectForm(FlaskForm):
    """Form for users to add a new Hetzner project."""
    name = StringField(
        'Project Name',
        validators=[DataRequired(), Length(min=3, max=100)],
        render_kw={"placeholder": "e.g., Personal Servers"}
    )
    api_token = PasswordField(
        'Hetzner API Token (R+W permissions)',
        validators=[DataRequired()],
        render_kw={"placeholder": "Paste your Hetzner API token here"}
    )
    submit = SubmitField('Add Project')