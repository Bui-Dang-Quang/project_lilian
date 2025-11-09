import unittest
from unittest.mock import MagicMock, patch, Mock
import datetime

# --- Import the class to be tested ---
from submission.services.shipping_service import ShippingService

# --- Import dependencies needed for mocks ---
# (We don't need to import the real classes if we remove the 'spec')
# from submission.repositories.in_memory.DataStore import DataStore
# from submission.domain.models.Order import Order
# from submission.domain.models.Customer import Customer

class TestShippingService(unittest.TestCase):
    
    def setUp(self):
        """Set up a fresh service and a mock datastore for each test."""
        # --- FIX: Remove spec=DataStore ---
        self.mock_datastore = MagicMock()
        self.shipping_service = ShippingService(self.mock_datastore)
    
    def test_shipping_cost_selects_standard_strategy(self):
        """
        Tests that shipping_cost correctly finds and
        executes the 'standard' strategy.
        """
        # --- FIX: Remove spec=Customer ---
        mock_customer = MagicMock()
        total_weight = 10.0
        subtotal = 40.0 # Should trigger $5 + (10 * 0.2) = $7.0
        
        cost = self.shipping_service.shipping_cost(
            "standard", total_weight, mock_customer, subtotal
        )
        
        self.assertEqual(cost, 7.0)

    def test_shipping_cost_selects_express_strategy(self):
        """
        Tests that shipping_cost correctly finds and
        executes the 'express' strategy for a gold member.
        """
        # --- FIX: Remove spec=Customer ---
        mock_customer = MagicMock()
        mock_customer.membership_tier.get_name.return_value = "gold"
        total_weight = 10.0
        subtotal = 100.0
        
        cost = self.shipping_service.shipping_cost(
            "express", total_weight, mock_customer, subtotal
        )
        
        self.assertEqual(cost, 15.0)

    def test_shipping_cost_invalid_method(self):
        """
        Tests that shipping_cost raises a ValueError
        for an unknown shipping method.
        """
        # --- FIX: Remove spec=Customer ---
        mock_customer = MagicMock()
        with self.assertRaises(ValueError) as context:
            self.shipping_service.shipping_cost(
                "invalid_method", 10.0, mock_customer, 100.0
            )
        
        self.assertIn("Invalid shipping method: invalid_method", str(context.exception))

    def test_create_shipment_for_order(self):
        """
        Tests that a shipment is created, saved to the datastore,
        and a tracking number is returned.
        """
        # --- FIX: Remove spec=Order ---
        mock_order = Mock(order_id=123) 
        self.mock_datastore.next_shipment_id = 1
        
        # We patch 'random.randint' in the *shipping_service* module
        with patch('submission.services.shipping_service.random.randint', return_value=9999):
            tracking_number = self.shipping_service.create_shipment_for_order(mock_order)
        
        # 1. Check the returned tracking number
        self.assertEqual(tracking_number, "TRACK1239999")
        
        # 2. Check that the datastore's ID was incremented
        self.assertEqual(self.mock_datastore.next_shipment_id, 2)
        
        # 3. Check that the shipment was saved to the datastore's dictionary
        self.mock_datastore.shipments.__setitem__.assert_called_once()
        
        call_args = self.mock_datastore.shipments.__setitem__.call_args[0]
        saved_shipment_id = call_args[0]
        saved_shipment_data = call_args[1]
        
        self.assertEqual(saved_shipment_id, 1)
        self.assertEqual(saved_shipment_data['shipment_id'], 1)
        self.assertEqual(saved_shipment_data['order_id'], 123)
        self.assertEqual(saved_shipment_data['tracking_number'], "TRACK1239999")
