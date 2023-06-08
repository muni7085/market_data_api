from models.sqlalchemy_m.user_model import User

def to_json(user:object):
    return dict(list(user.__dict__.items())[1:])