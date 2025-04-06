import allure
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests

@allure.epic("User details")
@allure.feature("Getting user details")
@allure.tag("regression")
class TestUserGet(BaseCase):
    @allure.story("Unauthorized user details access")
    @allure.title("Ensure only 'username' is visible without auth")
    @allure.description("Test verifies when user is not authenticated, only 'username' is returned")
    @allure.tag("smoke")
    def test_get_user_details_not_auth(self):
        with allure.step("Send request to get user (ID 2) data without authentication"):
            response = MyRequests.get("/user/2")

        with allure.step("Verify only 'username' is visible and other fields are not"):
            Assertions.assert_json_has_key(response, "username")
            Assertions.assert_json_has_not_key(response, "email")
            Assertions.assert_json_has_not_key(response, "firstName")
            Assertions.assert_json_has_not_key(response, "lastName")


    @allure.story("Authorized user details access")
    @allure.title("Ensure full user details are visible with auth")
    @allure.description("Test verifies an authenticated user can get full details about their own account")
    @allure.tag("smoke")
    def test_get_user_details_auth_as_same_user(self):
        with allure.step("Log in with valid credentials"):
            data = {
                'email': 'vinkotov@example.com',
                'password': '1234'
            }

            response_login = MyRequests.post("/user/login", data=data)

            auth_sid = self.get_cookie(response_login, "auth_sid")
            token = self.get_header(response_login, "x-csrf-token")
            user_id_from_auth_method = self.get_json_value(response_login, "user_id")

        with allure.step("Send request to get user (ID 2) data with authentication"):
            response_get_details = MyRequests.get(
                f"/user/{user_id_from_auth_method}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid}
            )

        with allure.step("Verify all user details are visible"):
            expected_fields = ["username", "email", "firstName", "lastName"]

            Assertions.assert_json_has_keys(response_get_details, expected_fields)

    @allure.story("Authorized user details access")
    @allure.title("Ensure limited user details are visible to other users")
    @allure.description("Test verifies an authenticated user can only see 'username' of other users")
    def test_get_user_details_auth_as_another_user(self):
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

        with allure.step("Try to get user2 details while logged in as user1"):
            response_get_details = MyRequests.get(
                f"/user/{user2_id}",
                headers={"x-csrf-token": token_user1},
                cookies={"auth_sid": auth_sid_user1}
            )

        with allure.step("Verify only 'username' is visible and other fields are not"):
            Assertions.assert_json_has_key(response_get_details, "username")
            Assertions.assert_json_has_not_key(response_get_details, "email")
            Assertions.assert_json_has_not_key(response_get_details, "firstName")
            Assertions.assert_json_has_not_key(response_get_details, "lastName")