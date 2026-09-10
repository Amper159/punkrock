from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, URL, Length, Length as _Length

class BandSubmitForm(FlaskForm):
    name = StringField("Název kapely", validators=[DataRequired(), Length(max=120)])
    city = StringField("Město", validators=[Optional(), Length(max=80)])
    styles = StringField("Styl(y)", validators=[Optional(), Length(max=200)])
    about = TextAreaField("O kapele", validators=[Optional()])
    spotify = StringField("Spotify", validators=[Optional(), URL()])
    bandcamp = StringField("Bandcamp", validators=[Optional(), URL()])
    web = StringField("Web", validators=[Optional(), URL()])
    submit = SubmitField("Odeslat ke schválení")


class CommentForm(FlaskForm):
    author_name = StringField("Jméno", validators=[DataRequired(), Length(max=80)])
    text = TextAreaField("Komentář", validators=[DataRequired(), Length(max=1000)])
    # honeypot — lidský návštěvník tohle pole nikdy nevyplní (v šabloně je vizuálně skryté)
    website = StringField("Web", validators=[Optional(), Length(max=0)])
    submit = SubmitField("Přidat komentář")


class GigPhotoForm(FlaskForm):
    uploader_name = StringField("Jméno", validators=[DataRequired(), Length(max=80)])
    caption = StringField("Popisek (kde, kdy, co je na fotce...)", validators=[Optional(), Length(max=200)])
    photo = FileField("Fotka", validators=[
        FileRequired("Vyber prosím fotku."),
        FileAllowed(["jpg", "jpeg", "png", "webp"], "Povolené formáty: JPG, PNG, WEBP."),
    ])
    website = StringField("Web", validators=[Optional(), Length(max=0)])  # honeypot
    submit = SubmitField("Nahrát fotku")
