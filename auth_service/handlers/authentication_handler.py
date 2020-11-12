import logging
from pyramid.view import view_config

from auth_service.controllers.authentication_controller import AuthenticationController

logger = logging.getLogger(__name__)

auth_controller = AuthenticationController()


@view_config(
    route_name='register',
    renderer='json',
    request_method='POST'
)
def register(request):
    username = request.json.get("username")
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    password = request.json.get("password")

    kwargs = {key: val for key, val in request.json.items() if key not in ['username', 'first_name', 'last_name', 'password']}
    print(kwargs)

    result = auth_controller.register(username, first_name, last_name, password, **kwargs)
    if result['status']:
        request.response.status = result['status']
    return result


@view_config(
    route_name='login',
    renderer='json',
    request_method='POST'
)
def login(request):
    username = request.json.get('username')
    password = request.json.get('password')
    auth_result = auth_controller.login(username, password)

    if auth_result['status']:
        request.response.status = auth_result['status']
    return auth_result
