import pytest
import allure
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests
from lib.utils import generate_random_string

@allure.epic("Registration")
@allure.feature("Creating a new user")
@allure.tag("regression")
class TestUserRegister(BaseCase):
    exclude_params = [
        ("password"),
        ("username"),
        ("firstName"),
        ("lastName"),
        ("email")
    ]

    @allure.story("Create a new user with valid data")
    @allure.title("Ensure a new user can be created with valid data")
    @allure.description("Test checks a new user can be successfully registered with valid data")
    @allure.tag("smoke")
    def test_create_user_successfully(self):
        with allure.step("Prepare registration data"):
            data = self.prepare_registration_data()

        with allure.step("Send request to register new user"):
            response = MyRequests.post("/user/", data=data)

        with allure.step("Verify user is created"):
            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")


    @allure.story("Create user with existing email")
    @allure.title("Ensure a new user cannot be created with existing email")
    @allure.description("Test checks user registration with an existing email returns error")
    def test_create_user_with_existing_email(self):
        with allure.step("Prepare data with existing email"):
            email = 'vinkotov@example.com'
            data = self.prepare_registration_data(email)

        with allure.step("Send request with existing email"):
            response = MyRequests.post("/user/", data=data)

        with allure.step("Verify error message"):
            Assertions.assert_code_status(response, 400)
            assert (response.content.decode("utf-8") ==
                    f"Users with email '{email}' already exists"), f"Unexpected response content '{response.content}'"


    @allure.story("Create user with invalid email")
    @allure.title("Ensure a new user cannot be created with invalid email")
    @allure.description("Test checks user registration with an invalid email returns error")
    @allure.tag("smoke")
    def test_create_user_with_invalid_email(self):
        with allure.step("Prepare data with invalid email"):
            email = 'with_no_at_sign_example.com'
            data = self.prepare_registration_data(email)

        with allure.step("Send request with invalid email"):
            response = MyRequests.post("/user/", data=data)

        with allure.step("Verify error message"):
            Assertions.assert_code_status(response, 400)
            assert (response.content.decode("utf-8") ==
                    f"Invalid email format"), f"Unexpected response content '{response.content}'"


    @allure.story("Create user with short name")
    @allure.title("Ensure a new user cannot be created with short name")
    @allure.description("Test checks user registration with short name returns error")
    def test_create_user_with_short_name(self):
        with allure.step("Prepare data with short first name"):
            data = self.prepare_registration_data()
            short_name = generate_random_string(1)
            data["firstName"] = short_name

        with allure.step("Send request with short first name"):
            response = MyRequests.post("/user/", data=data)

        with allure.step("Verify error message"):
            Assertions.assert_code_status(response, 400)
            assert (response.content.decode("utf-8") ==
                    "The value of 'firstName' field is too short"), f"Unexpected response content: '{response.content}'"


    @allure.story("Create user with long name")
    @allure.title("Ensure a new user cannot be created with long name")
    @allure.description("Test checks user registration with long name returns error")
    def test_create_user_with_long_name(self):
        with allure.step("Prepare data with long first name"):
            data = self.prepare_registration_data()
            max_length = 250
            long_name = generate_random_string(max_length + 1)
            data["firstName"] = long_name

        with allure.step("Send request with long first name"):
         response = MyRequests.post("/user/", data=data)

        with allure.step("Verify error message"):
            Assertions.assert_code_status(response, 400)
            assert (response.content.decode("utf-8") ==
                    "The value of 'firstName' field is too long"), f"Unexpected response content: '{response.content}'"


    @allure.story("Create user with missing required fields")
    @allure.title("Ensure a new user cannot be created if any required field is missing")
    @allure.description("Test checks user registration without any required field returns error")
    @pytest.mark.parametrize("missing_field", exclude_params)
    @allure.tag("smoke")
    def test_create_user_without_one_field(self, missing_field):
        with allure.step(f"Prepare registration data without field: {missing_field}"):
            data = self.prepare_registration_data()
            data.pop(missing_field)

        with allure.step(f"Send request without field: {missing_field}"):
            response = MyRequests.post("/user/", data=data)

        with allure.step("Verify error message"):
            Assertions.assert_code_status(response, 400)
            assert (response.content.decode("utf-8") == f"The following required params are missed: {missing_field}"), \
                (f"Unexpected response content: '{response.content}'")