from io import BytesIO
from qr import generate_qr
import unittest

class TestQr(unittest.TestCase):

    def test_generate_qr_invalid_input(self):
        """
        Test generate_qr with empty input (None)
        """
        result = generate_qr(None)
        assert isinstance(result, BytesIO)
        assert result.getvalue().startswith(b'\x89PNG')

    def test_generate_qr_non_ascii_input(self):
        """
        Test generate_qr with non-ASCII input
        """
        result = generate_qr("こんにちは")  # Japanese for "hello"
        assert isinstance(result, BytesIO)
        assert result.getvalue().startswith(b'\x89PNG')

    def test_generate_qr_special_characters(self):
        """
        Test generate_qr with special characters
        """
        result = generate_qr("!@#$%^&*()")
        assert isinstance(result, BytesIO)
        assert result.getvalue().startswith(b'\x89PNG')

    def test_generate_qr_with_valid_data(self):
        """
        Test generate_qr function with valid input data.
        """
        # Arrange
        test_data = "Test QR Code Data"

        # Act
        result = generate_qr(test_data)

        # Assert
        assert isinstance(result, BytesIO)
        assert result.getvalue().startswith(b'\x89PNG')  # Check if it's a valid PNG image

if __name__ == '__main__':
    unittest.main()
