import os
import jwt
import json
import datetime

from mongoengine import *
from mongoengine import signals

from mongoengine.errors import NotUniqueError
from auth_service.configuration import Config


config = Config()


def encode_auth_token(username):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            "exp": datetime.datetime.now() + datetime.timedelta(days=0, seconds=5),
            "iat": datetime.datetime.now(),
            "sub": username
        }
        return jwt.encode(
            payload,
            config.service_config.get_str("auth_service.secret_key"),
            algorithm="HS256"
        )
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Validates the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(
            auth_token, config.service_config.get_str("auth_service.secret_key"))
        is_blacklisted_token = True if BlacklistedToken.objects(
            token=auth_token).first() else False
        if is_blacklisted_token:
            return "Token blacklisted. Please log in again."
        else:
            return payload["sub"]
    except jwt.ExpiredSignatureError:
        return "Signature expired. Please log in again."
    except jwt.InvalidTokenError:
        return "Invalid token. Please log in again."


def handler(event):
    """Signal decorator to allow use of callback functions as class decorators."""
    def decorator(fn):
        def apply(cls):
            event.connect(fn, sender=cls)
            return cls

        fn.apply = apply
        return fn
    return decorator


@handler(signals.pre_save)
def update_modified(sender, document):
    document.modified = datetime.datetime.now()


@update_modified.apply
class ContactDetails(Document):
    email = StringField(max_length=320, unique=True, required=True)
    contact_number = StringField(max_length=16)
    date_created = DateTimeField(default=datetime.datetime.now())
    modified = DateTimeField()

    def __repr__(self):
        return "{}: {}".format(
            self.user.first_name,
            "tel: %s and email: %s" % self.contact_number, self.email
        )


@update_modified.apply
class Permission(Document):
    name = StringField(max_length=64, unique=True, required=True)
    # might use this to deprecate permissions
    is_active = BooleanField(default=True)
    date_created = DateTimeField(default=datetime.datetime.now())
    modified = DateTimeField()

    def __repr__(self):
        return "{}: <{}>".format(
            self.__class__.__name__,
            self.name
        )


@update_modified.apply
class Role(Document):
    name = StringField(max_length=32, unique=True, required=True)
    description = StringField(max_length=256)
    is_active = BooleanField(default=True)
    date_created = DateTimeField(default=datetime.datetime.now())
    modified = DateTimeField()

    permissions = ListField(ReferenceField(Permission))

    def __repr__(self):
        return "{}: <{}>".format(
            self.__class__.__name__,
            self.name
        )


@update_modified.apply
class User(Document):
    username = StringField(max_length=320, unique=True, required=True)
    first_name = StringField(max_length=255, required=True)
    last_name = StringField(max_length=255, required=True)
    password = StringField(max_length=255, required=True)
    is_active = BooleanField(default=False)
    is_troupe_leader = BooleanField(default=False)
    is_clown = BooleanField(default=False)
    is_client = BooleanField(default=False)
    last_login = DateTimeField()
    date_created = DateTimeField(default=datetime.datetime.now())
    modified = DateTimeField()

    roles = ListField(ReferenceField(Role))
    # requesting this should be hidden under permission
    contact_details = ReferenceField(ContactDetails)

    def __repr__(self):
        return "{}: {}".format(
            self.__class__.__name__,
            self.email
        )


@update_modified.apply
class Clown(Document):
    CLOWN_RANKS = {
        1: "Top Dan",
        2: "Some Bob",
        3: "Maybe Harry",
    }
    rank = IntField(default=1)
    modified = DateTimeField()

    user = ReferenceField(User)

    def __repr__(self):
        return "{} from {}".format(
            self.user.name,
            self.troupe.name
        )


@update_modified.apply
class Troupe(Document):
    name = StringField(max_length=128, required=True)
    max_capacity = IntField(default=1)
    date_created = DateTimeField(default=datetime.datetime.now())
    modified = DateTimeField()

    clowns = ListField(ReferenceField(Clown))

    def __repr__(self):
        return "{}: {}".format(
            self.__class__.__name__,
            self.name
        )


@update_modified.apply
class TroupeLeader(Document):
    modified = DateTimeField()

    user = ReferenceField(User)
    troupe = ReferenceField(Troupe)

    def __repr__(self):
        return "{} leads {}".format(
            self.user.first_name,
            self.troupe
        )


@update_modified.apply
class Client(Document):
    modified = DateTimeField()

    user = ReferenceField(User)
    contact_details = ReferenceField(ContactDetails)

    def __repr__(self):
        return "{}: {}".format(
            self.__class__.__name__,
            self.user.email
        )


class BlacklistedToken(Document):
    token = StringField(max_length=500, unique=True, required=True)
    blacklisted_on = DateTimeField(default=datetime.datetime.now())

    def __repr__(self):
        return "{}: <{}>".format(
            self.__class__.__name__,
            self.token
        )
