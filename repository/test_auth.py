import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from repository.auth import check_exist_user, login, check_user_password, regis, edit_password, list_user
from schemas.auth import LoginRequest, SignupRequest, EditPassRequest

class TestAuth(unittest.IsolatedAsyncioTestCase):
    async def test_login_success(self):
        db = MagicMock()
        db.table().select().execute.return_value.data = [{"email": "test@example.com", "password": "hashedpass"}]
        request = LoginRequest(email="test@example.com", password="sigma")
        
        response = await login(db, request)
        self.assertEqual(response["email"], "test@example.com")

    async def test_login_user_not_found(self):
        db = MagicMock()
        db.table().select().execute.return_value.data = []
        
        request = LoginRequest(email="notfound@example.com", password="sigma")
        
        with self.assertRaises(IndexError):
            await login(db, request)
            
    async def test_login_invalid_password(self):
        db = MagicMock()
        db.table().select().execute.return_value.data = [{"email": "test@example.com", "password": "hashedpass"}]
        
        request = LoginRequest(email="test@example.com", password="wrongpassword")
        
        with self.assertRaises(ValueError) as context:
            await login(db, request)
        self.assertEqual(str(context.exception), "Invalid credentical")

    def test_check_user_password_correct(self):
        db = MagicMock()
        db.table().select().eq().execute.return_value.data = [{"email": "test@example.com", "password": "sigma"}]
        
        result = check_user_password(db, "test@example.com", "sigma")
        self.assertEqual(result["email"], "test@example.com")

    def test_check_user_password_incorrect(self):
        db = MagicMock()
        db.table().select().eq().execute.return_value.data = []
        
        with self.assertRaises(ValueError) as context:
            check_user_password(db, "test@example.com", "wrongpass")
        self.assertEqual(str(context.exception), "Invalid credentical")

    def test_user_exists(self):
        db = MagicMock()
        db.table().select().or_().execute.return_value.data = [{"id": "1"}]
        
        result = check_exist_user(db, "test@example.com", "testuser")
        self.assertTrue(result)
    
    def test_user_does_not_exist(self):
        db = MagicMock()
        db.table().select().or_().execute.return_value.data = []
        
        result = check_exist_user(db, "notfound@example.com", "notfounduser")
        self.assertFalse(result)
        
    def test_check_exist_user_db_error(self):
        db = MagicMock()
        db.table().select().or_().execute.side_effect = Exception("Database error")

        result = check_exist_user(db, "error@example.com", "erroruser")

        self.assertFalse(result)

    async def test_regis_success(self):
        db = MagicMock()
        with patch("repository.auth.check_exist_user", return_value=False):
            db.table().insert().execute.return_value = "Success"

            request = SignupRequest(username="newuser", email="newuser@example.com", password="password123", full_name="John Doe", phone_number="1234567890")

            response = await regis(db, request)
            self.assertEqual(response, "Success")
            
    async def test_regis_failure(self):
        db = MagicMock()
        db.table().insert().execute.side_effect = Exception("Database error")

        request = SignupRequest(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            full_name="John Doe",
            phone_number="1234567890"
        )

        with patch("repository.auth.check_exist_user", return_value=False):
            with self.assertRaises(ValueError) as context:
                await regis(db, request)
            self.assertEqual(str(context.exception), "Database error")

    async def test_regis_user_already_exist(self):
        db = MagicMock()
        
        request = SignupRequest(
            username="existinguser",
            email="existing@example.com",
            password="password123",
            full_name="John Doe",
            phone_number="1234567890"
        )

        with patch("repository.auth.check_exist_user", return_value=True):
            with self.assertRaises(ValueError) as context:
                await regis(db, request)
            self.assertEqual(str(context.exception), "User already exist")


    async def test_edit_password_success(self):
        db = MagicMock()
        db.table().update().eq().execute.return_value = MagicMock(data=[{"id": 1}])

        request = EditPassRequest(
            email="test@example.com",
            password="newpassword",
            confim_password="newpassword"
        )

        response = await edit_password(db, request)
        self.assertEqual(response, "Success")

    async def test_edit_password_failure(self):
        db = MagicMock()
        db.table().update().eq().execute.side_effect = Exception("Database error")

        request = EditPassRequest(
            email="test@example.com",
            password="newpassword",
            confim_password="newpassword"
        )

        with self.assertRaises(ValueError) as context:
            await edit_password(db, request)
        self.assertEqual(str(context.exception), "Database error")
        
    async def test_edit_password_user_not_found(self):
        db = MagicMock()
        db.table().update().eq().execute.return_value = MagicMock(data=[])

        request = EditPassRequest(
            email="notfound@example.com",
            password="newpassword",
            confim_password="newpassword"
        )

        with self.assertRaises(ValueError) as context:
            await edit_password(db, request)

        self.assertEqual(str(context.exception), "User not found")


    async def test_list_user(self):
        db = MagicMock()
        db.table().select().range().execute.return_value.data = [{"email": "user1@example.com"}, {"email": "user2@example.com"}]
        
        response, count = await list_user(db)
        self.assertEqual(len(response), 2)
        self.assertEqual(count, 2)
        
    async def test_list_user_failure(self):
        db = MagicMock()
        db.table().select().range().execute.side_effect = Exception("Database error")

        with self.assertRaises(ValueError) as context:
            await list_user(db)
        self.assertEqual(str(context.exception), "Database error")
        
    @patch("unittest.main")
    def test_main_called(self, mock_main):
        unittest.main()
        mock_main.assert_called_once()

if __name__ == "__main__":
    unittest.main()
