import unittest
from unittest.mock import MagicMock, patch
import io # Used to capture stdout

# Import the class we are testing
from submission.services.supplier_service import SupplierService

# We will create mock objects for the dependencies (Product, Supplier)
# so we don't need to import their real classes.

class TestSupplierService(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh environment for each test.
        """
        # 1. Create a mock for the DataStore dependency.
        # This mock will stand in for the real DataStore.
        self.mock_data_store = MagicMock()
        self.mock_data_store.get_supplier = MagicMock() # Mock the method we call
        
        # 2. Instantiate the service with the mock DataStore
        self.supplier_service = SupplierService(data_store=self.mock_data_store)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_notify_supplier_reorder_success(self, mock_stdout):
        """
        Tests that the correct notification is printed when a supplier is found.
        (The "Happy Path")
        """
        # 1. Arrange
        
        # Create a mock Supplier object that our DataStore will "find"
        mock_supplier = MagicMock()
        mock_supplier.email = "notify@supplier.com"
        
        # Create a mock Product object to pass to the service
        mock_product = MagicMock()
        mock_product.supplier_id = "S123"
        mock_product.name = "Test Widget"
        
        # Configure the mock DataStore to return the mock supplier
        self.mock_data_store.get_supplier.return_value = mock_supplier
        
        # 2. Act
        # Call the method we are testing
        self.supplier_service.notify_supplier_reorder(mock_product)
        
        # 3. Assert
        # Check that get_supplier was called once with the correct ID
        self.mock_data_store.get_supplier.assert_called_once_with("S123")
        
        # Check that the correct message was printed to stdout
        expected_output = "Email to notify@supplier.com: Low stock alert for Test Widget\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_notify_supplier_reorder_supplier_not_found(self, mock_stdout):
        """
        Tests that the correct warning is printed when no supplier is found.
        (The "Sad Path")
        """
        # 1. Arrange
        
        # Create a mock Product object
        mock_product = MagicMock()
        mock_product.supplier_id = "S_NONE"
        mock_product.product_id = "P789" # The method uses this for the warning
        mock_product.name = "Orphan Widget"
        
        # Configure the mock DataStore to return None (supplier not found)
        self.mock_data_store.get_supplier.return_value = None
        
        # 2. Act
        self.supplier_service.notify_supplier_reorder(mock_product)
        
        # 3. Assert
        # Check that get_supplier was called once with the correct ID
        self.mock_data_store.get_supplier.assert_called_once_with("S_NONE")
        
        # Check that the correct warning message was printed
        expected_output = "Warning: No supplier found for product P789\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)
