"""
API Payment System for Repository Scanning Data

This module provides a paid API for scrapers and developers who want
to access the repository analysis data programmatically.

Pricing Tiers:
- Free: 100 requests/day, basic data
- Pro ($9/month): 1,000 requests/day, full data + insights
- Enterprise ($49/month): 10,000 requests/day, full data + bulk exports + webhooks

Integration: Lemon Squeezy for payment processing
"""

import os
import time
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, g
from redis import Redis

# Configure logging
logger = logging.getLogger("APIPayments")

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Redis connection for rate limiting and API key storage
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_conn = Redis.from_url(redis_url)
    redis_conn.ping()
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    redis_conn = None

# Lemon Squeezy configuration
LEMONSQUEEZY_API_KEY = os.getenv("LEMONSQUEEZY_API_KEY", "")
LEMONSQUEEZY_STORE_ID = os.getenv("LEMONSQUEEZY_STORE_ID", "")
LEMONSQUEEZY_WEBHOOK_SECRET = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "")

# Pricing tiers configuration
PRICING_TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "requests_per_day": 100,
        "rate_limit_per_minute": 10,
        "features": ["basic_data", "public_repos"],
        "variant_id": None  # Free tier, no payment
    },
    "pro": {
        "name": "Pro",
        "price": 9,
        "requests_per_day": 1000,
        "rate_limit_per_minute": 60,
        "features": ["basic_data", "public_repos", "insights", "ai_analysis", "historical_data"],
        "variant_id": os.getenv("LEMONSQUEEZY_PRO_VARIANT_ID", "")
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 49,
        "requests_per_day": 10000,
        "rate_limit_per_minute": 300,
        "features": ["basic_data", "public_repos", "insights", "ai_analysis", "historical_data", 
                     "bulk_export", "webhooks", "priority_support"],
        "variant_id": os.getenv("LEMONSQUEEZY_ENTERPRISE_VARIANT_ID", "")
    }
}


def generate_api_key():
    """Generate a secure API key."""
    return f"bos_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key):
    """Hash an API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_api_key_data(api_key):
    """Retrieve API key data from Redis."""
    if not redis_conn:
        return None
    
    key_hash = hash_api_key(api_key)
    data = redis_conn.hgetall(f"api_key:{key_hash}")
    
    if not data:
        return None
    
    return {k.decode(): v.decode() for k, v in data.items()}


def save_api_key(api_key, email, tier="free", subscription_id=None):
    """Save API key to Redis."""
    if not redis_conn:
        logger.error("Redis not available, cannot save API key")
        return False
    
    key_hash = hash_api_key(api_key)
    data = {
        "email": email,
        "tier": tier,
        "created_at": datetime.utcnow().isoformat(),
        "subscription_id": subscription_id or "",
        "active": "true"
    }
    
    redis_conn.hset(f"api_key:{key_hash}", mapping=data)
    redis_conn.sadd(f"user_keys:{email}", key_hash)
    
    return True


def check_rate_limit(api_key, tier):
    """Check if the request is within rate limits."""
    if not redis_conn:
        return True, 0, 0
    
    tier_config = PRICING_TIERS.get(tier, PRICING_TIERS["free"])
    key_hash = hash_api_key(api_key)
    
    # Check minute rate limit
    minute_key = f"rate:{key_hash}:minute:{int(time.time() // 60)}"
    minute_count = redis_conn.incr(minute_key)
    redis_conn.expire(minute_key, 60)
    
    if minute_count > tier_config["rate_limit_per_minute"]:
        return False, minute_count, tier_config["rate_limit_per_minute"]
    
    # Check daily limit
    day_key = f"rate:{key_hash}:day:{datetime.utcnow().strftime('%Y-%m-%d')}"
    day_count = redis_conn.incr(day_key)
    redis_conn.expire(day_key, 86400)
    
    if day_count > tier_config["requests_per_day"]:
        return False, day_count, tier_config["requests_per_day"]
    
    return True, day_count, tier_config["requests_per_day"]


def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
        
        if not api_key:
            return jsonify({
                "error": "API key required",
                "message": "Please provide an API key via X-API-Key header or api_key parameter",
                "docs": "https://bestof-opensource.dev/api/docs"
            }), 401
        
        # Validate API key
        key_data = get_api_key_data(api_key)
        if not key_data or key_data.get("active") != "true":
            return jsonify({
                "error": "Invalid API key",
                "message": "The provided API key is invalid or has been revoked"
            }), 401
        
        # Check rate limits
        tier = key_data.get("tier", "free")
        allowed, current, limit = check_rate_limit(api_key, tier)
        
        # Add rate limit headers
        g.rate_limit_remaining = max(0, limit - current)
        g.rate_limit_limit = limit
        
        if not allowed:
            return jsonify({
                "error": "Rate limit exceeded",
                "message": f"You have exceeded your rate limit. Current: {current}, Limit: {limit}",
                "upgrade_url": "https://bestof-opensource.dev/api/pricing"
            }), 429
        
        g.api_key = api_key
        g.api_tier = tier
        g.api_features = PRICING_TIERS[tier]["features"]
        
        return f(*args, **kwargs)
    
    return decorated_function


def add_rate_limit_headers(response):
    """Add rate limit headers to response."""
    if hasattr(g, 'rate_limit_remaining'):
        response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_remaining)
        response.headers['X-RateLimit-Limit'] = str(g.rate_limit_limit)
    return response


# ============================================================
# API Endpoints
# ============================================================

@api_bp.route('/repos', methods=['GET'])
@require_api_key
def list_repos():
    """
    List all scanned repositories.
    
    Query Parameters:
        - page (int): Page number (default: 1)
        - per_page (int): Results per page (default: 20, max: 100)
        - language (str): Filter by programming language
        - min_score (int): Minimum score filter
        - category (str): Filter by category
        - sort (str): Sort by field (stars, score, updated)
        - order (str): Sort order (asc, desc)
    """
    import json
    from pathlib import Path
    
    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    language = request.args.get('language')
    min_score = request.args.get('min_score', type=int)
    category = request.args.get('category')
    sort_by = request.args.get('sort', 'score')
    order = request.args.get('order', 'desc')
    
    # Load repository data
    output_dir = Path(__file__).parent.parent / "output"
    repos = []
    
    # Load from ai_scan.json (main scan results)
    ai_scan_path = output_dir / "ai_scan.json"
    if ai_scan_path.exists():
        try:
            with open(ai_scan_path) as f:
                data = json.load(f)
                if isinstance(data, list):
                    repos.extend(data)
                elif isinstance(data, dict) and "repos" in data:
                    repos.extend(data["repos"])
        except Exception as e:
            logger.error(f"Error loading ai_scan.json: {e}")
    
    # Apply filters
    if language:
        repos = [r for r in repos if r.get("language", "").lower() == language.lower()]
    
    if min_score:
        repos = [r for r in repos if r.get("score", 0) >= min_score]
    
    if category:
        repos = [r for r in repos if category.lower() in [c.lower() for c in r.get("categories", [])]]
    
    # Sort
    reverse = order.lower() == 'desc'
    if sort_by == 'stars':
        repos.sort(key=lambda x: x.get("stargazers_count", 0), reverse=reverse)
    elif sort_by == 'updated':
        repos.sort(key=lambda x: x.get("updated_at", ""), reverse=reverse)
    else:
        repos.sort(key=lambda x: x.get("score", 0), reverse=reverse)
    
    # Paginate
    total = len(repos)
    start = (page - 1) * per_page
    end = start + per_page
    repos_page = repos[start:end]
    
    # Filter data based on tier
    if "insights" not in g.api_features:
        # Remove insights for free tier
        for repo in repos_page:
            repo.pop("insights", None)
            repo.pop("ai_analysis", None)
    
    return jsonify({
        "data": repos_page,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    })


@api_bp.route('/repos/<path:repo_name>', methods=['GET'])
@require_api_key
def get_repo(repo_name):
    """
    Get detailed information about a specific repository.
    
    Path Parameters:
        - repo_name: Full repository name (owner/repo)
    """
    import json
    from pathlib import Path
    
    output_dir = Path(__file__).parent.parent / "output"
    
    # Search for the repository
    ai_scan_path = output_dir / "ai_scan.json"
    if ai_scan_path.exists():
        try:
            with open(ai_scan_path) as f:
                data = json.load(f)
                repos = data if isinstance(data, list) else data.get("repos", [])
                
                for repo in repos:
                    if repo.get("full_name", "").lower() == repo_name.lower():
                        # Filter based on tier
                        if "insights" not in g.api_features:
                            repo.pop("insights", None)
                            repo.pop("ai_analysis", None)
                        
                        return jsonify({"data": repo})
        except Exception as e:
            logger.error(f"Error searching for repo: {e}")
    
    return jsonify({
        "error": "Repository not found",
        "message": f"No data found for repository: {repo_name}"
    }), 404


@api_bp.route('/search', methods=['GET'])
@require_api_key
def search_repos():
    """
    Search repositories by keyword.
    
    Query Parameters:
        - q (str): Search query (searches name, description, topics)
        - page (int): Page number
        - per_page (int): Results per page
    """
    import json
    from pathlib import Path
    
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({
            "error": "Missing query",
            "message": "Please provide a search query via the 'q' parameter"
        }), 400
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    output_dir = Path(__file__).parent.parent / "output"
    repos = []
    
    ai_scan_path = output_dir / "ai_scan.json"
    if ai_scan_path.exists():
        try:
            with open(ai_scan_path) as f:
                data = json.load(f)
                all_repos = data if isinstance(data, list) else data.get("repos", [])
                
                for repo in all_repos:
                    searchable = " ".join([
                        repo.get("name", ""),
                        repo.get("full_name", ""),
                        repo.get("description", "") or "",
                        " ".join(repo.get("topics", []))
                    ]).lower()
                    
                    if query in searchable:
                        repos.append(repo)
        except Exception as e:
            logger.error(f"Error searching repos: {e}")
    
    # Sort by relevance (simple scoring)
    def relevance_score(repo):
        score = 0
        name = repo.get("name", "").lower()
        if query == name:
            score += 100
        elif query in name:
            score += 50
        if query in repo.get("description", "").lower():
            score += 20
        score += repo.get("score", 0) / 10
        return score
    
    repos.sort(key=relevance_score, reverse=True)
    
    # Paginate
    total = len(repos)
    start = (page - 1) * per_page
    repos_page = repos[start:start + per_page]
    
    # Filter based on tier
    if "insights" not in g.api_features:
        for repo in repos_page:
            repo.pop("insights", None)
            repo.pop("ai_analysis", None)
    
    return jsonify({
        "data": repos_page,
        "meta": {
            "query": query,
            "total": total,
            "page": page,
            "per_page": per_page
        }
    })


@api_bp.route('/stats', methods=['GET'])
@require_api_key
def get_stats():
    """Get overall statistics about scanned repositories."""
    import json
    from pathlib import Path
    from collections import Counter
    
    output_dir = Path(__file__).parent.parent / "output"
    
    stats = {
        "total_repos": 0,
        "languages": {},
        "categories": {},
        "average_score": 0,
        "last_updated": None
    }
    
    ai_scan_path = output_dir / "ai_scan.json"
    if ai_scan_path.exists():
        try:
            with open(ai_scan_path) as f:
                data = json.load(f)
                repos = data if isinstance(data, list) else data.get("repos", [])
                
                stats["total_repos"] = len(repos)
                
                languages = Counter()
                categories = Counter()
                total_score = 0
                
                for repo in repos:
                    if repo.get("language"):
                        languages[repo["language"]] += 1
                    for cat in repo.get("categories", []):
                        categories[cat] += 1
                    total_score += repo.get("score", 0)
                
                stats["languages"] = dict(languages.most_common(20))
                stats["categories"] = dict(categories.most_common(20))
                stats["average_score"] = round(total_score / max(1, len(repos)), 2)
                stats["last_updated"] = datetime.utcnow().isoformat()
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
    
    return jsonify({"data": stats})


@api_bp.route('/export', methods=['GET'])
@require_api_key
def export_data():
    """
    Export all repository data (Enterprise only).
    
    Query Parameters:
        - format (str): Export format (json, csv)
    """
    if "bulk_export" not in g.api_features:
        return jsonify({
            "error": "Feature not available",
            "message": "Bulk export is only available for Enterprise tier",
            "upgrade_url": "https://bestof-opensource.dev/api/pricing"
        }), 403
    
    import json
    from pathlib import Path
    
    export_format = request.args.get('format', 'json')
    output_dir = Path(__file__).parent.parent / "output"
    
    ai_scan_path = output_dir / "ai_scan.json"
    if ai_scan_path.exists():
        with open(ai_scan_path) as f:
            data = json.load(f)
            repos = data if isinstance(data, list) else data.get("repos", [])
            
            if export_format == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                if repos:
                    writer = csv.DictWriter(output, fieldnames=repos[0].keys())
                    writer.writeheader()
                    writer.writerows(repos)
                
                return output.getvalue(), 200, {
                    'Content-Type': 'text/csv',
                    'Content-Disposition': 'attachment; filename=repos_export.csv'
                }
            
            return jsonify({"data": repos})
    
    return jsonify({"data": []})


# ============================================================
# API Key Management Endpoints
# ============================================================

@api_bp.route('/keys', methods=['POST'])
def create_api_key():
    """
    Create a new API key (Free tier).
    
    Request Body:
        - email (str): User email address
    """
    data = request.get_json()
    
    if not data or not data.get("email"):
        return jsonify({
            "error": "Email required",
            "message": "Please provide an email address"
        }), 400
    
    email = data["email"]
    
    # Check if user already has a key
    if redis_conn:
        existing_keys = redis_conn.smembers(f"user_keys:{email}")
        if len(existing_keys) >= 3:
            return jsonify({
                "error": "Key limit reached",
                "message": "You have reached the maximum number of API keys (3)"
            }), 400
    
    # Generate new key
    api_key = generate_api_key()
    save_api_key(api_key, email, tier="free")
    
    return jsonify({
        "message": "API key created successfully",
        "api_key": api_key,
        "tier": "free",
        "limits": PRICING_TIERS["free"],
        "important": "Save this API key securely. It won't be shown again."
    }), 201


@api_bp.route('/keys/upgrade', methods=['POST'])
@require_api_key
def upgrade_api_key():
    """
    Get upgrade URL for API key.
    
    Request Body:
        - tier (str): Target tier (pro, enterprise)
    """
    data = request.get_json() or {}
    target_tier = data.get("tier", "pro")
    
    if target_tier not in ["pro", "enterprise"]:
        return jsonify({
            "error": "Invalid tier",
            "message": "Valid tiers are: pro, enterprise"
        }), 400
    
    tier_config = PRICING_TIERS[target_tier]
    
    # Generate checkout URL (would integrate with Lemon Squeezy)
    checkout_url = f"https://bestof-opensource.lemonsqueezy.com/checkout/buy/{tier_config['variant_id']}"
    
    return jsonify({
        "message": f"Upgrade to {tier_config['name']} tier",
        "tier": target_tier,
        "price": f"${tier_config['price']}/month",
        "features": tier_config["features"],
        "checkout_url": checkout_url
    })


@api_bp.route('/keys/status', methods=['GET'])
@require_api_key
def get_key_status():
    """Get current API key status and usage."""
    key_data = get_api_key_data(g.api_key)
    tier = key_data.get("tier", "free")
    tier_config = PRICING_TIERS[tier]
    
    # Get current usage
    key_hash = hash_api_key(g.api_key)
    day_key = f"rate:{key_hash}:day:{datetime.utcnow().strftime('%Y-%m-%d')}"
    
    daily_usage = 0
    if redis_conn:
        daily_usage = int(redis_conn.get(day_key) or 0)
    
    return jsonify({
        "data": {
            "tier": tier,
            "tier_name": tier_config["name"],
            "email": key_data.get("email"),
            "created_at": key_data.get("created_at"),
            "active": key_data.get("active") == "true",
            "usage": {
                "daily_requests": daily_usage,
                "daily_limit": tier_config["requests_per_day"],
                "rate_limit_per_minute": tier_config["rate_limit_per_minute"]
            },
            "features": tier_config["features"]
        }
    })


# ============================================================
# Webhook Handler for Lemon Squeezy
# ============================================================

@api_bp.route('/webhooks/lemonsqueezy', methods=['POST'])
def lemonsqueezy_webhook():
    """Handle Lemon Squeezy webhook events."""
    import hmac
    
    # Verify webhook signature
    signature = request.headers.get('X-Signature')
    if not signature or not LEMONSQUEEZY_WEBHOOK_SECRET:
        return jsonify({"error": "Invalid signature"}), 401
    
    expected_sig = hmac.new(
        LEMONSQUEEZY_WEBHOOK_SECRET.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Process webhook
    data = request.get_json()
    event_name = data.get("meta", {}).get("event_name")
    
    logger.info(f"Received Lemon Squeezy webhook: {event_name}")
    
    if event_name == "subscription_created":
        # Upgrade user's API key
        customer_email = data.get("data", {}).get("attributes", {}).get("user_email")
        variant_id = str(data.get("data", {}).get("attributes", {}).get("variant_id"))
        subscription_id = str(data.get("data", {}).get("id"))
        
        # Find tier by variant ID
        tier = "pro"  # default
        for tier_name, tier_config in PRICING_TIERS.items():
            if tier_config.get("variant_id") == variant_id:
                tier = tier_name
                break
        
        # Update user's API keys
        if redis_conn and customer_email:
            user_keys = redis_conn.smembers(f"user_keys:{customer_email}")
            for key_hash in user_keys:
                redis_conn.hset(f"api_key:{key_hash.decode()}", "tier", tier)
                redis_conn.hset(f"api_key:{key_hash.decode()}", "subscription_id", subscription_id)
        
        logger.info(f"Upgraded {customer_email} to {tier} tier")
    
    elif event_name == "subscription_cancelled":
        # Downgrade to free
        customer_email = data.get("data", {}).get("attributes", {}).get("user_email")
        
        if redis_conn and customer_email:
            user_keys = redis_conn.smembers(f"user_keys:{customer_email}")
            for key_hash in user_keys:
                redis_conn.hset(f"api_key:{key_hash.decode()}", "tier", "free")
                redis_conn.hset(f"api_key:{key_hash.decode()}", "subscription_id", "")
        
        logger.info(f"Downgraded {customer_email} to free tier")
    
    return jsonify({"received": True})


# ============================================================
# API Documentation Endpoint
# ============================================================

@api_bp.route('/docs', methods=['GET'])
def api_docs():
    """Return API documentation."""
    return jsonify({
        "name": "Best of Open Source API",
        "version": "1.0.0",
        "description": "Access repository scanning data programmatically",
        "base_url": "https://bestof-opensource.dev/api/v1",
        "authentication": {
            "type": "API Key",
            "header": "X-API-Key",
            "query_param": "api_key"
        },
        "pricing": {
            "free": {
                "price": "$0/month",
                "requests_per_day": 100,
                "features": ["Basic repository data", "Public repos only"]
            },
            "pro": {
                "price": "$9/month",
                "requests_per_day": 1000,
                "features": ["Full repository data", "AI insights", "Historical data"]
            },
            "enterprise": {
                "price": "$49/month",
                "requests_per_day": 10000,
                "features": ["Everything in Pro", "Bulk export", "Webhooks", "Priority support"]
            }
        },
        "endpoints": {
            "GET /repos": "List all scanned repositories",
            "GET /repos/{owner}/{repo}": "Get specific repository data",
            "GET /search?q={query}": "Search repositories",
            "GET /stats": "Get overall statistics",
            "GET /export": "Export all data (Enterprise only)",
            "POST /keys": "Create new API key",
            "GET /keys/status": "Get API key status"
        },
        "rate_limits": {
            "description": "Rate limits vary by tier",
            "headers": ["X-RateLimit-Remaining", "X-RateLimit-Limit"]
        }
    })


# Register after_request handler
@api_bp.after_request
def after_request(response):
    return add_rate_limit_headers(response)
