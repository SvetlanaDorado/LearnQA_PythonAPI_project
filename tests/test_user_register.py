import pytest
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests
from lib.utils import generate_random_string

class TestUserRegister(BaseCase):
    exclude_params = [
        ("password"),
        ("username"),
        ("firstName"),
        ("lastName"),
        ("email")
    ]

    def test_create_user_successfully(self):
        data = self.prepare_registration_data()

        response = MyRequests.post("/user/", data=data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")


    def test_create_user_with_existing_email(self):
        email = 'vinkotov@example.com'
        data = self.prepare_registration_data(email)

        response = MyRequests.post("/user/", data=data)

        Assertions.assert_code_status(response, 400)
        assert (response.content.decode("utf-8") ==
                f"Users with email '{email}' already exists"), f"Unexpected response content '{response.content}'"


    def test_create_user_with_invalid_email(self):
        email = 'with_no_at_sign_example.com'
        data = self.prepare_registration_data(email)

        response = MyRequests.post("/user/", data=data)

        Assertions.assert_code_status(response, 400)
        assert (response.content.decode("utf-8") ==
                f"Invalid email format"), f"Unexpected response content '{response.content}'"


    def test_create_user_with_short_name(self):
        data = self.prepare_registration_data()
        short_name = generate_random_string(1)
        data["firstName"] = short_name

        response = MyRequests.post("/user/", data=data)

        Assertions.assert_code_status(response, 400)
        assert (response.content.decode("utf-8") ==
                "The value of 'firstName' field is too short"), f"Unexpected response content: '{response.content}'"


    def test_create_user_with_long_name(self):
        data = self.prepare_registration_data()
        max_length = 250
        long_name = generate_random_string(max_length + 1)
        data["firstName"] = long_name

        response = MyRequests.post("/user/", data=data)

        Assertions.assert_code_status(response, 400)
        assert (response.content.decode("utf-8") ==
                "The value of 'firstName' field is too long"), f"Unexpected response content: '{response.content}'"


    @pytest.mark.parametrize("missing_field", exclude_params)
    def test_create_user_without_one_field(self, missing_field):
        data = self.prepare_registration_data()
        data.pop(missing_field)

        response = MyRequests.post("/user/", data=data)

        Assertions.assert_code_status(response, 400)
        assert (response.content.decode("utf-8") == f"The following required params are missed: {missing_field}"), \
            (f"Unexpected response content: '{response.content}'")