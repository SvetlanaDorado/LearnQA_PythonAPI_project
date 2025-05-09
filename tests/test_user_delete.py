import allure
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.my_requests import MyRequests

@allure.epic("User details")
@allure.feature("Deleting user details")
@allure.tag("regression")
class TestUserDelete(BaseCase):
    @allure.story("Deleting protected user")
    @allure.title("Ensure protected user cannot be deleted")
    @allure.description("Test verifies a protected user cannot be deleted")
    def test_delete_protected_user(self):
        with allure.step("Login as protected user (ID 2)"):
            data = {
            'email': 'vinkotov@example.com',
            'password': '1234'
            }

            response_login = MyRequests.post("/user/login", data=data)

            Assertions.assert_code_status(response_login, 200)

            token = self.get_header(response_login, "x-csrf-token")
            auth_sid = self.get_cookie(response_login, "auth_sid")

        with allure.step("Try to delete protected user"):
            response_delete = MyRequests.delete(
            "/user/2",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid}
            )

        with allure.step("Verify error message"):
            Assertions.assert_code_status(response_delete, 400)
            assert (response_delete.json()["error"] ==
                    "Please, do not delete test users with ID 1, 2, 3, 4 or 5."), f"Unexpected response: {response_delete.text}"


    @allure.story("Deleting own user")
    @allure.title("Ensure user can be deleted")
    @allure.description("Test verifies a user can delete their own account successfully")
    @allure.tag("smoke")
    def test_delete_user_successfully(self):
        with allure.step("Register and login as a new user"):
            data = self.create_user_and_login()

            user_id = data["user_id"]
            token = data["token"]
            auth_sid = data["auth_sid"]

        with allure.step("Delete user account"):
            response_delete = MyRequests.delete(
                f"/user/{user_id}",
                headers={"x-csrf-token": token},
                cookies={"auth_sid": auth_sid}
            )
            Assertions.assert_code_status(response_delete, 200)

        with allure.step("Verify user is deleted"):
            response_get_details = MyRequests.get(f"/user/{user_id}")

            Assertions.assert_code_status(response_get_details, 404)
            assert (response_get_details.text ==
                    "User not found"), f"Unexpected response: {response_get_details.text}"


    @allure.story("Deleting another user")
    @allure.title("Ensure user cannot delete another user")
    @allure.description("Test verifies one user cannot delete another user's data")
    def test_delete_user_as_another_user(self):
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

        with allure.step("Try to delete user2 while logged in as user1"):
            response_delete = MyRequests.delete(
                f"/user/{user2_id}",
                headers={"x-csrf-token": token_user1},
                cookies={"auth_sid": auth_sid_user1}
            )

            Assertions.assert_code_status(response_delete, 400)
            assert (response_delete.json()["error"] ==
                    "This user can only delete their own account."), f"Unexpected response: {response_delete.text}"

        with allure.step("Check user2 still exists"):
            response_get_details = MyRequests.get(f"/user/{user2_id}")

            Assertions.assert_code_status(response_get_details, 200)
            Assertions.assert_json_has_key(response_get_details, "username")