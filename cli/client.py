# cli/client.py
import requests
from typing import Optional, Dict, Any
from cli.config import get_cli_settings, setup_cli_logging

settings = get_cli_settings()
logger = setup_cli_logging()

class APIClient:
    """HTTP client for API communication"""
    
    def __init__(self):
        self.base_url = settings.api_base_url
        self.headers = {"X-API-Key": settings.api_key}
        logger.info(f"API Client initialized: {self.base_url}")
        
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """ Make HTTP requests """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Request: {method} {endpoint}")
        try: 
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            logger.info(f"Success: {method} {url} - Status: {response.status_code}")
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {method} {url} - {e.response.status_code}")
            if e.response.status_code == 401:
                print("❌ Authentication failed. Check your API key.")
            elif e.response.status_code == 404:
                print("❌ Resource not found.")
            else:
                print(f"❌ Error: {e.response.json().get('detail', str(e))}")
            return {}
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection Error: {method} {url}")
            print("❌ Cannot connect to API. Is the server running?")
            return {}
        except Exception as e:
            logger.error(f"Unexpected Error: {method} {endpoint} - {str(e)}", exc_info=True)
            print(f"❌ Unexpected error: {str(e)}")
            return {}

    # User endpoints
    def create_user(self, name: str, email: str) -> Optional[Dict]:
        return self._request("POST", "/users/", json={"name": name, "email": email})
    
    def get_users(self, skip: int = 0, limit: int = 100) -> Optional[Dict]:
        print(f"Fetching users with skip={skip} and limit={limit}")
        return self._request("GET", "/users/", params={"skip": skip, "limit": limit})
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        return self._request("GET", f"/users/{user_id}")
    
    def get_user_summary(self, user_id: int) -> Optional[Dict]:
        return self._request("GET", f"/users/{user_id}/summary")
    
    def update_user(self, user_id: int, **kwargs) -> Optional[Dict]:
        return self._request("PUT", f"/users/{user_id}", json=kwargs)
    
    def delete_user(self, user_id: int) -> bool:
        response = self._request("DELETE", f"/users/{user_id}")
        return response is not None

    # Savings Account endpoints
    def create_savings_account(self, **kwargs) -> Optional[Dict]:
        return self._request("POST", "/savings-accounts/", json=kwargs)
    
    def get_savings_accounts(self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> Optional[Dict]:
        params = {"skip": skip, "limit": limit}
        if user_id:
            params["user_id"] = user_id
        return self._request("GET", "/savings-accounts/", params=params)
    
    def get_savings_account(self, account_id: int) -> Optional[Dict]:
        return self._request("GET", f"/savings-accounts/{account_id}")
    
    def update_savings_account(self, account_id: int, **kwargs) -> Optional[Dict]:
        return self._request("PUT", f"/savings-accounts/{account_id}", json=kwargs)
    
    def delete_savings_account(self, account_id: int) -> bool:
        response = self._request("DELETE", f"/savings-accounts/{account_id}")
        return response is not None
    
    def create_transaction(self, **kwargs) -> Optional[Dict]:
        return self._request("POST", "/savings-accounts/transactions", json=kwargs)
    
    def get_transactions(self, account_id: int, skip: int = 0, limit: int = 100) -> Optional[Dict]:
        return self._request("GET", f"/savings-accounts/{account_id}/transactions", params={"skip": skip, "limit": limit})
    
    # Debit Card endpoints
    def create_debit_card(self, **kwargs) -> Optional[Dict]:
        return self._request("POST", "/debit-cards/", json=kwargs)
    
    def get_debit_cards(
        self, 
        user_id: Optional[int] = None, 
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> Optional[Dict]:
        params = {"skip": skip, "limit": limit}
        if user_id is not None:
            params["user_id"] = user_id
        if is_active is not None:
            params["is_active"] = is_active
        return self._request("GET", "/debit-cards/", params=params)
    
    def get_debit_card(self, card_id: int) -> Optional[Dict]:
        return self._request("GET", f"/debit-cards/{card_id}")
    
    def get_debit_card_details(self, card_id: int) -> Optional[Dict]:
        return self._request("GET", f"/debit-cards/{card_id}/details")
    
    def update_debit_card(self, card_id: int, **kwargs) -> Optional[Dict]:
        return self._request("PUT", f"/debit-cards/{card_id}", json=kwargs)
    
    def delete_debit_card(self, card_id: int) -> bool:
        response = self._request("DELETE", f"/debit-cards/{card_id}")
        return response is not None
    
    def activate_debit_card(self, card_id: int) -> Optional[Dict]:
        return self._request("POST", f"/debit-cards/{card_id}/activate")
    
    def deactivate_debit_card(self, card_id: int) -> Optional[Dict]:
        return self._request("POST", f"/debit-cards/{card_id}/deactivate")
    
    # Credit Card endpoints
    def create_credit_card(self, **kwargs) -> Optional[Dict]:
        logger.info(f"Creating credit card for user {kwargs.get('user_id')}")
        return self._request("POST", "/credit-cards/", json=kwargs)
    
    def get_credit_cards(
        self,
        user_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Optional[Dict]:
        params = {"skip": skip, "limit": limit}
        if user_id is not None:
            params["user_id"] = user_id
        if is_active is not None:
            params["is_active"] = is_active
        return self._request("GET", "/credit-cards/", params=params)
    
    def get_credit_card(self, card_id: int) -> Optional[Dict]:
        return self._request("GET", f"/credit-cards/{card_id}")
    
    def update_credit_card(self, card_id: int, **kwargs) -> Optional[Dict]:
        logger.info(f"Updating credit card {card_id}")
        return self._request("PUT", f"/credit-cards/{card_id}", json=kwargs)
    
    def delete_credit_card(self, card_id: int) -> bool:
        logger.warning(f"Deleting credit card {card_id}")
        response = self._request("DELETE", f"/credit-cards/{card_id}")
        return response is not None
    
    def create_credit_transaction(self, **kwargs) -> Optional[Dict]:
        logger.info(f"Creating credit transaction for card {kwargs.get('credit_card_id')}")
        return self._request("POST", "/credit-cards/transactions", json=kwargs)
    
    def get_credit_transactions(self, card_id: int, skip: int = 0, limit: int = 100) -> Optional[Dict]:
        return self._request(
            "GET",
            f"/credit-cards/{card_id}/transactions",
            params={"skip": skip, "limit": limit}
        )
    
    def create_credit_payment(self, **kwargs) -> Optional[Dict]:
        logger.info(f"Processing payment for card {kwargs.get('credit_card_id')}")
        return self._request("POST", "/credit-cards/payments", json=kwargs)
    
    def get_credit_payments(self, card_id: int, skip: int = 0, limit: int = 100) -> Optional[Dict]:
        return self._request(
            "GET",
            f"/credit-cards/{card_id}/payments",
            params={"skip": skip, "limit": limit}
        )
        
    # Expense endpoints
    def create_expense(self, **kwargs) -> Optional[Dict]:
        logger.info(f"Creating expense: {kwargs.get('category')} - ${kwargs.get('amount')}")
        return self._request("POST", "/expenses/", json=kwargs)
    
    def get_expenses(
        self,
        user_id: Optional[int] = None,
        category: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Optional[Dict]:
        params = {"skip": skip, "limit": limit}
        if user_id is not None:
            params["user_id"] = user_id
        if category:
            params["category"] = category
        if payment_method:
            params["payment_method"] = payment_method
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if min_amount is not None:
            params["min_amount"] = min_amount
        if max_amount is not None:
            params["max_amount"] = max_amount
        return self._request("GET", "/expenses/", params=params)
    
    def get_expense(self, expense_id: int) -> Optional[Dict]:
        return self._request("GET", f"/expenses/{expense_id}")
    
    def get_expense_details(self, expense_id: int) -> Optional[Dict]:
        return self._request("GET", f"/expenses/{expense_id}/details")
    
    def update_expense(self, expense_id: int, **kwargs) -> Optional[Dict]:
        logger.info(f"Updating expense {expense_id}")
        return self._request("PUT", f"/expenses/{expense_id}", json=kwargs)
    
    def delete_expense(self, expense_id: int) -> bool:
        logger.warning(f"Deleting expense {expense_id}")
        response = self._request("DELETE", f"/expenses/{expense_id}")
        return response is not None
    
    def get_expense_statistics(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict]:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", f"/expenses/statistics/user/{user_id}", params=params)
    
    def get_monthly_summary(self, user_id: int, year: int, month: int) -> Optional[Dict]:
        return self._request("GET", f"/expenses/summary/user/{user_id}/{year}/{month}")
    
client = APIClient()