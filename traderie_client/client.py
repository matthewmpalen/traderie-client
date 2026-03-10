"""
Synchronous Traderie API client.
"""

import httpx

from .exceptions import TraderieError, AuthenticationError, RateLimitError
from .models import Listing, Notification, Message, Conversation, Offer, User


class TraderieClient:
    """
    API client for Traderie Diablo 2 Resurrected.

    Usage:
        client = TraderieClient(auth_token="your_token")

        # Get your account info
        account = client.get_account()

        # Search listings
        listings = client.get_listings(item_name="Shako")

        # Get your offers
        offers = client.get_offers(seller_id="your_seller_id")
    """

    BASE_URL = "https://traderie.com/api/diablo2resurrected"

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }

    def __init__(
        self,
        auth_token: str | None = None,
        timeout: float = 30.0,
        base_url: str | None = None,
    ):
        """
        Initialize the Traderie API client.

        Args:
            auth_token: Authorization token for authenticated requests.
            timeout: Request timeout in seconds.
            base_url: Override the base URL (for testing).
        """
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self._auth_token = auth_token

        headers = self.DEFAULT_HEADERS.copy()
        if auth_token:
            headers["Authorization"] = auth_token

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
        )

    def __enter__(self) -> "TraderieClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path.
            params: Query parameters.
            json: JSON body for POST/PUT requests.

        Returns:
            Response JSON as a dictionary.

        Raises:
            TraderieError: On API errors.
            AuthenticationError: On authentication failures.
            RateLimitError: On rate limiting.
        """
        url = f"/{endpoint.lstrip('/')}"

        try:
            response = self._client.request(
                method=method,
                url=url,
                params=params,
                json=json,
            )
        except httpx.TimeoutException as e:
            raise TraderieError(f"Request timed out: {e}")
        except httpx.RequestError as e:
            raise TraderieError(f"Request failed: {e}")

        if response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed",
                status_code=401,
                response=response.json() if response.content else None,
            )
        elif response.status_code == 429:
            raise RateLimitError(
                "Rate limited by API",
                status_code=429,
                response=response.json() if response.content else None,
            )
        elif response.status_code >= 400:
            error_data = response.json() if response.content else None
            raise TraderieError(
                f"API error: {response.status_code}",
                status_code=response.status_code,
                response=error_data,
            )

        if not response.content:
            return {}

        return response.json()

    # Account Methods

    def get_account(self, user_id: str | None = None) -> dict:
        """
        Get account information.

        Args:
            user_id: Optional user ID. If not provided, returns current user.

        Returns:
            Account data dictionary.
        """
        params = {}
        if user_id:
            params["user"] = user_id
        return self._request("GET", "accounts", params=params)

    def update_status(self, status: str) -> dict:
        """
        Update user status.

        Args:
            status: New status string.

        Returns:
            Updated account data.
        """
        return self._request("PUT", "accounts/update", json={"status": status})

    # Notification Methods

    def get_notifications(
        self,
        limit: int = 50,
        new_only: bool = False,
    ) -> list[Notification]:
        """
        Get notifications.

        Args:
            limit: Maximum number of notifications to return.
            new_only: If True, only return unread notifications.

        Returns:
            List of Notification objects.
        """
        params = {"limit": limit}
        if new_only:
            params["new"] = "true"

        data = self._request("GET", "notifications", params=params)
        notifications = data.get("notifications", data) if isinstance(data, dict) else data

        if isinstance(notifications, list):
            return [Notification.from_dict(n) for n in notifications]
        return []

    def mark_notifications_read(self, notification_ids: list[str] | None = None) -> dict:
        """
        Mark notifications as read.

        Args:
            notification_ids: List of notification IDs to mark read.
                            If None, marks all as read.

        Returns:
            Response data.
        """
        json_data = {}
        if notification_ids:
            json_data["notificationIDs"] = notification_ids
        return self._request("PUT", "notifications/read", json=json_data)

    # Listing Methods

    def get_listings(
        self,
        seller_id: str | None = None,
        item_name: str | None = None,
        item_id: str | None = None,
        active: bool = True,
        page: int = 1,
        limit: int = 50,
        # Client-side filters
        platform: str | None = None,
        mode: str | None = None,
        region: str | None = None,
        game_version: str | None = None,
        ladder: bool | None = None,
    ) -> list[Listing]:
        """
        Get item listings.

        Args:
            seller_id: Filter by seller ID.
            item_name: Filter by item name (search).
            item_id: Filter by specific item ID.
            active: If True, only return active listings.
            page: Page number for pagination.
            limit: Number of results per page.
            platform: Client-side filter: "PC", "playstation", "xbox", "switch".
            mode: Client-side filter: "softcore" or "hardcore".
            region: Client-side filter: "Americas", "Europe", "Asia".
            game_version: Client-side filter: "classic", "lord of destruction",
                         "reign of the warlock".
            ladder: Client-side filter: True for ladder, False for non-ladder.

        Returns:
            List of Listing objects.
        """
        params = {
            "page": page,
            "limit": limit,
            "active": "true" if active else "false",
        }
        if seller_id:
            params["seller"] = seller_id
        if item_name:
            params["itemName"] = item_name
        if item_id:
            params["itemID"] = item_id

        data = self._request("GET", "listings", params=params)
        listings = data.get("listings", data) if isinstance(data, dict) else data

        if not isinstance(listings, list):
            return []

        result = [Listing.from_dict(l) for l in listings]

        # Apply client-side filters
        if platform is not None:
            result = [l for l in result if l.platform == platform]
        if mode is not None:
            result = [l for l in result if l.mode == mode]
        if region is not None:
            result = [l for l in result if l.region == region]
        if game_version is not None:
            result = [l for l in result if l.game_version == game_version]
        if ladder is not None:
            result = [l for l in result if l.ladder == ladder]

        return result

    def refresh_listings(self, listing_ids: list[str]) -> dict:
        """
        Refresh/relist expired or expiring listings.

        Args:
            listing_ids: List of listing IDs to refresh.

        Returns:
            Response data.
        """
        return self._request("PUT", "listings/refresh", json={"listingIDs": listing_ids})

    # Offer Methods

    def get_offers(
        self,
        seller_id: str | None = None,
        buyer_id: str | None = None,
        completed: bool | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> list[Offer]:
        """
        Get trade offers.

        Args:
            seller_id: Filter by seller ID.
            buyer_id: Filter by buyer ID.
            completed: Filter by completion status.
            page: Page number for pagination.
            limit: Number of results per page.

        Returns:
            List of Offer objects.
        """
        params = {"page": page, "limit": limit}
        if seller_id:
            params["seller"] = seller_id
        if buyer_id:
            params["buyer"] = buyer_id
        if completed is not None:
            params["completed"] = "true" if completed else "false"

        data = self._request("GET", "offers", params=params)
        offers = data.get("offers", data) if isinstance(data, dict) else data

        if isinstance(offers, list):
            return [Offer.from_dict(o) for o in offers]
        return []

    def accept_offer(self, offer_id: str) -> dict:
        """
        Accept a trade offer.

        Args:
            offer_id: The offer ID to accept.

        Returns:
            Response data.
        """
        return self._request("PUT", "offers/accept", json={"offerID": offer_id})

    def deny_offer(self, offer_id: str) -> dict:
        """
        Deny/decline a trade offer.

        Args:
            offer_id: The offer ID to deny.

        Returns:
            Response data.
        """
        return self._request("PUT", "offers/deny", json={"offerID": offer_id})

    # Conversation/Message Methods

    def get_conversations(
        self,
        page: int = 1,
        limit: int = 50,
    ) -> list[Conversation]:
        """
        Get conversations.

        Args:
            page: Page number for pagination.
            limit: Number of results per page.

        Returns:
            List of Conversation objects.
        """
        params = {"page": page, "limit": limit}
        data = self._request("GET", "conversations", params=params)
        convos = data.get("conversations", data) if isinstance(data, dict) else data

        if isinstance(convos, list):
            return [Conversation.from_dict(c) for c in convos]
        return []

    def get_messages(
        self,
        conversation_id: str,
        page: int = 1,
        limit: int = 50,
    ) -> list[Message]:
        """
        Get messages from a conversation.

        Args:
            conversation_id: The conversation ID.
            page: Page number for pagination.
            limit: Number of results per page.

        Returns:
            List of Message objects.
        """
        params = {
            "convoId": conversation_id,
            "page": page,
            "limit": limit,
        }
        data = self._request("GET", "messages", params=params)
        messages = data.get("messages", data) if isinstance(data, dict) else data

        if isinstance(messages, list):
            return [Message.from_dict(m) for m in messages]
        return []

    def send_message(self, conversation_id: str, text: str) -> dict:
        """
        Send a message in a conversation.

        Args:
            conversation_id: The conversation ID.
            text: Message text to send.

        Returns:
            Response data.
        """
        return self._request(
            "POST",
            "messages",
            json={"convoId": conversation_id, "text": text},
        )

    def start_conversation(self, user_id: str, text: str) -> dict:
        """
        Start a new conversation with a user.

        Args:
            user_id: The user ID to message.
            text: Initial message text.

        Returns:
            Response data including conversation ID.
        """
        return self._request(
            "POST",
            "conversations",
            json={"userID": user_id, "text": text},
        )

    # User Methods

    def search_users(self, username: str, limit: int = 20) -> list[User]:
        """
        Search for users by username.

        Args:
            username: Username to search for.
            limit: Maximum number of results.

        Returns:
            List of User objects.
        """
        params = {"username": username, "limit": limit}
        data = self._request("GET", "users", params=params)
        users = data.get("users", data) if isinstance(data, dict) else data

        if isinstance(users, list):
            return [User.from_dict(u) for u in users]
        return []

    # Review Methods

    def add_review(
        self,
        user_id: str,
        rating: int,
        text: str,
        offer_id: str | None = None,
    ) -> dict:
        """
        Add a review for a user.

        Args:
            user_id: The user ID to review.
            rating: Rating (typically 1-5).
            text: Review text.
            offer_id: Optional associated offer ID.

        Returns:
            Response data.
        """
        json_data = {
            "userID": user_id,
            "rating": rating,
            "text": text,
        }
        if offer_id:
            json_data["offerID"] = offer_id
        return self._request("POST", "reviews/add", json=json_data)

    # Block Methods

    def block_user(self, user_id: str) -> dict:
        """
        Block a user.

        Args:
            user_id: The user ID to block.

        Returns:
            Response data.
        """
        return self._request("POST", "blocks", json={"userID": user_id})
