from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

class BaseServiceConnector(ABC):
    """
    Abstract Base Class for Simulated External Service Connectors.
    All operations are strictly controlled tools; LLM never mutates external services directly.
    """
    def __init__(self, provider_name: str, category: str):
        self.provider_name = provider_name
        self.category = category

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_payment(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_cancellation_policy(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_delivery_status(self, order_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_refund_status(self, refund_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_refund(self, transaction_id: str, amount: float, reason: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_case(self, customer_id: str, issue_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        pass


class RedBusConnector(BaseServiceConnector):
    """Simulated connector for RedBus bus ticket reservations."""
    def __init__(self):
        super().__init__("RedBus", "TRAVEL_BUS")

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return self.get_booking(order_id)

    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        return {
            "booking_id": booking_id,
            "provider": "RedBus",
            "service_type": "Intercity Bus",
            "route": "Bengaluru (KBS) -> Mumbai (Borivali)",
            "departure_time": "2026-10-22T20:30:00",
            "status": "CONFIRMED",
            "amount": 2499.0,
            "seat_numbers": ["12A", "12B"]
        }

    def get_payment(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        return {
            "transaction_id": transaction_id,
            "gateway": "RAZORPAY",
            "status": "SUCCESS",
            "amount": 2499.0,
            "timestamp": "2026-10-20T10:14:00"
        }

    def get_cancellation_policy(self) -> Dict[str, Any]:
        return {
            "policy_id": "POL-RB-01",
            "provider": "RedBus",
            "window_hours": 24,
            "refund_percentage_within_window": 100.0,
            "refund_percentage_after_window": 0.0,
            "terms": "Free cancellation with 100% refund up to 24 hours before scheduled departure."
        }

    def get_delivery_status(self, order_id: str) -> Dict[str, Any]:
        return {"status": "TICKET_ISSUED", "provider": "RedBus", "pnr": "RB-992182"}

    def get_refund_status(self, refund_id: str) -> Optional[Dict[str, Any]]:
        return {"refund_id": refund_id, "status": "PROCESSING", "arn": "ARN-UPI-REDBUS-991"}

    def create_refund(self, transaction_id: str, amount: float, reason: str) -> Dict[str, Any]:
        arn = f"ARN-UPI-RB-{hash(transaction_id) % 100000000:08d}"
        ref_id = f"RF-RB-{datetime.now().strftime('%M%S')}"
        return {
            "success": True,
            "refund_id": ref_id,
            "arn": arn,
            "amount": amount,
            "provider": "RedBus",
            "reason": reason,
            "timeline": "3-5 business days"
        }

    def cancel_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        return {"success": True, "booking_id": order_id, "status": "CANCELLED", "reason": reason}

    def create_case(self, customer_id: str, issue_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return {"case_id": f"RB-CASE-{datetime.now().strftime('%M%S')}", "status": "OPEN", "priority": "NORMAL"}


class MakeMyTripConnector(BaseServiceConnector):
    """Simulated connector for MakeMyTrip hotel & flight bookings."""
    def __init__(self):
        super().__init__("MakeMyTrip", "TRAVEL_HOTEL_FLIGHT")

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return self.get_booking(order_id)

    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        return {
            "booking_id": booking_id,
            "provider": "MakeMyTrip",
            "service_type": "Hotel Booking",
            "property": "Grand Hyatt Goa Resort & Spa",
            "checkin_date": "2026-10-25T14:00:00",
            "status": "CONFIRMED",
            "amount": 6800.0,
            "free_cancellation_until": "2026-10-23T23:59:59"
        }

    def get_payment(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        return {
            "transaction_id": transaction_id,
            "gateway": "PAYU",
            "status": "SUCCESS",
            "amount": 6800.0
        }

    def get_cancellation_policy(self) -> Dict[str, Any]:
        return {
            "policy_id": "POL-MMT-01",
            "provider": "MakeMyTrip",
            "terms": "Free cancellation allowed up to 48 hours prior to check-in. Non-refundable thereafter."
        }

    def get_delivery_status(self, order_id: str) -> Dict[str, Any]:
        return {"status": "VOUCHER_CONFIRMED", "provider": "MakeMyTrip"}

    def get_refund_status(self, refund_id: str) -> Optional[Dict[str, Any]]:
        return {"refund_id": refund_id, "status": "COMPLETED", "arn": "ARN-MMT-551982"}

    def create_refund(self, transaction_id: str, amount: float, reason: str) -> Dict[str, Any]:
        arn = f"ARN-MMT-{hash(transaction_id) % 100000000:08d}"
        ref_id = f"RF-MMT-{datetime.now().strftime('%M%S')}"
        return {"success": True, "refund_id": ref_id, "arn": arn, "amount": amount, "provider": "MakeMyTrip"}

    def cancel_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        return {"success": True, "booking_id": order_id, "status": "CANCELLED_REFUNDABLE"}

    def create_case(self, customer_id: str, issue_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return {"case_id": f"MMT-CASE-{datetime.now().strftime('%M%S')}", "status": "OPEN"}


class AmazonConnector(BaseServiceConnector):
    """Simulated connector for Amazon e-commerce purchases."""
    def __init__(self):
        super().__init__("Amazon", "ECOMMERCE")

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return {
            "order_id": order_id,
            "provider": "Amazon",
            "item_name": "Sony WH-1000XM5 Wireless Headphones",
            "status": "DELIVERED",
            "delivery_timestamp": "2026-10-19T14:20:00",
            "amount": 26990.0,
            "return_window_days": 7
        }

    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        return None

    def get_payment(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        return {"transaction_id": transaction_id, "gateway": "AMAZON_PAY", "status": "SUCCESS"}

    def get_cancellation_policy(self) -> Dict[str, Any]:
        return {
            "policy_id": "POL-AMZ-01",
            "provider": "Amazon",
            "terms": "7-day replacement or refund for damaged, defective, or incorrect items."
        }

    def get_delivery_status(self, order_id: str) -> Dict[str, Any]:
        return {"status": "DELIVERED", "signed_by": "Customer", "carrier": "Amazon Logistics"}

    def get_refund_status(self, refund_id: str) -> Optional[Dict[str, Any]]:
        return {"refund_id": refund_id, "status": "SETTLED"}

    def create_refund(self, transaction_id: str, amount: float, reason: str) -> Dict[str, Any]:
        arn = f"ARN-AMZ-{hash(transaction_id) % 100000000:08d}"
        ref_id = f"RF-AMZ-{datetime.now().strftime('%M%S')}"
        return {"success": True, "refund_id": ref_id, "arn": arn, "amount": amount, "provider": "Amazon"}

    def cancel_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        return {"success": True, "order_id": order_id, "status": "RETURN_PICKUP_SCHEDULED"}

    def create_case(self, customer_id: str, issue_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return {"case_id": f"AMZ-CASE-{datetime.now().strftime('%M%S')}", "status": "OPEN"}


class FlipkartConnector(BaseServiceConnector):
    """Simulated connector for Flipkart e-commerce orders."""
    def __init__(self):
        super().__init__("Flipkart", "ECOMMERCE")

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return {
            "order_id": order_id,
            "provider": "Flipkart",
            "item_name": "Apple iPhone 15 (128 GB) - Blue",
            "status": "DELIVERED",
            "amount": 58999.0
        }

    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        return None

    def get_payment(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        return {"transaction_id": transaction_id, "gateway": "PHONEPE", "status": "SUCCESS"}

    def get_cancellation_policy(self) -> Dict[str, Any]:
        return {"policy_id": "POL-FK-01", "provider": "Flipkart", "terms": "7-day replacement policy."}

    def get_delivery_status(self, order_id: str) -> Dict[str, Any]:
        return {"status": "DELIVERED", "carrier": "Ekart"}

    def get_refund_status(self, refund_id: str) -> Optional[Dict[str, Any]]:
        return {"refund_id": refund_id, "status": "PROCESSING"}

    def create_refund(self, transaction_id: str, amount: float, reason: str) -> Dict[str, Any]:
        arn = f"ARN-FK-{hash(transaction_id) % 100000000:08d}"
        return {"success": True, "refund_id": f"RF-FK-{datetime.now().strftime('%M%S')}", "arn": arn, "amount": amount}

    def cancel_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        return {"success": True, "order_id": order_id, "status": "CANCELLED"}

    def create_case(self, customer_id: str, issue_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return {"case_id": f"FK-CASE-{datetime.now().strftime('%M%S')}", "status": "OPEN"}


class SwiggyConnector(BaseServiceConnector):
    """Simulated connector for Swiggy food delivery."""
    def __init__(self):
        super().__init__("Swiggy", "FOOD_DELIVERY")

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return {
            "order_id": order_id,
            "provider": "Swiggy",
            "restaurant": "Meghana Foods (Indiranagar)",
            "status": "DELIVERED_WRONG_ITEM",
            "amount": 749.0
        }

    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        return None

    def get_payment(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        return {"transaction_id": transaction_id, "gateway": "SWIGGY_PAY", "status": "SUCCESS"}

    def get_cancellation_policy(self) -> Dict[str, Any]:
        return {"policy_id": "POL-SWG-01", "provider": "Swiggy", "terms": "Instant refund for missing or wrong food items."}

    def get_delivery_status(self, order_id: str) -> Dict[str, Any]:
        return {"status": "DELIVERED", "delivery_partner": "Ramesh K."}

    def get_refund_status(self, refund_id: str) -> Optional[Dict[str, Any]]:
        return {"refund_id": refund_id, "status": "SETTLED"}

    def create_refund(self, transaction_id: str, amount: float, reason: str) -> Dict[str, Any]:
        arn = f"ARN-SWG-{hash(transaction_id) % 100000000:08d}"
        return {"success": True, "refund_id": f"RF-SWG-{datetime.now().strftime('%M%S')}", "arn": arn, "amount": amount}

    def cancel_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        return {"success": True, "order_id": order_id, "status": "REFUNDED"}

    def create_case(self, customer_id: str, issue_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return {"case_id": f"SWG-CASE-{datetime.now().strftime('%M%S')}", "status": "RESOLVED_AUTO"}


class GenericMerchantConnector(BaseServiceConnector):
    """Simulated connector for generic merchant payments & checkout."""
    def __init__(self):
        super().__init__("Generic Merchant", "GENERAL_COMMERCE")

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return {"order_id": order_id, "provider": "Generic Merchant", "amount": 2499.0, "status": "FAILED"}

    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        return None

    def get_payment(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        return {"transaction_id": transaction_id, "gateway": "RAZORPAY", "status": "SUCCESS"}

    def get_cancellation_policy(self) -> Dict[str, Any]:
        return {"policy_id": "POL-GEN-01", "provider": "Generic Merchant", "terms": "Standard refund policy."}

    def get_delivery_status(self, order_id: str) -> Dict[str, Any]:
        return {"status": "UNFULFILLED"}

    def get_refund_status(self, refund_id: str) -> Optional[Dict[str, Any]]:
        return {"refund_id": refund_id, "status": "PROCESSING"}

    def create_refund(self, transaction_id: str, amount: float, reason: str) -> Dict[str, Any]:
        arn = f"ARN-UPI-{hash(transaction_id) % 100000000:08d}"
        return {"success": True, "refund_id": f"RF-GEN-{datetime.now().strftime('%M%S')}", "arn": arn, "amount": amount}

    def cancel_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        return {"success": True, "order_id": order_id, "status": "CANCELLED"}

    def create_case(self, customer_id: str, issue_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return {"case_id": f"GEN-CASE-{datetime.now().strftime('%M%S')}", "status": "OPEN"}


class ServiceConnectorRegistry:
    """Registry managing simulated service connectors."""
    def __init__(self):
        self._connectors: Dict[str, BaseServiceConnector] = {
            "redbus": RedBusConnector(),
            "makemytrip": MakeMyTripConnector(),
            "amazon": AmazonConnector(),
            "flipkart": FlipkartConnector(),
            "swiggy": SwiggyConnector(),
            "generic": GenericMerchantConnector()
        }

    def get_connector(self, provider_name: Optional[str]) -> BaseServiceConnector:
        if not provider_name:
            return self._connectors["generic"]
        p_clean = provider_name.lower().replace(" ", "").replace("_", "")
        for key, conn in self._connectors.items():
            if key in p_clean or p_clean in key:
                return conn
        return self._connectors["generic"]

    def identify_provider(self, text: str, entity_id: str = "") -> str:
        """Determines service provider from text, order prefix, or evidence."""
        t_low = text.lower()
        if "redbus" in t_low or entity_id.startswith("RB-"):
            return "RedBus"
        if "makemytrip" in t_low or "mmt" in t_low or entity_id.startswith("MMT-"):
            return "MakeMyTrip"
        if "amazon" in t_low or "amz" in t_low or entity_id.startswith("AMZ-"):
            return "Amazon"
        if "flipkart" in t_low or entity_id.startswith("FK-"):
            return "Flipkart"
        if "swiggy" in t_low or entity_id.startswith("SWG-"):
            return "Swiggy"
        return "Generic Merchant"

# Global registry singleton
service_registry = ServiceConnectorRegistry()
