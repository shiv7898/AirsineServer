from typing import List, Any
from math import ceil

def paginate(
    query,
    page: int = 1,
    limit: int = 10,
    max_limit: int = 100
):
    """
    Paginate SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (starts from 1)
        limit: Items per page
        max_limit: Maximum items per page allowed
    
    Returns:
        dict with pagination info and data
    """
    # Validation
    if page < 1:
        page = 1
    
    if limit < 1:
        limit = 10
    
    if limit > max_limit:
        limit = max_limit
    
    # Get total count
    total = query.count()
    
    # Calculate total pages
    total_pages = ceil(total / limit) if total > 0 else 0
    
    # Adjust page if it exceeds total pages
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate offset
    offset = (page - 1) * limit
    
    # Get paginated data
    data = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "data": data
    }