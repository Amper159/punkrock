from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, URL, Length

class BandSubmitForm(FlaskForm):
    name = StringField("Název kapely", validators=[DataRequired(), Length(max=120)])
    city = StringField("Město", validators=[Optional(), Length(max=80)])
    styles = StringField("Styl(y)", validators=[Optional(), Length(max=200)])
    about = TextAreaField("O kapele", validators=[Optional()])
    spotify = StringField("Spotify", validators=[Optional(), URL()])
    bandcamp = StringField("Bandcamp", validators=[Optional(), URL()])
    web = StringField("Web", validators=[Optional(), URL()])
    submit = SubmitField("Odeslat ke schválení")
