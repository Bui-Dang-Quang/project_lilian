import unittest
from unittest.mock import MagicMock, patch
import io # Used to capture stdout

# Import the class we are testing
from submission.services.product_service import ProductService

# We will use MagicMock to create stand-ins for
# the DataStore and Product models.

class TestProductService(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh service and mock DataStore for each test.
        """
        self.mock_data_store = MagicMock()
        self.product_service = ProductService(data_store=self.mock_data_store)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_update_product_price_success(self, mock_stdout):
        """
        Tests that a product's price is updated successfully.
        (The "Happy Path")
        """
        # 1. Arrange
        # Create a mock Product object
        mock_product = MagicMock()
        mock_product.name = "Test Widget"
        mock_product.price = 10.00
        
        # Configure the mock DataStore to return this product
        self.mock_data_store.get_product.return_value = mock_product
        
        # 2. Act
        result = self.product_service.update_product_price("P123", 15.50)
        
        # 3. Assert
        # Check the method returned True
        self.assertTrue(result)
        
        # Check that we tried to find the product
        self.mock_data_store.get_product.assert_called_once_with("P123")
        
        # Check that the price on the mock object was updated
        self.assertEqual(mock_product.price, 15.50)
        
        # Check that the correct message was printed
        expected_output = "Updated Test Widget price from $10.00 to $15.50\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_update_product_price_not_found(self, mock_stdout):
        """
        Tests that the method returns False if the product is not found.
        (The "Sad Path")
        """
        # 1. Arrange
        # Configure the mock DataStore to return None
        self.mock_data_store.get_product.return_value = None
        
        # 2. Act
        result = self.product_service.update_product_price("P_BAD", 15.50)
        
        # 3. Assert
        # Check the method returned False
        self.assertFalse(result)
        
        # Check that we tried to find the product
        self.mock_data_store.get_product.assert_called_once_with("P_BAD")
        
        # Check that nothing was printed
        self.assertEqual(mock_stdout.getvalue(), "")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
