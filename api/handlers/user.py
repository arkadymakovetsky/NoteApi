from api import app, request, multi_auth, db
from api.models.user import UserModel
from api.schemas.user import user_schema, users_schema, UserSchema, UserRequestSchema
from utility.helpers import get_object_or_404
from flask_apispec import doc, marshal_with, use_kwargs


@app.get("/users/<int:user_id>")
@doc(description='Api for users', tags=['Users'], summary="Get user by id")
@marshal_with(UserSchema, code=200)
def get_user_by_id(user_id):
    user = get_object_or_404(UserModel, user_id)
    if user is None:
        return {"error": f"User with id={user_id} not found"}, 404
    # return user_schema.dump(user), 200
    return user, 200


@app.get("/users")
@doc(description='Api for all users', tags=['Users'], summary="Get all users")
@marshal_with(UserSchema(many=True), code=200)
def get_users():
    users = UserModel.query.all()
    # return users_schema.dump(users), 200
    return users, 200


@app.route("/users", methods=["POST"])
@doc(description='Api for create user', tags=['Users'], summary="Create user")
@use_kwargs(UserRequestSchema, location='json')
@marshal_with(UserSchema, code=201)
# def create_user():
#     user_data = request.json
#     user = UserModel(**user_data)
def create_user(**kwargs):
    user = UserModel(**kwargs)
    # DONE: добавить обработчик на создание пользователя с неуникальным username --> ПОВЕРИТЬ!!! 409 one_or_none() user alredy exists
    if UserModel.query.filter_by(username=user.username).one_or_none():
        return {"error": f"User with name={user.username} alredy exists"}, 409
    user.save()
    # return user_schema.dump(user), 201
    return user, 201


@app.route("/users/<int:user_id>", methods=["PUT"])
##Insert decorator
@multi_auth.login_required(role="admin")
def edit_user(user_id):
    user_data = request.json
    user = get_object_or_404(UserModel, user_id)
    user.username = user_data["username"]
    user.save()
    return user_schema.dump(user), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
@multi_auth.login_required(role="admin")
def delete_user(user_id):
    """
    Пользователь может удалять ТОЛЬКО свои заметки
    """
    user = UserModel.query.get(user_id)
    user.delete()
    return {"message": f"User with id={user_id} has deleted"}, 200