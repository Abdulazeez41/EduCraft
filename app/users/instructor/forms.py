from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, DateField, FileField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileAllowed

class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    due_date = DateField('Due Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Create Quiz')

class AssignmentForm(FlaskForm):
    title = StringField('Assignment Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateField('Due Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    file_upload = FileField('Upload Assignment File', validators=[Optional(), FileAllowed(['pdf', 'docx'], 'Documents only!')])
    submit = SubmitField('Create Assignment')
