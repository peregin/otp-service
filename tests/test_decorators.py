from flask import Flask, jsonify
from http import HTTPStatus
from decorators import RequestValidators, handle_validation_error
import pytest


class TestDecorators:

    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def app_2(self):
        app_2 = Flask(__name__)
        return app_2

    def test_decorated_function_1(self):
        """
        Test that the validate_username decorator returns an error when username is missing
        """
        app = Flask(__name__)

        @app.route('/test', methods=['POST'])
        @RequestValidators.validate_username
        def test_route(username):
            return jsonify({"message": "Success"}), HTTPStatus.OK

        with app.test_client() as client:
            response = client.post('/test', json={})
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.get_json() == {"error": "Username is required"}

    def test_handle_validation_error_empty_input(self, app):
        """
        Test handle_validation_error with empty input
        """
        with app.test_request_context():
            response, status_code = handle_validation_error("")
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": ""}

    def test_handle_validation_error_long_string(self, app):
        """
        Test handle_validation_error with a very long string
        """
        long_error = "a" * 10000
        with app.test_request_context():
            response, status_code = handle_validation_error(long_error)
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": long_error}


    def test_handle_validation_error_special_characters(self, app):
        """
        Test handle_validation_error with special characters
        """
        special_chars = "!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`"
        with app.test_request_context():
            response, status_code = handle_validation_error(special_chars)
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": special_chars}


    def test_validate_otp_empty(self, app):
        """Test when OTP is empty in the request"""
        with app.test_request_context(json={"otp": ""}):
            @RequestValidators.validate_otp
            def dummy_function(**kwargs):
                return jsonify({"message": "Success"})

            response, status_code = dummy_function()
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": "OTP is required"}


    def test_validate_otp_empty_otp(self, app_2):
        """
        Test that validate_otp decorator returns an error when OTP is empty
        """

        @app_2.route('/test', methods=['POST'])
        @RequestValidators.validate_otp
        def test_route():
            return jsonify({"success": True}), HTTPStatus.OK

        with app_2.test_client() as client:
            response = client.post('/test', json={"otp": ""})
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.get_json() == {"error": "OTP is required"}


    def test_validate_otp_empty_otp_2(self, app_2):
        """
        Test the validate_otp decorator when OTP is an empty string
        """
        with app_2.test_request_context(json={"otp": ""}):
            @RequestValidators.validate_otp
            def dummy_function(*args, **kwargs):
                return "Success"

            response, status_code = dummy_function()
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": "OTP is required"}


    def test_validate_otp_exception_handling(self, app_2):
        """
        Test the validate_otp decorator's exception handling
        """
        with app_2.test_request_context(json={"otp": "123456"}):
            @RequestValidators.validate_otp
            def dummy_function(*args, **kwargs):
                raise ValueError("Test exception")

            with pytest.raises(ValueError, match="Test exception"):
                dummy_function()


    def test_validate_otp_malformed_json(self, app_2):
        """
        Test that validate_otp decorator handles malformed JSON input
        """

        @app_2.route('/test', methods=['POST'])
        @RequestValidators.validate_otp
        def test_route():
            return jsonify({"success": True}), HTTPStatus.OK

        with app_2.test_client() as client:
            response = client.post('/test', data="invalid json", content_type='application/json')
            assert response.status_code == HTTPStatus.BAD_REQUEST


    def test_validate_otp_missing(self):
        """
        Test that validate_otp returns an error when OTP is missing from the request.
        """
        app = Flask(__name__)

        @app.route('/test', methods=['POST'])
        @RequestValidators.validate_otp
        def test_route():
            return jsonify({"success": True}), HTTPStatus.OK

        with app.test_client() as client:
            response = client.post('/test', json={})

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.get_json() == {"error": "OTP is required"}


    def test_validate_otp_missing_2(self):
        """
        Test that validate_otp decorator returns an error when OTP is missing
        """
        app = Flask(__name__)

        @app.route('/test', methods=['POST'])
        @RequestValidators.validate_otp
        def test_endpoint(*args, **kwargs):
            return jsonify({"message": "Success"}), HTTPStatus.OK

        with app.test_client() as client:
            response = client.post('/test', json={})
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.get_json() == {"error": "OTP is required"}


    def test_validate_otp_missing_3(self, app):
        """Test when OTP is missing from the request"""
        with app.test_request_context(json={}):
            @RequestValidators.validate_otp
            def dummy_function(**kwargs):
                return jsonify({"message": "Success"})

            response, status_code = dummy_function()
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": "OTP is required"}


    def test_validate_otp_missing_otp(self, app_2):
        """
        Test that validate_otp decorator returns an error when OTP is missing
        """

        @app_2.route('/test', methods=['POST'])
        @RequestValidators.validate_otp
        def test_route():
            return jsonify({"success": True}), HTTPStatus.OK

        with app_2.test_client() as client:
            response = client.post('/test', json={})
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.get_json() == {"error": "OTP is required"}


    def test_validate_otp_missing_otp_2(self):
        """
        Test that the validate_otp decorator returns an error when OTP is missing
        """
        app = Flask(__name__)

        @app.route('/test', methods=['POST'])
        @RequestValidators.validate_otp
        def test_endpoint():
            return "Success", HTTPStatus.OK

        with app.test_client() as client:
            response = client.post('/test', json={})

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.get_json() == {"error": "OTP is required"}


    def test_validate_otp_missing_otp_3(self, app_2):
        """
        Test the validate_otp decorator when OTP is missing from the request
        """
        with app_2.test_request_context(json={}):
            @RequestValidators.validate_otp
            def dummy_function(*args, **kwargs):
                return "Success"

            response, status_code = dummy_function()
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": "OTP is required"}


    def test_validate_otp_non_string_input(self, app_2):
        """
        Test that validate_otp decorator handles non-string OTP input
        """

        @app_2.route('/test', methods=['POST'])
        @RequestValidators.validate_otp
        def test_route(otp):
            return jsonify({"success": True, "otp": otp}), HTTPStatus.OK

        with app_2.test_client() as client:
            response = client.post('/test', json={"otp": 12345})
            assert response.status_code == HTTPStatus.OK
            assert response.get_json() == {"success": True, "otp": 12345}


    def test_validate_otp_non_string_otp(self, app_2):
        """
        Test the validate_otp decorator when OTP is not a string
        """
        with app_2.test_request_context(json={"otp": 12345}):
            @RequestValidators.validate_otp
            def dummy_function(*args, **kwargs):
                return kwargs.get('otp')

            result = dummy_function()
            assert result == 12345


    def test_validate_otp_none(self, app):
        """Test when OTP is None in the request"""
        with app.test_request_context(json={"otp": None}):
            @RequestValidators.validate_otp
            def dummy_function(**kwargs):
                return jsonify({"message": "Success"})

            response, status_code = dummy_function()
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": "OTP is required"}


    def test_validate_otp_success(self, app_2):
        """
        Test that validate_otp decorator passes OTP to the wrapped function when present
        """

        @app_2.route('/test', methods=['POST'])
        @RequestValidators.validate_otp
        def test_route(otp):
            return jsonify({"success": True, "otp": otp}), HTTPStatus.OK

        with app_2.test_client() as client:
            response = client.post('/test', json={"otp": "123456"})
            assert response.status_code == HTTPStatus.OK
            assert response.get_json() == {"success": True, "otp": "123456"}


    def test_validate_otp_valid(self):
        """
        Test that validate_otp decorator passes when OTP is provided
        """
        app = Flask(__name__)

        @app.route('/test', methods=['POST'])
        @RequestValidators.validate_otp
        def test_endpoint(*args, **kwargs):
            return jsonify({"message": "Success", "otp": kwargs.get('otp')}), HTTPStatus.OK

        with app.test_client() as client:
            response = client.post('/test', json={"otp": "123456"})
            assert response.status_code == HTTPStatus.OK
            assert response.get_json() == {"message": "Success", "otp": "123456"}


    def test_validate_otp_with_additional_data(self, app_2):
        """
        Test the validate_otp decorator with additional data in the request
        """
        with app_2.test_request_context(json={"otp": "123456", "extra": "data"}):
            @RequestValidators.validate_otp
            def dummy_function(*args, **kwargs):
                return kwargs

            result = dummy_function()
            assert 'otp' in result
            assert result['otp'] == "123456"


    def test_validate_username_empty(self, app):
        """Test when username is empty in the request"""
        with app.test_request_context(json={"username": ""}):
            @RequestValidators.validate_username
            def dummy_function(username):
                return jsonify({"message": "Success"})

            response, status_code = dummy_function()
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": "Username is required"}


    def test_validate_username_empty_input(self, app):
        """
        Test validate_username decorator with empty username input
        """

        @RequestValidators.validate_username
        def dummy_function(username):
            return jsonify({"message": "Success"}), HTTPStatus.OK

        with app.test_request_context(json={}):
            response, status_code = dummy_function()
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": "Username is required"}


    def test_validate_username_exception_handling(self, app):
        """
        Test validate_username decorator exception handling
        """

        @RequestValidators.validate_username
        def dummy_function(username):
            raise ValueError("Test exception")

        with app.test_request_context(json={"username": "test_user"}):
            with pytest.raises(ValueError, match="Test exception"):
                dummy_function()


    def test_validate_username_incorrect_type(self, app):
        """
        Test validate_username decorator with incorrect input type
        """

        @RequestValidators.validate_username
        def dummy_function(username):
            return jsonify({"message": "Success"}), HTTPStatus.OK

        with app.test_request_context(json={"username": 12345}):
            response, status_code = dummy_function()
            assert status_code == HTTPStatus.OK
            assert response.json == {"message": "Success"}


    def test_validate_username_missing(self):
        """
        Test that validate_username decorator returns an error when username is missing
        """
        app = Flask(__name__)

        @app.route('/test', methods=['POST'])
        @RequestValidators.validate_username
        def test_endpoint(username):
            return jsonify({"message": f"Hello, {username}!"}), HTTPStatus.OK

        with app.test_client() as client:
            response = client.post('/test', json={})
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.get_json() == {"error": "Username is required"}


    def test_validate_username_missing_2(self):
        """
        Test that validate_username decorator returns an error when username is missing.
        """
        app = Flask(__name__)

        @app.route('/test', methods=['POST'])
        @RequestValidators.validate_username
        def test_endpoint(username):
            return jsonify({"message": "Success"}), HTTPStatus.OK

        with app.test_client() as client:
            response = client.post('/test', json={})

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.get_json() == {"error": "Username is required"}


    def test_validate_username_missing_3(self, app):
        """Test when username is missing from the request"""
        with app.test_request_context(json={}):
            @RequestValidators.validate_username
            def dummy_function(username):
                return jsonify({"message": "Success"})

            response, status_code = dummy_function()
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": "Username is required"}


    def test_validate_username_missing_username(self):
        """
        Test that the validate_username decorator returns an error when username is missing
        """
        app = Flask(__name__)

        @app.route('/test', methods=['POST'])
        @RequestValidators.validate_username
        def test_route(username):
            return jsonify({"message": "Success"}), HTTPStatus.OK

        with app.test_client() as client:
            response = client.post('/test', json={})
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.get_json() == {"error": "Username is required"}


    def test_validate_username_none(self, app):
        """Test when username is None in the request"""
        with app.test_request_context(json={"username": None}):
            @RequestValidators.validate_username
            def dummy_function(username):
                return jsonify({"message": "Success"})

            response, status_code = dummy_function()
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": "Username is required"}


    def test_validate_username_none_input(self, app):
        """
        Test validate_username decorator with None as username input
        """

        @RequestValidators.validate_username
        def dummy_function(username):
            return jsonify({"message": "Success"}), HTTPStatus.OK

        with app.test_request_context(json={"username": None}):
            response, status_code = dummy_function()
            assert status_code == HTTPStatus.BAD_REQUEST
            assert response.json == {"error": "Username is required"}


    def test_validate_username_present(self):
        """
        Test that validate_username decorator allows the request when username is present
        """
        app = Flask(__name__)

        @app.route('/test', methods=['POST'])
        @RequestValidators.validate_username
        def test_endpoint(username):
            return jsonify({"message": f"Hello, {username}!"}), HTTPStatus.OK

        with app.test_client() as client:
            response = client.post('/test', json={"username": "testuser"})
            assert response.status_code == HTTPStatus.OK
            assert response.get_json() == {"message": "Hello, testuser!"}


    def test_validate_username_whitespace_only(self, app):
        """
        Test validate_username decorator with whitespace-only input
        """

        @RequestValidators.validate_username
        def dummy_function(username):
            return jsonify({"message": "Success"}), HTTPStatus.OK

        with app.test_request_context(json={"username": "   "}):
            response, status_code = dummy_function()
            assert status_code == HTTPStatus.OK
            assert response.json == {"message": "Success"}
