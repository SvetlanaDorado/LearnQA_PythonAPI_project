from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests

class TestUserEdit(BaseCase):
    def test_edit_just_created_user(self):
        # Register and Auth
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