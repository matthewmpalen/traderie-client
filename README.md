# Traderie Client

A Python API client for the [Traderie](https://traderie.com/diablo2resurrected) Diablo 2 Resurrected trading platform.

## Installation

Install from GitHub:

```bash
pip install git+https://github.com/matthewmpalen/traderie-client.git
```

Or clone and install locally:

```bash
git clone https://github.com/matthewmpalen/traderie-client.git
cd traderie-client
pip install -e .
```

## Quick Start

```python
from traderie_client import TraderieClient

with TraderieClient() as client:
    # Search for items
    listings = client.get_listings(item_name="Shako", limit=10)

    for listing in listings:
        print(f"{listing.listing_id}: {listing.platform} - {listing.mode}")
```

## Authentication

For authenticated endpoints (managing your listings, offers, etc.), you'll need an auth token from Traderie. You can obtain this by inspecting network requests in your browser's developer tools while logged into traderie.com.

```python
client = TraderieClient(auth_token="your_token_here")
```

## Usage

### Sync Client

```python
from traderie_client import TraderieClient

with TraderieClient(auth_token="your_token") as client:
    # Get listings with filters
    listings = client.get_listings(
        item_name="Ber",
        platform="PC",
        mode="softcore",
        region="Americas",
    )

    # Get your offers
    offers = client.get_offers(seller_id="your_seller_id")

    # Accept an offer
    client.accept_offer(offer_id="123456")

    # Get notifications
    notifications = client.get_notifications(new_only=True)
```

### Async Client

```python
import asyncio
from traderie_client import AsyncTraderieClient

async def main():
    async with AsyncTraderieClient(auth_token="your_token") as client:
        listings = await client.get_listings(item_name="Jah")
        print(f"Found {len(listings)} listings")

asyncio.run(main())
```

## Listing Filters

The API doesn't support server-side filtering by platform/mode/region, but the client provides client-side filtering:

```python
listings = client.get_listings(
    item_name="Shako",
    platform="PC",           # "PC", "playstation", "xbox", "switch"
    mode="softcore",         # "softcore", "hardcore"
    region="Americas",       # "Americas", "Europe", "Asia"
    game_version="reign of the warlock",  # "classic", "lord of destruction", "reign of the warlock"
    ladder=True,             # True, False
)
```

## Listing Properties

Access common properties directly on `Listing` objects:

```python
listing = listings[0]

# Property values
listing.platform       # "PC", "playstation", "xbox", "switch"
listing.mode           # "softcore", "hardcore"
listing.region         # "Americas", "Europe", "Asia"
listing.game_version   # "classic", "lord of destruction", "reign of the warlock"
listing.ladder         # True, False

# Boolean checks
listing.is_pc          # True if PC
listing.is_playstation # True if PlayStation
listing.is_xbox        # True if Xbox
listing.is_switch      # True if Nintendo Switch
listing.is_hardcore    # True if hardcore mode
listing.is_softcore    # True if softcore mode

# Get any property by name
listing.get_property("Rarity")  # "magic", "rare", etc.

# Item properties with formatted names
for prop in listing.properties:
    print(prop.formatted_name())  # "+20 to Life", "+141% Enhanced Defense"
```

## API Methods

### Listings

| Method | Description |
|--------|-------------|
| `get_listings()` | Search/filter item listings |
| `refresh_listings(listing_ids)` | Refresh/relist expired listings |

### Offers

| Method | Description |
|--------|-------------|
| `get_offers()` | Get trade offers |
| `accept_offer(offer_id)` | Accept an offer |
| `deny_offer(offer_id)` | Decline an offer |

### Notifications

| Method | Description |
|--------|-------------|
| `get_notifications()` | Get notifications |
| `mark_notifications_read()` | Mark notifications as read |

### Messages

| Method | Description |
|--------|-------------|
| `get_conversations()` | Get conversations |
| `get_messages(conversation_id)` | Get messages in a conversation |
| `send_message(conversation_id, text)` | Send a message |
| `start_conversation(user_id, text)` | Start a new conversation |

### Users

| Method | Description |
|--------|-------------|
| `get_account()` | Get account information |
| `update_status(status)` | Update user status |
| `search_users(username)` | Search for users |
| `add_review(user_id, rating, text)` | Add a review |
| `block_user(user_id)` | Block a user |

## Data Models

- `Listing` - Marketplace listing with item properties
- `Offer` - Trade offer
- `Notification` - User notification
- `Message` - Chat message
- `Conversation` - Conversation with another user
- `User` - Traderie user
- `ListingProperty` - Item property (stats, attributes)

## Exceptions

```python
from traderie_client import TraderieError, AuthenticationError, RateLimitError

try:
    listings = client.get_listings(item_name="Shako")
except AuthenticationError:
    print("Invalid or expired auth token")
except RateLimitError:
    print("Rate limited - slow down requests")
except TraderieError as e:
    print(f"API error: {e.status_code}")
```

## Project Structure

```
traderie-client/
├── pyproject.toml           # Package configuration
├── README.md
├── example.py               # Usage examples
└── traderie_client/         # Package source
    ├── __init__.py          # Public API exports
    ├── client.py            # TraderieClient (sync)
    ├── async_client.py      # AsyncTraderieClient (async)
    ├── models.py            # Data models
    └── exceptions.py        # Exception classes
```

## Disclaimer

This is an unofficial client based on reverse-engineered API endpoints. Use responsibly and in accordance with Traderie's terms of service.

## License

MIT
