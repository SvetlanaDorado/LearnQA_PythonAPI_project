import pytest
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests
from lib.utils import generate_random_string


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


    def test_edit_just_created_user(self):
        # Register and Login
        user_data = self.create_user_and_login()

        user_id = user_data["user_id"]
        token = user_data["token"]
        auth_sid = user_data["auth_sid"]

        new_name = "Changed Name"

        # Edit
        response_edit = MyRequests.put(
            f"/user/{user_id}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
            data={'firstName': new_name}
        )
        Assertions.assert_code_status(response_edit, 200)

        # Get
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


    def test_edit_user_without_auth(self):
        user_data = self.prepare_registration_data()

        response_create = MyRequests.post("/user/", data=user_data)

        Assertions.assert_code_status(response_create, 200)
        Assertions.assert_json_has_key(response_create, "id")

        user_id = self.get_json_value(response_create, "id")

        response_edit = MyRequests.put(
            f"/user/{user_id}",
            data={"firstName": "Name No Auth"}
        )

        Assertions.assert_code_status(response_edit, 400)
        assert (response_edit.json()["error"] ==
                "Auth token not supplied"), f"Unexpected response: {response_edit.text}"


    def test_edit_user_as_another_user(self):
        # Register and login as user1
        user1 = self.create_user_and_login()

        # Register user2
        user2_data = self.prepare_registration_data()

        response_create2 = MyRequests.post("/user/", data=user2_data)

        Assertions.assert_code_status(response_create2, 200)
        Assertions.assert_json_has_key(response_create2, "id")

        user2_id = self.get_json_value(response_create2, "id")

        # Edit user2 while logged in as user1
        response_edit = MyRequests.put(
            f"/user/{user2_id}",
            headers={"x-csrf-token": user1["token"]},
            cookies={"auth_sid": user1["auth_sid"]},
            data={"firstName": "Name Another User"}
        )

        Assertions.assert_code_status(response_edit, 400)
        assert (response_edit.json()["error"] ==
        "This user can only edit their own data."), f"Unexpected response: {response_edit.text}"


    @pytest.mark.parametrize("field, value, expected_message", invalid_params)
    def test_edit_user_with_invalid_data(self, field, value, expected_message):
        user_data = self.create_user_and_login()

        user_id = user_data["user_id"]
        token = user_data["token"]
        auth_sid = user_data["auth_sid"]

        response = MyRequests.put(
            f"/user/{user_id}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid},
            data={field: value}
        )

        Assertions.assert_code_status(response, 400)
        assert (response.json()["error"] ==
                expected_message), f"Unexpected response: {response.text}"