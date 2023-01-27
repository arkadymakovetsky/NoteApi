from api import app, multi_auth, request
from api.models.note import NoteModel
from api.schemas.note import note_schema, notes_schema
from utility.helpers import get_object_or_404


@app.route("/notes/<int:note_id>", methods=["GET"])
@multi_auth.login_required
def get_note_by_id(note_id):
    # DONE: авторизованный пользователь может получить только свою заметку или публичную заметку других пользователей
    # Попытка получить чужую приватную заметку, возвращает ответ с кодом 403
    user = multi_auth.current_user()
    note = get_object_or_404(NoteModel, note_id)
    if not (note.author_id == user.id or not note.private):
        return {"error": f"Попытка получить чужую заметку c note_id={note_id}"}, 403
    return note_schema.dump(note), 200


@app.route("/notes", methods=["GET"])
@multi_auth.login_required
def get_notes():
    # DONE: авторизованный пользователь получает только свои заметки и публичные заметки других пользователей
    user = multi_auth.current_user()
    notes = NoteModel.query.filter((NoteModel.author_id == user.id) | (NoteModel.private == False)).all()
    return notes_schema.dump(notes), 200


@app.route("/notes", methods=["POST"])
@multi_auth.login_required
def create_note():
    user = multi_auth.current_user()
    note_data = request.json
    note = NoteModel(author_id=user.id, **note_data)
    note.save()
    return note_schema.dump(note), 201


@app.route("/notes/<int:note_id>", methods=["PUT"])
@multi_auth.login_required
def edit_note(note_id):
    # DONE: Пользователь может редактировать ТОЛЬКО свои заметки.
    # Попытка редактировать чужую заметку, возвращает ответ с кодом 403
    author = multi_auth.current_user()
    note = get_object_or_404(NoteModel, note_id)
    if note.author_id != author.id:
        return {"error": f"Попытка редактировать чужую заметку c note_id={note_id}"}, 403
    note_data = request.json
    for key, value in note_data.items():
        setattr(note, key, value)
    note.save()
    return note_schema.dump(note), 200


@app.route("/notes/<int:note_id>", methods=["DELETE"])
@multi_auth.login_required
def delete_note(note_id):
    # DONE: Пользователь может удалять ТОЛЬКО свои заметки.
    # Попытка удалить чужую заметку, возвращает ответ с кодом 403
    author = multi_auth.current_user()
    note = get_object_or_404(NoteModel, note_id)
    if note.author_id != author.id:
        return {"error": f"Попытка удалить чужую заметку c note_id={note_id}"}, 403
    note.delete()
    return {"message": f"Note with id={note_id} has deleted"}, 200
