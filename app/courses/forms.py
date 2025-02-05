from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, FileField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileAllowed

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    instructor_name = StringField('Instructor Name', validators=[DataRequired()])
    date_created = DateField('Start Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    prerequisites = TextAreaField('Prerequisites', validators=[Optional()])
    media = FileField('Upload Image/Video', validators=[Optional(), FileAllowed(['jpg', 'png', 'mp4', 'avi', 'pdf'], 'PDF, Images and videos only!')])
    category = StringField('Category', validators=[Optional()])
    difficulty_level = StringField('Difficulty Level', validators=[Optional()])
    submit = SubmitField('Create Course')
