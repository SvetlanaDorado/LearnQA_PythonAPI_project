import pytest
import allure
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests
from lib.utils import generate_random_string

@allure.epic("User details")
@allure.feature("Updating user details")
@allure.tag("regression")
class TestUserEdit(BaseCase):
    invalid_params = [
        (
            "email",
            "with_no_at_sign_example.com",
            "Invalid email format"
        ),
        (
            "firstName",
            generate_random_string(1),
            "The value for field `firstName` is too short"
        )
    ]

    @allure.story("Edit own user data")
    @allure.title("Ensure user can successfully change own first name")
    @allure.description("Test verifies an authenticated user can edit their own first name")
    @allure.tag("smoke")
    def test_edit_just_created_user(self):
        with allure.step("Register and login user"):
            data = self.create_user_and_login()

            user_id = data["user_id"]
            token = data["token"]
            auth_sid = data["auth_sid"]

            new_name = "Changed Name"

        with allure.step("Edit user first name"):
            response_edit = MyRequests.put(
                f"/user/{user_id}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid},
                data={'firstName': new_name}
            )
            Assertions.assert_code_status(response_edit, 200)

        with allure.step("Verify name was updated"):
            response_check = MyRequests.get(
                f"/user/{user_id}",
             headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid}
            )
            Assertions.assert_json_value_by_name(
                response_check,
                "firstName",
                new_name,
                "Wrong user name after edit"
            )

    @allure.story("Edit own user data")
    @allure.title("Ensure user cannot edit data without being authorized")
    @allure.description("Test verifies unauthorized user cannot edit any user data")
    def test_edit_user_without_auth(self):
        with allure.step("Prepare registration data"):
            data = self.prepare_registration_data()

        with allure.step("Send request to register new user"):
            response_create = MyRequests.post("/user/", data=data)

        with allure.step("Verify user is created"):
            Assertions.assert_code_status(response_create, 200)
            Assertions.assert_json_has_key(response_create, "id")

            user_id = self.get_json_value(response_create, "id")

        with allure.step("Try to edit user without auth"):
            response_edit = MyRequests.put(
                f"/user/{user_id}",
                data={"firstName": "Name No Auth"}
            )

        with allure.step("Verify error message"):
            Assertions.assert_code_status(response_edit, 400)
            assert (response_edit.json()["error"] ==
                    "Auth token not supplied"), f"Unexpected response: {response_edit.text}"

    @allure.story("Edit another user's data")
    @allure.title("Ensure user cannotedit other users' data")
    @allure.description("Test verifies an authenticated user cannot edit data of another user")
    def test_edit_user_as_another_user(self):
        with allure.step("Register and login as user1"):
            user1_data = self.create_user_and_login()
            token_user1 = user1_data["token"]
            auth_sid_user1 = user1_data["auth_sid"]

        with allure.step("Register user2"):
            user2_data = self.prepare_registration_data()

            response_create = MyRequests.post("/user/", data=user2_data)

            Assertions.assert_code_status(response_create, 200)
            Assertions.assert_json_has_key(response_create, "id")

            user2_id = self.get_json_value(response_create, "id")

        with allure.step("Try to edit user2 while logged in as user1"):
            response_edit = MyRequests.put(
                f"/user/{user2_id}",
                headers={"x-csrf-token": token_user1},
                cookies={"auth_sid": auth_sid_user1},
                data={"firstName": "Name Another User"}
            )

        with allure.step("Verify error message"):
            Assertions.assert_code_status(response_edit, 400)
            assert (response_edit.json()["error"] ==
            "This user can only edit their own data."), f"Unexpected response: {response_edit.text}"


    @allure.story("Edit own user data")
    @allure.title("Ensure user cannot update data with invalid fields")
    @allure.description("Test verifies error response when updating with invalid email or too short first name")
    @pytest.mark.parametrize("field, value, expected_message", invalid_params)
    @allure.tag("smoke")
    def test_edit_user_with_invalid_data(self, field, value, expected_message):
        with allure.step("Register and login user"):
            data = self.create_user_and_login()

            user_id = data["user_id"]
            token = data["token"]
            auth_sid = data["auth_sid"]

        with allure.step(f"Try to update field {field} with invalid value"):
            response = MyRequests.put(
                f"/user/{user_id}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid},
                data={field: value}
            )

        with allure.step("Verify error message"):
            Assertions.assert_code_status(response, 400)
            assert (response.json()["error"] ==
                    expected_message), f"Unexpected response: {response.text}"