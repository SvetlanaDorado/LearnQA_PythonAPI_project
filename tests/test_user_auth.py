import pytest
import allure
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests

@allure.epic("Authorization")
@allure.feature("Login and session verification")
@allure.tag("regression")
class TestUserAuth(BaseCase):
    exclude_params = [
        ("no_cookie"),
        ("no_token")
    ]

    def setup_method(self):
        with allure.step("Log in with valid credentials"):
            data = {
                'email': 'vinkotov@example.com',
                'password': '1234'
            }

            response_login = MyRequests.post("/user/login", data=data)

        with allure.step("Get auth_sid, token and user_id from response"):
            self.auth_sid = self.get_cookie(response_login, "auth_sid")
            self.token = self.get_header(response_login, "x-csrf-token")
            self.user_id_from_auth_method = self.get_json_value(response_login, "user_id")


    @allure.story("Successful login and auth check")
    @allure.title("Ensure a user is authenticated correctly with token and cookie")
    @allure.description("Test verifies successful login and that user ID is returned and matches during auth check")
    @allure.tag("smoke")
    def test_auth_user(self):
        with allure.step("Send auth request with token and cookie"):
            response_auth = MyRequests.get(
                "/user/auth",
                headers={"x-csrf-token": self.token},
                cookies={"auth_sid": self.auth_sid}
            )

        with allure.step("Verify user ID from auth method matches user ID from check method"):
            Assertions.assert_json_value_by_name(
                response_auth,
                "user_id",
                self.user_id_from_auth_method,
                "User id from auth method is not equal to user id from check method"
            )


    @allure.story("Negative login scenarios")
    @allure.title("Ensure a user is not authenticated without token or cookie")
    @allure.description("Test checks authorization status w/o sending auth cookie or token")
    @allure.tag("smoke")
    @pytest.mark.parametrize('condition', exclude_params)
    def test_negative_auth_check(self, condition):
        if condition == "no_cookie":
            with allure.step("Send auth request without cookie"):
                response_auth = MyRequests.get(
                    "/user/auth",
                    headers={"x-csrf-token": self.token}
                )
        else:
            with allure.step("Send auth request without token"):
                response_auth = MyRequests.get(
                    "/user/auth",
                    cookies={"auth_sid": self.auth_sid}
                )

        with allure.step("Verify user is not authenticated"):
            Assertions.assert_json_value_by_name(
                response_auth,
                "user_id",
                0,
                f"User is authorized with condition {condition}"
            )