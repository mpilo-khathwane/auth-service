import json
import logging
import pyramid.httpexceptions as exc
import bcrypt
from requests.exceptions import HTTPError

from auth_service.models.models import *
from auth_service.controllers.abstract_controller import AbstractController


class AuthenticationController(AbstractController):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config._connect_db()

    def _hash_password(self, password):
        """
            Create a bcrypt hash of a password
        """
        passwordhash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        return passwordhash

    def has_permission(self, request, view_permission):
        authorization = request.headers.get('Authorization')

        try:
            # todo: this is supposed to be the auth_token
            auth_token = authorization[1]
            logging.info(auth_token)
            username = decode_auth_token(auth_token)

            user_permissions = self.get_user_permissions(username)

            is_authorised = view_permission in user_permissions
            request.headers['User-Name'] = user.username
            request.headers['User-Id'] = user._id

            return is_authorised
        except HTTPError as e:
            if e.response.status_code == 401:
                raise exc.HTTPUnauthorized
            else:
                raise exc.HTTPForbidden

    def register(self, username, first_name, last_name, password, **kwargs):
        user = User.objects(username=username).first()
        if not user:
            try:
                password = self._hash_password(password)
                date_created = datetime.datetime.now()

                user = User(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    date_created=date_created,
                    **kwargs
                )
                user.save()

                if kwargs.get("is_client"):
                    self.logger.info("-------------")
                    client_roles = [Role.objects(name="client").first()]
                    self.logger.info(client_roles)
                    user.roles = client_roles
                    client = Client(user=user)
                    client.save()
                    user.save()
                if kwargs.get("is_troupe_leader"):
                    troupe_leader_roles = [Role.objects(name="troupe_leader")]
                    user.roles = troupe_leader_roles
                    troupe_leader = TroupeLeader(user=user)
                    troupe_leader.save()
                elif kwargs.get("is_clown"):
                    clown_roles = [Role.objects(name="clown")]
                    user.roles = clown_roles
                    clown = Clown(user=user)
                    clown.save()

                logging.info(user.username)

                auth_token = encode_auth_token(user.username)
                logging.info(auth_token)

                responseObject = {
                    'status': 201,
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode()
                }
                return responseObject
            except HTTPError as e:
                self.logger.exception(e)
                responseObject = {
                    'status': 400,
                    'message': 'Some error occurred. Please try again.'
                }
        else:
            responseObject = {
                'status': 400,
                'message': 'User already exists. Please Log in.',
            }
            return responseObject

    def login(self, username, password):
        roles = Role()
        try:
            user = User.objects(username=username).first()
            if user and bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8')):
                auth_token = encode_auth_token(user.username)
                if auth_token:
                    responseObject = {
                        'status': 201,
                        'message': 'Successfully logged in.',
                        'user_permissions': self.get_user_permissions(user.username),
                        'auth_token': auth_token.decode()
                    }
                    return responseObject
            else:
                responseObject = {
                    'status': 404,
                    'message': 'User does not exist.'
                }
                return responseObject
        except HTTPError as e:
            raise e

    def logout():
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    # todo: blacklist
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 403

    def get_user_permissions(self, username):
        user = User.objects(username=username).first()
        user_permissions = list()
        logging.info(">>>>>>>>>")
        logging.info(user.roles)
        logging.info(">>>>>>>>>")
        if user.roles:
            for role in user.roles:
                user_permissions += role.permissions
        return user_permissions
