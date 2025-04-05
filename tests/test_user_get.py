from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests

class TestUserGet(BaseCase):
    def test_get_user_details_not_auth(self):
        response = MyRequests.get("/user/2")

        Assertions.assert_json_has_key(response, "username")
        Assertions.assert_json_has_not_key(response, "email")
        Assertions.assert_json_has_not_key(response, "firstName")
        Assertions.assert_json_has_not_key(response, "lastName")


    def test_get_user_details_auth_as_same_user(self):
        data = {
            'email': 'vinkotov@example.com',
            'password': '1234'
        }

        response_login = MyRequests.post("/user/login", data=data)

        auth_sid = self.get_cookie(response_login, "auth_sid")
        token = self.get_header(response_login, "x-csrf-token")
        user_id_from_auth_method = self.get_json_value(response_login, "user_id")

        response_get_details = MyRequests.get(
            f"/user/{user_id_from_auth_method}",
            headers={"x-csrf-token": token},
            cookies={"auth_sid": auth_sid}
        )

        expected_fields = ["username", "email", "firstName", "lastName"]

        Assertions.assert_json_has_keys(response_get_details, expected_fields)


    def test_get_user_details_auth_as_another_user(self):
        user1_data = self.create_user_and_login()
        token_user1 = user1_data["token"]
        auth_sid_user1 = user1_data["auth_sid"]

        user2_data = self.prepare_registration_data()

        response_create = MyRequests.post("/user/", data=user2_data)

        Assertions.assert_code_status(response_create, 200)
        Assertions.assert_json_has_key(response_create, "id")

        user2_id = self.get_json_value(response_create, "id")

        response_get_details = MyRequests.get(
            f"/user/{user2_id}",
            headers={"x-csrf-token": token_user1},
            cookies={"auth_sid": auth_sid_user1}
        )

        Assertions.assert_json_has_key(response_get_details, "username")
        Assertions.assert_json_has_not_key(response_get_details, "email")
        Assertions.assert_json_has_not_key(response_get_details, "firstName")
        Assertions.assert_json_has_not_key(response_get_details, "lastName")