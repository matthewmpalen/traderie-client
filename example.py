"""
Example usage of the Traderie API client.

Note: You'll need an auth token from Traderie to use authenticated endpoints.
You can obtain this by inspecting network requests in your browser when
logged into traderie.com.
"""

import asyncio
from traderie_client import (
    TraderieClient,
    AsyncTraderieClient,
    TraderieError,
    AuthenticationError,
)


def sync_example():
    """Synchronous client example."""
    # For authenticated requests, pass your auth token
    # client = TraderieClient(auth_token="your_token_here")

    # For unauthenticated/public endpoints
    with TraderieClient() as client:
        try:
            # Search for listings (may require auth)
            listings = client.get_listings(item_name="Shako", limit=10)
            print(f"Found {len(listings)} Shako listings")

            for listing in listings[:3]:
                print(f"  - Listing {listing.listing_id} (seller: {listing.seller_id})")
                for prop in listing.properties[:3]:
                    print(f"      {prop.formatted_name()}")

        except AuthenticationError:
            print("Authentication required for this endpoint")
        except TraderieError as e:
            print(f"API error: {e}")


async def async_example():
    """Asynchronous client example."""
    async with AsyncTraderieClient() as client:
        try:
            # Fetch listings asynchronously
            listings = await client.get_listings(item_name="Ber Rune", limit=5)
            print(f"Found {len(listings)} Ber Rune listings")

        except TraderieError as e:
            print(f"API error: {e}")


def authenticated_example(auth_token: str, seller_id: str):
    """Example with authentication."""
    with TraderieClient(auth_token=auth_token) as client:
        # Get your account info
        account = client.get_account()
        print(f"Account: {account}")

        # Get your notifications
        notifications = client.get_notifications(new_only=True)
        print(f"You have {len(notifications)} new notifications")

        # Get offers for your listings
        offers = client.get_offers(seller_id=seller_id, completed=False)
        print(f"You have {len(offers)} pending offers")

        for offer in offers:
            print(f"  - {offer.buyer_username} offered for {offer.item_name}")

        # Accept an offer
        # client.accept_offer(offer_id="...")

        # Refresh your listings
        # my_listings = client.get_listings(seller_id=seller_id)
        # listing_ids = [l.listing_id for l in my_listings]
        # client.refresh_listings(listing_ids)


if __name__ == "__main__":
    print("=== Sync Example ===")
    sync_example()

    print("\n=== Async Example ===")
    asyncio.run(async_example())

    # Uncomment with your credentials to test authenticated endpoints
    # print("\n=== Authenticated Example ===")
    # authenticated_example(
    #     auth_token="your_auth_token",
    #     seller_id="your_seller_id"
    # )
