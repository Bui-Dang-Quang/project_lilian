import unittest
from unittest.mock import MagicMock, patch, call
import io # Used to capture stdout

from submission.services.inventory_service import InventoryService


class TestInventoryService(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh service and mock dependencies for each test.
        """
        self.mock_data_store = MagicMock()
        self.mock_supplier_service = MagicMock()
        
        # Instantiate the service with the MOCK dependencies
        self.inventory_service = InventoryService(
            data_store=self.mock_data_store,
            supplier_service=self.mock_supplier_service
        )

    def test_deduct_stock_and_log(self):
        """
        Tests that stock is correctly deducted and the change is logged.
        """
        # 1. Arrange
        # Create mock domain models
        mock_product = MagicMock()
        mock_product.quantity_available = 20
        
        mock_item = MagicMock()
        mock_item.product_id = "P100"
        mock_item.quantity = 2
        
        mock_order = MagicMock()
        mock_order.order_id = "O500"
        
        # Configure the DataStore mock to return the mock product
        self.mock_data_store.get_product.return_value = mock_product

        # 2. Act
        self.inventory_service.deduct_stock_and_log([mock_item], mock_order)

        # 3. Assert
        # Check that we retrieved the product
        self.mock_data_store.get_product.assert_called_once_with("P100")
        
        # Check that the product's quantity was reduced in-memory
        self.assertEqual(mock_product.quantity_available, 18) # 20 - 2
        
        # Check that the change was logged with the correct details
        self.mock_data_store.log_inventory_change.assert_called_once_with(
            "P100", -2, "order_O500"
        )

    def test_check_and_notify_low_stock_triggers_notification(self):
        """
        Tests that the supplier is notified if stock drops below the threshold (5).
        """
        # 1. Arrange
        # This product has stock *below* the threshold of 5
        mock_low_stock_product = MagicMock()
        mock_low_stock_product.quantity_available = 3 
        
        mock_item = MagicMock()
        mock_item.product_id = "P101"

        self.mock_data_store.get_product.return_value = mock_low_stock_product

        # 2. Act
        self.inventory_service.check_and_notify_low_stock([mock_item])

        # 3. Assert
        self.mock_data_store.get_product.assert_called_once_with("P101")
        
        # Check that the supplier service was called
        self.mock_supplier_service.notify_supplier_reorder.assert_called_once_with(
            mock_low_stock_product
        )

    def test_check_and_notify_low_stock_does_not_trigger(self):
        """
        Tests that the supplier is *not* notified if stock is sufficient.
        """
        # 1. Arrange
        # This product has stock *above* the threshold of 5
        mock_high_stock_product = MagicMock()
        mock_high_stock_product.quantity_available = 10
        
        mock_item = MagicMock()
        mock_item.product_id = "P102"

        self.mock_data_store.get_product.return_value = mock_high_stock_product

        # 2. Act
        self.inventory_service.check_and_notify_low_stock([mock_item])

        # 3. Assert
        self.mock_data_store.get_product.assert_called_once_with("P102")
        
        # Check that the supplier service was *not* called
        self.mock_supplier_service.notify_supplier_reorder.assert_not_called()

    def test_restore_stock(self):
        """
        Tests that stock is correctly restored (e.g., for a canceled order).
        """
        # 1. Arrange
        mock_product = MagicMock()
        mock_product.quantity_available = 15
        
        mock_item = MagicMock()
        mock_item.product_id = "P100"
        mock_item.quantity = 5
        
        # The mock order needs an 'items' attribute to be iterable
        mock_order = MagicMock()
        mock_order.order_id = "O501"
        mock_order.items = [mock_item] 
        
        self.mock_data_store.get_product.return_value = mock_product

        # 2. Act
        self.inventory_service.restore_stock(mock_order)

        # 3. Assert
        self.mock_data_store.get_product.assert_called_once_with("P100")
        
        # Check that the product's quantity was increased
        self.assertEqual(mock_product.quantity_available, 20) # 15 + 5
        
        # Check that the (positive) change was logged
        self.mock_data_store.log_inventory_change.assert_called_once_with(
            "P100", 5, "cancel_order_O501"
        )

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_restock_product_success(self, mock_stdout):
        """
        Tests the happy path for restocking a product.
        """
        # 1. Arrange
        mock_product = MagicMock()
        mock_product.quantity_available = 10
        mock_product.supplier_id = "S1"
        mock_product.name = "Test Widget"
        
        self.mock_data_store.get_product.return_value = mock_product
        
        # 2. Act
        result = self.inventory_service.restock_product("P1", 40, "S1")

        # 3. Assert
        self.assertTrue(result)
        self.assertEqual(mock_product.quantity_available, 50) # 10 + 40
        self.mock_data_store.log_inventory_change.assert_called_once_with(
            "P1", 40, "restock"
        )
        self.assertIn("Restocked Test Widget by 40", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_restock_product_not_found(self, mock_stdout):
        """
        Tests restocking failure if the product ID does not exist.
        """
        # 1. Arrange
        self.mock_data_store.get_product.return_value = None # Product not found
        
        # 2. Act
        result = self.inventory_service.restock_product("P_BAD", 40)

        # 3. Assert
        self.assertFalse(result)
        # Check that no logging or stock changes occurred
        self.mock_data_store.log_inventory_change.assert_not_called()
        self.assertIn("Product not found", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_restock_product_supplier_mismatch(self, mock_stdout):
        """
        Tests restocking failure if the supplier ID does not match.
        """
        # 1. Arrange
        mock_product = MagicMock()
        mock_product.quantity_available = 10
        mock_product.supplier_id = "S1" # The correct supplier
        
        self.mock_data_store.get_product.return_value = mock_product
        
        # 2. Act
        # We try to restock with "S_WRONG"
        result = self.inventory_service.restock_product("P1", 40, "S_WRONG")

        # 3. Assert
        self.assertFalse(result)
        # Stock should not have changed
        self.assertEqual(mock_product.quantity_available, 10)
        # No log should have been made
        self.mock_data_store.log_inventory_change.assert_not_called()
        self.assertIn("Supplier mismatch", mock_stdout.getvalue())

    def test_get_low_stock_products(self):
        """
        Tests that the service correctly filters for low-stock products.
        """
        # 1. Arrange
        # Create mock products
        prod_low = MagicMock()
        prod_low.quantity_available = 5
        
        prod_high = MagicMock()
        prod_high.quantity_available = 50
        
        prod_exact = MagicMock()
        prod_exact.quantity_available = 10 # Should be included (<=)

        # Configure the mock DataStore to return these products
        # when '.products.values()' is called
        self.mock_data_store.products.values.return_value = [prod_low, prod_high, prod_exact]

        # 2. Act
        # Use the default threshold of 10
        low_stock_list = self.inventory_service.get_low_stock_products() 

        # 3. Assert
        self.assertEqual(len(low_stock_list), 2)
        self.assertIn(prod_low, low_stock_list)
        self.assertIn(prod_exact, low_stock_list)
        self.assertNotIn(prod_high, low_stock_list)

    def test_check_stock_availability_success(self):
        """
        Tests the happy path where all items are in stock.
        """
        # 1. Arrange
        prod_a = MagicMock(); prod_a.quantity_available = 10
        prod_b = MagicMock(); prod_b.quantity_available = 5
        
        item_a = MagicMock(); item_a.product_id = "A"; item_a.quantity = 2
        item_b = MagicMock(); item_b.product_id = "B"; item_b.quantity = 5
        
        # Use .side_effect to return different values on sequential calls
        self.mock_data_store.get_product.side_effect = [prod_a, prod_b]

        # 2. Act
        result = self.inventory_service.check_stock_availability([item_a, item_b])

        # 3. Assert
        self.assertTrue(result)
        # Check that get_product was called for both items
        self.mock_data_store.get_product.assert_has_calls([call("A"), call("B")])

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_check_stock_availability_insufficient_stock(self, mock_stdout):
        """
        Tests failure when an item's requested quantity exceeds available stock.
        """
        # 1. Arrange
        prod_a = MagicMock()
        prod_a.quantity_available = 10 # Has stock
        prod_a.name = "Product A"
        
        prod_b = MagicMock()
        prod_b.quantity_available = 4   # Not enough stock
        prod_b.name = "Product B"
        
        item_a = MagicMock(); item_a.product_id = "A"; item_a.quantity = 2
        item_b = MagicMock(); item_b.product_id = "B"; item_b.quantity = 5 # Requesting 5
        
        self.mock_data_store.get_product.side_effect = [prod_a, prod_b]

        # 2. Act
        result = self.inventory_service.check_stock_availability([item_a, item_b])

        # 3. Assert
        self.assertFalse(result)
        # Check it failed on the second item
        self.mock_data_store.get_product.assert_has_calls([call("A"), call("B")])
        self.assertIn("Not enough stock for Product B", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_check_stock_availability_product_not_found(self, mock_stdout):
        """
        Tests failure when a product ID in the order does not exist.
        """
        # 1. Arrange
        item_bad = MagicMock(); item_bad.product_id = "P_BAD"; item_bad.quantity = 1
        
        # Configure get_product to return None for this ID
        self.mock_data_store.get_product.return_value = None

        # 2. Act
        result = self.inventory_service.check_stock_availability([item_bad])

        # 3. Assert
        self.assertFalse(result)
        self.mock_data_store.get_product.assert_called_once_with("P_BAD")
        self.assertIn("Product P_BAD not found", mock_stdout.getvalue())
