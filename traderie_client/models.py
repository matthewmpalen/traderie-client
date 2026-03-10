"""
Data models for the Traderie API.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OfferStatus(Enum):
    """Status of a trade offer."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DENIED = "denied"
    COMPLETED = "completed"


@dataclass
class ListingProperty:
    """A property/attribute of a listed item."""
    id: str
    name: str
    value: str | int | None

    def formatted_name(self) -> str:
        """Return the property name with value substituted."""
        if self.value is not None and "{{value}}" in self.name:
            return self.name.replace("{{value}}", str(self.value))
        return self.name


@dataclass
class Listing:
    """A marketplace listing."""
    listing_id: str
    updated_at: str | None = None
    prices: list[dict[str, Any]] | None = None
    properties: list[ListingProperty] = field(default_factory=list)
    item_id: str | None = None
    seller_id: str | None = None
    amount: int = 1
    active: bool = True
    selling: bool = True
    make_offer: bool = False
    total_offers: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Listing":
        properties = []
        raw_props = data.get("properties", [])
        if isinstance(raw_props, list):
            for prop in raw_props:
                if isinstance(prop, dict):
                    # Get the value from either number or string field
                    value = prop.get("number") or prop.get("string") or prop.get("value")
                    properties.append(ListingProperty(
                        id=str(prop.get("id", "")),
                        name=prop.get("property", prop.get("name", "")),
                        value=value,
                    ))
        elif isinstance(raw_props, dict):
            for key, prop in raw_props.items():
                if isinstance(prop, dict):
                    properties.append(ListingProperty(
                        id=str(prop.get("id", "")),
                        name=prop.get("property", prop.get("name", key)),
                        value=prop.get("number") or prop.get("string") or prop.get("value"),
                    ))

        # Handle total_offers which can be string or int
        total_offers = data.get("total_offers", 0)
        if isinstance(total_offers, str):
            total_offers = int(total_offers) if total_offers.isdigit() else 0

        return cls(
            listing_id=str(data.get("id", data.get("listingID", data.get("_id", "")))),
            updated_at=data.get("updated_at", data.get("updated")),
            prices=data.get("prices", data.get("price")),
            properties=properties,
            item_id=str(data.get("item_id", data.get("itemID", ""))) or None,
            seller_id=str(data.get("seller_id", data.get("sellerID", ""))) or None,
            amount=data.get("amount", 1),
            active=data.get("active", True),
            selling=data.get("selling", True),
            make_offer=data.get("make_offer", False),
            total_offers=total_offers,
        )

    def get_property(self, name: str) -> str | int | bool | None:
        """
        Get a property value by name.

        Args:
            name: The property name (e.g., "Platform", "Mode", "Region").

        Returns:
            The property value, or None if not found.
        """
        for prop in self.properties:
            if prop.name == name:
                return prop.value
        return None

    @property
    def platform(self) -> str | None:
        """Platform: 'PC', 'playstation', 'switch', or 'xbox'."""
        value = self.get_property("Platform")
        return str(value) if value is not None else None

    @property
    def mode(self) -> str | None:
        """Game mode: 'softcore' or 'hardcore'."""
        value = self.get_property("Mode")
        return str(value) if value is not None else None

    @property
    def region(self) -> str | None:
        """Region: 'Americas', 'Europe', or 'Asia'."""
        value = self.get_property("Region")
        return str(value) if value is not None else None

    @property
    def game_version(self) -> str | None:
        """Game version: 'classic', 'lord of destruction', or 'reign of the warlock'."""
        value = self.get_property("Game version")
        return str(value) if value is not None else None

    @property
    def ladder(self) -> bool | None:
        """Whether this is a ladder item."""
        value = self.get_property("Ladder")
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "ladder")

    @property
    def is_pc(self) -> bool:
        """Check if this listing is for PC."""
        return self.platform == "PC"

    @property
    def is_playstation(self) -> bool:
        """Check if this listing is for PlayStation."""
        return self.platform == "playstation"

    @property
    def is_xbox(self) -> bool:
        """Check if this listing is for Xbox."""
        return self.platform == "xbox"

    @property
    def is_switch(self) -> bool:
        """Check if this listing is for Nintendo Switch."""
        return self.platform == "switch"

    @property
    def is_hardcore(self) -> bool:
        """Check if this is a hardcore listing."""
        return self.mode == "hardcore"

    @property
    def is_softcore(self) -> bool:
        """Check if this is a softcore listing."""
        return self.mode == "softcore"


@dataclass
class Notification:
    """A notification from Traderie."""
    notification_id: str
    text: str
    date: int
    from_user_id: str | None = None
    listing_id: str | None = None
    read: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        return cls(
            notification_id=data.get("notificationID", data.get("_id", "")),
            text=data.get("text", ""),
            date=data.get("date", 0),
            from_user_id=data.get("fromUserID"),
            listing_id=data.get("listingID"),
            read=data.get("read", False),
        )


@dataclass
class Message:
    """A chat message."""
    msg_id: str
    text: str
    from_id: str
    to_id: str
    timestamp: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            msg_id=data.get("msgID", data.get("_id", "")),
            text=data.get("text", ""),
            from_id=data.get("fromID", ""),
            to_id=data.get("toID", ""),
            timestamp=data.get("timestamp", 0),
        )


@dataclass
class Conversation:
    """A conversation with another user."""
    conversation_id: str
    user_id: str
    username: str | None = None
    last_message: str | None = None
    unread: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        return cls(
            conversation_id=data.get("conversationID", data.get("_id", "")),
            user_id=data.get("userID", ""),
            username=data.get("username"),
            last_message=data.get("lastMessage"),
            unread=data.get("unread", 0),
        )


@dataclass
class Offer:
    """A trade offer."""
    offer_id: str
    listing_id: str
    item_name: str
    item_id: str
    seller_id: str
    seller_username: str
    buyer_id: str
    buyer_username: str
    offer_items: list[dict[str, Any]]
    amount: int
    status: str = "pending"

    @classmethod
    def from_dict(cls, data: dict) -> "Offer":
        return cls(
            offer_id=data.get("offerID", data.get("_id", "")),
            listing_id=data.get("listingID", ""),
            item_name=data.get("itemName", ""),
            item_id=data.get("itemID", ""),
            seller_id=data.get("sellerID", ""),
            seller_username=data.get("sellerUsername", ""),
            buyer_id=data.get("buyerID", ""),
            buyer_username=data.get("buyerUsername", ""),
            offer_items=data.get("offer", []),
            amount=data.get("amount", 1),
            status=data.get("status", "pending"),
        )


@dataclass
class User:
    """A Traderie user."""
    user_id: str
    username: str
    status: str | None = None
    rating: float | None = None
    review_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            user_id=data.get("userID", data.get("_id", "")),
            username=data.get("username", ""),
            status=data.get("status"),
            rating=data.get("rating"),
            review_count=data.get("reviewCount", 0),
        )
