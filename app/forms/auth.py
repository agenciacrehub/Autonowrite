from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User

class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', 
                         validators=[DataRequired(), 
                                    Length(min=4, max=20)])
    email = StringField('Email',
                       validators=[DataRequired(), 
                                 Email()])
    password = PasswordField('Senha',
                           validators=[DataRequired(),
                                     Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha',
                                   validators=[DataRequired(),
                                              EqualTo('password')])
    submit = SubmitField('Cadastrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está cadastrado. Por favor, use outro email.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), 
                                 Email()])
    password = PasswordField('Senha',
                           validators=[DataRequired()])
    remember_me = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), 
                                 Email()])
    submit = SubmitField('Solicitar Redefinição de Senha')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova Senha',
                           validators=[DataRequired()])
    confirm_password = PasswordField('Repita a Senha',
                                   validators=[DataRequired(),
                                              EqualTo('password')])
    submit = SubmitField('Redefinir Senha')
