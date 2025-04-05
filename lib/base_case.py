import json.decoder
from requests import Response
from datetime import datetime
from lib.assertions import Assertions
from lib.my_requests import MyRequests


class BaseCase:
    def get_cookie (self, response: Response, cookie_name):
        assert cookie_name in response.cookies, f"Cannot find cookie with the name '{cookie_name}' in the last response"
        return response.cookies[cookie_name]


    def get_header (self, response: Response, headers_name):
        assert headers_name in response.headers, f"Cannot find header with the name '{headers_name}' in the last response"
        return response.headers[headers_name]


    def get_json_value(self, response: Response, name):
        try:
            response_as_dict = response.json()
        except json.decoder.JSONDecodeError:
           assert False, f"Response is not in JSON format. Response text is '{response.text}'"

        assert name in response_as_dict, f"Response JSON does not have key '{name}'"
        return response_as_dict[name]


    def prepare_registration_data(self, email=None):
        if email is None:
            base_part = 'learnqa'
            domain = 'example.com'
            random_part = datetime.now().strftime("%m%d%Y%H%M%S")
            email = f"{base_part}{random_part}@{domain}"

        return {
            'password': '123',
            'username': 'learnqa',
            'firstName': 'learnqa',
            'lastName': 'learnqa',
            'email': email
        }


    def create_user_and_auth(self):
        registration_data = self.prepare_registration_data()
        response_create = MyRequests.post("/user/", data=registration_data)

        Assertions.assert_code_status(response_create, 200)
        Assertions.assert_json_has_key(response_create, "id")

        user_id = self.get_json_value(response_create, "id")

        auth_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }

        response_auth = MyRequests.post("/user/login", data=auth_data)

        Assertions.assert_code_status(response_auth, 200)

        token = self.get_header(response_auth, "x-csrf-token")
        auth_sid = self.get_cookie(response_auth, "auth_sid")

        return {
            "password": registration_data["password"],
            "email": registration_data["email"],
            "user_id": user_id,
            "auth_sid": auth_sid,
            "token": token
        }