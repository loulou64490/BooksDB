from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])

class RegisterForm(FlaskForm):
    mail = StringField("Adresse mail", validators=[DataRequired()])
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    password2 = PasswordField("Confirmer le mot de passe", validators=[DataRequired()])

class CommentForm(FlaskForm):
    comment = StringField("Commentaire", validators=[DataRequired()])
    rating = IntegerField("Note", validators=[DataRequired()])

class BookForm(FlaskForm):
    title = StringField("Titre", validators=[DataRequired()])
    author = StringField("Auteur", validators=[DataRequired()])
    year = IntegerField("Année", validators=[DataRequired()])

class SearchForm(FlaskForm):
    search = StringField("Recherche", validators=[DataRequired()])
