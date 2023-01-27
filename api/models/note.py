from api import db
from api.models.user import UserModel
from sqlalchemy.exc import IntegrityError


class NoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(UserModel.id))
    text = db.Column(db.String(255), unique=False, nullable=False)
    private = db.Column(db.Boolean(), default=True, nullable=False)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError:  # Обработка ошибки "Duplicate key"
            db.session.rollback()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
