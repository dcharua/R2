from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired

## login and registration


class CapturarEgreso(FlaskForm):
    vendor = SelectField(u'categoria', choices=[('Gosh', 'gosh'),('cat','Caterpillar')])
    
