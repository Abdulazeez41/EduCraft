from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, DateField
from wtforms.validators import DataRequired

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    instructor_name = StringField('Instructor Name', validators=[DataRequired()])
    date_created = DateField('Start Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    prerequisites = TextAreaField('Prerequisites')
    submit = SubmitField('Create Course')
