"""
Context Marketplace — Shared knowledge graphs.

Allows sharing and discovering knowledge graphs, plugins, and integrations.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class ListingType(str, Enum):
    KNOWLEDGE_GRAPH = "knowledge_graph"
    PLUGIN = "plugin"
    INTEGRATION = "integration"
    TEMPLATE = "template"


class ListingStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class MarketplaceListing:
    """A marketplace listing."""
    id: str
    title: str
    description: str
    listing_type: ListingType
    author_user_id: str
    author_name: str
    status: ListingStatus
    review_status: ReviewStatus
    version: str
    tags: list[str] = field(default_factory=list)
    downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    price: float = 0.0  # 0 = free
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class MarketplaceReview:
    """A listing review."""
    id: str
    listing_id: str
    user_id: str
    user_name: str
    rating: int  # 1-5
    title: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MarketplaceConfig:
    """Marketplace configuration."""
    enabled: bool = True
    require_review: bool = True
    max_free_downloads: int = 1000
    commission_rate: float = 0.1  # 10% commission on paid listings
    max_listings_per_user: int = 50


class MarketplaceService:
    """Context Marketplace service."""

    def __init__(self, config: Optional[MarketplaceConfig] = None):
        self.config = config or MarketplaceConfig()
        self._listings: dict[str, MarketplaceListing] = {}
        self._reviews: dict[str, list[MarketplaceReview]] = {}

    async def create_listing(
        self,
        title: str,
        description: str,
        listing_type: ListingType,
        author_user_id: str,
        author_name: str,
        version: str = "1.0.0",
        tags: Optional[list[str]] = None,
        price: float = 0.0,
        metadata: Optional[dict] = None,
    ) -> MarketplaceListing:
        """
        Create a new marketplace listing.

        Args:
            title: Listing title
            description: Listing description
            listing_type: Type of listing
            author_user_id: Author user ID
            author_name: Author display name
            version: Version string
            tags: Optional tags
            price: Price (0 = free)
            metadata: Optional metadata

        Returns:
            Created MarketplaceListing
        """
        listing_id = str(uuid4())
        status = ListingStatus.DRAFT
        review_status = ReviewStatus.PENDING if self.config.require_review else ReviewStatus.APPROVED

        listing = MarketplaceListing(
            id=listing_id,
            title=title,
            description=description,
            listing_type=listing_type,
            author_user_id=author_user_id,
            author_name=author_name,
            status=status,
            review_status=review_status,
            version=version,
            tags=tags or [],
            price=price,
            metadata=metadata or {},
        )

        self._listings[listing_id] = listing
        self._reviews[listing_id] = []

        logger.info(f"Created listing: {title} by {author_name}")
        return listing

    async def get_listing(self, listing_id: str) -> Optional[MarketplaceListing]:
        """Get listing by ID."""
        return self._listings.get(listing_id)

    async def update_listing(
        self,
        listing_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[list[str]] = None,
        price: Optional[float] = None,
    ) -> Optional[MarketplaceListing]:
        """Update a listing."""
        listing = self._listings.get(listing_id)
        if not listing:
            return None

        if title:
            listing.title = title
        if description:
            listing.description = description
        if version:
            listing.version = version
        if tags is not None:
            listing.tags = tags
        if price is not None:
            listing.price = price

        listing.updated_at = datetime.utcnow()
        return listing

    async def publish_listing(self, listing_id: str) -> bool:
        """Publish a listing."""
        listing = self._listings.get(listing_id)
        if not listing:
            return False

        if listing.review_status != ReviewStatus.APPROVED and self.config.require_review:
            return False

        listing.status = ListingStatus.PUBLISHED
        listing.published_at = datetime.utcnow()
        return True

    async def archive_listing(self, listing_id: str) -> bool:
        """Archive a listing."""
        listing = self._listings.get(listing_id)
        if not listing:
            return False

        listing.status = ListingStatus.ARCHIVED
        return True

    async def delete_listing(self, listing_id: str) -> bool:
        """Delete a listing."""
        if listing_id in self._listings:
            del self._listings[listing_id]
            self._reviews.pop(listing_id, None)
            return True
        return False

    async def add_review(
        self,
        listing_id: str,
        user_id: str,
        user_name: str,
        rating: int,
        title: str,
        content: str,
    ) -> Optional[MarketplaceReview]:
        """
        Add a review to a listing.

        Args:
            listing_id: Listing to review
            user_id: Reviewer user ID
            user_name: Reviewer display name
            rating: Rating 1-5
            title: Review title
            content: Review content

        Returns:
            Created MarketplaceReview or None
        """
        if rating < 1 or rating > 5:
            return None

        listing = self._listings.get(listing_id)
        if not listing:
            return None

        review = MarketplaceReview(
            id=str(uuid4()),
            listing_id=listing_id,
            user_id=user_id,
            user_name=user_name,
            rating=rating,
            title=title,
            content=content,
        )

        if listing_id not in self._reviews:
            self._reviews[listing_id] = []
        self._reviews[listing_id].append(review)

        # Update listing rating
        reviews = self._reviews[listing_id]
        listing.rating = sum(r.rating for r in reviews) / len(reviews)
        listing.rating_count = len(reviews)

        return review

    async def get_reviews(
        self,
        listing_id: str,
        limit: int = 50,
    ) -> list[MarketplaceReview]:
        """Get reviews for a listing."""
        return self._reviews.get(listing_id, [])[:limit]

    async def record_download(self, listing_id: str) -> bool:
        """Record a download."""
        listing = self._listings.get(listing_id)
        if not listing:
            return False

        listing.downloads += 1
        return True

    async def list_listings(
        self,
        listing_type: Optional[ListingType] = None,
        status: Optional[ListingStatus] = None,
        tags: Optional[list[str]] = None,
        author_user_id: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "downloads",  # downloads, rating, created_at
        limit: int = 50,
        offset: int = 0,
    ) -> list[MarketplaceListing]:
        """
        List marketplace listings with filters.

        Args:
            listing_type: Filter by type
            status: Filter by status
            tags: Filter by tags
            author_user_id: Filter by author
            search: Search in title/description
            sort_by: Sort field
            limit: Max results
            offset: Pagination offset

        Returns:
            List of MarketplaceListing
        """
        listings = list(self._listings.values())

        if listing_type:
            listings = [l for l in listings if l.listing_type == listing_type]
        if status:
            listings = [l for l in listings if l.status == status]
        if tags:
            listings = [l for l in listings if any(t in l.tags for t in tags)]
        if author_user_id:
            listings = [l for l in listings if l.author_user_id == author_user_id]
        if search:
            search_lower = search.lower()
            listings = [
                l for l in listings
                if search_lower in l.title.lower()
                or search_lower in l.description.lower()
            ]

        # Sort
        if sort_by == "downloads":
            listings.sort(key=lambda l: l.downloads, reverse=True)
        elif sort_by == "rating":
            listings.sort(key=lambda l: l.rating, reverse=True)
        elif sort_by == "created_at":
            listings.sort(key=lambda l: l.created_at, reverse=True)

        return listings[offset:offset + limit]

    async def get_featured_listings(
        self,
        limit: int = 10,
    ) -> list[MarketplaceListing]:
        """Get featured/top listings."""
        return await self.list_listings(
            status=ListingStatus.PUBLISHED,
            sort_by="downloads",
            limit=limit,
        )

    async def get_marketplace_stats(self) -> dict:
        """Get marketplace statistics."""
        listings = list(self._listings.values())
        published = [l for l in listings if l.status == ListingStatus.PUBLISHED]

        return {
            "total_listings": len(listings),
            "published": len(published),
            "total_downloads": sum(l.downloads for l in listings),
            "by_type": {
                lt.value: len([l for l in listings if l.listing_type == lt])
                for lt in ListingType
            },
            "avg_rating": sum(l.rating for l in published) / len(published) if published else 0,
        }
