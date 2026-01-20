from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.database import get_db
from app.models import AnalyticsResponse

router = APIRouter()

# Get credentials from environment variables
TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")


@router.get("/tiktok")
async def get_tiktok_analytics():
    """
    Get TikTok analytics data
    Requires TikTok Business API credentials in .env file
    """
    # Check if credentials are available
    if not TIKTOK_ACCESS_TOKEN and not TIKTOK_CLIENT_KEY:
        # Return mock data for development
        return {
            "platform": "tiktok",
            "metrics": {
                "followers": 15420,
                "likes": 125000,
                "views": 2500000,
                "engagement_rate": 4.8,
                "posts_count": 156,
                "growth": 12.5  # percentage
            },
            "updated_at": datetime.utcnow().isoformat(),
            "note": "Using mock data. Add TikTok credentials to .env file for real data. See SOCIAL_MEDIA_SETUP.md for instructions."
        }
    
    # TikTok Business API integration
    try:
        headers = {
            "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Get user info
        user_response = requests.get(
            "https://open.tiktokapis.com/v2/user/info/",
            headers=headers,
            params={"fields": "display_name,avatar_url,follower_count,following_count,likes_count,video_count"}
        )
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            user_info = user_data.get("data", {}).get("user", {})
            
            # Get video insights
            videos_response = requests.get(
                "https://open.tiktokapis.com/v2/video/list/",
                headers=headers,
                params={"max_count": 10}
            )
            
            total_views = 0
            total_likes = 0
            video_count = user_info.get("video_count", 0)
            
            if videos_response.status_code == 200:
                videos_data = videos_response.json()
                videos = videos_data.get("data", {}).get("videos", [])
                for video in videos:
                    total_views += video.get("view_count", 0)
                    total_likes += video.get("like_count", 0)
            
            followers = user_info.get("follower_count", 0)
            engagement_rate = (total_likes / total_views * 100) if total_views > 0 else 0
            
            return {
                "platform": "tiktok",
                "metrics": {
                    "followers": followers,
                    "likes": total_likes,
                    "views": total_views,
                    "engagement_rate": round(engagement_rate, 2),
                    "posts_count": video_count,
                    "growth": 0  # Calculate from historical data
                },
                "updated_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=user_response.status_code,
                detail=f"TikTok API error: {user_response.text}"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching TikTok data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing TikTok data: {str(e)}")


@router.get("/instagram")
async def get_instagram_analytics():
    """
    Get Instagram analytics data
    Requires Instagram Graph API access token and business account ID in .env file
    """
    # Check if credentials are available
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        # Return mock data for development
        return {
            "platform": "instagram",
            "metrics": {
                "followers": 8920,
                "following": 450,
                "posts": 234,
                "engagement_rate": 5.2,
                "average_likes": 465,
                "average_comments": 32,
                "reach": 15000,
                "growth": 8.3  # percentage
            },
            "updated_at": datetime.utcnow().isoformat(),
            "note": "Using mock data. Add Instagram credentials to .env file for real data. See SOCIAL_MEDIA_SETUP.md for instructions."
        }
    
    # Instagram Graph API integration
    try:
        base_url = "https://graph.facebook.com/v18.0"
        account_id = INSTAGRAM_BUSINESS_ACCOUNT_ID
        
        # Get account info
        account_response = requests.get(
            f"{base_url}/{account_id}",
            params={
                "fields": "username,account_type,profile_picture_url",
                "access_token": INSTAGRAM_ACCESS_TOKEN
            }
        )
        
        if account_response.status_code != 200:
            raise HTTPException(
                status_code=account_response.status_code,
                detail=f"Instagram API error: {account_response.text}"
            )
        
        # Get insights/metrics
        insights_response = requests.get(
            f"{base_url}/{account_id}/insights",
            params={
                "metric": "follower_count,impressions,reach,profile_views",
                "period": "day",
                "access_token": INSTAGRAM_ACCESS_TOKEN
            }
        )
        
        # Get media count
        media_response = requests.get(
            f"{base_url}/{account_id}/media",
            params={
                "fields": "like_count,comments_count,engagement",
                "access_token": INSTAGRAM_ACCESS_TOKEN,
                "limit": 25
            }
        )
        
        # Parse insights
        insights_data = insights_response.json().get("data", []) if insights_response.status_code == 200 else []
        followers = 0
        reach = 0
        impressions = 0
        
        for insight in insights_data:
            metric_name = insight.get("name")
            values = insight.get("values", [])
            if values:
                value = values[0].get("value", 0)
                if metric_name == "follower_count":
                    followers = value
                elif metric_name == "reach":
                    reach = value
                elif metric_name == "impressions":
                    impressions = value
        
        # Parse media data
        media_data = media_response.json().get("data", []) if media_response.status_code == 200 else []
        total_likes = sum(post.get("like_count", 0) for post in media_data)
        total_comments = sum(post.get("comments_count", 0) for post in media_data)
        posts_count = len(media_data)
        
        avg_likes = total_likes / posts_count if posts_count > 0 else 0
        avg_comments = total_comments / posts_count if posts_count > 0 else 0
        engagement_rate = ((total_likes + total_comments) / impressions * 100) if impressions > 0 else 0
        
        return {
            "platform": "instagram",
            "metrics": {
                "followers": followers,
                "following": 0,  # Not available in basic API
                "posts": posts_count,
                "engagement_rate": round(engagement_rate, 2),
                "average_likes": round(avg_likes, 0),
                "average_comments": round(avg_comments, 0),
                "reach": reach,
                "growth": 0  # Calculate from historical data
            },
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Instagram data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Instagram data: {str(e)}")


@router.get("/sheets")
async def get_sheets_analytics(db: Session = Depends(get_db)):
    """
    Get Google Sheets analytics
    Uses existing sheets_client to fetch data and calculate metrics
    """
    try:
        from pathlib import Path
        
        from src.sheets_client import SheetsClient
        import yaml
        
        # Load config
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        client = SheetsClient(
            spreadsheet_id=config['google_sheets']['spreadsheet_id'],
            service_account_path=config['google_sheets']['service_account_path']
        )
        
        # Get all sheets data
        try:
            orders_sheet = client.spreadsheet.worksheet("Orders")
            orders_data = orders_sheet.get_all_values()
        except:
            orders_data = []
        
        try:
            products_sheet = client.spreadsheet.worksheet("Products")
            products_data = products_sheet.get_all_values()
        except:
            products_data = []
        
        try:
            customers_sheet = client.spreadsheet.worksheet("Customers")
            customers_data = customers_sheet.get_all_values()
        except:
            customers_data = []
        
        # Calculate metrics
        total_orders = len(orders_data) - 1 if orders_data and len(orders_data) > 1 else 0
        total_products = len(products_data) - 1 if products_data and len(products_data) > 1 else 0
        total_customers = len(customers_data) - 1 if customers_data and len(customers_data) > 1 else 0
        
        # Calculate total revenue from orders (look for Total Profit column)
        total_revenue = 0
        if orders_data and len(orders_data) > 1:
            # Find the Total Profit column index
            headers = orders_data[0] if orders_data else []
            profit_col_idx = None
            for idx, header in enumerate(headers):
                if 'total profit' in header.lower() or 'revenue' in header.lower():
                    profit_col_idx = idx
                    break
            
            if profit_col_idx is not None:
                for order in orders_data[1:]:  # Skip header
                    try:
                        if len(order) > profit_col_idx and order[profit_col_idx]:
                            profit_str = str(order[profit_col_idx]).replace('$', '').replace(',', '').strip()
                            # Handle formulas
                            if not profit_str.startswith('='):
                                total_revenue += float(profit_str)
                    except (ValueError, IndexError):
                        continue
        
        return {
            "platform": "google_sheets",
            "metrics": {
                "total_orders": total_orders,
                "total_products": total_products,
                "total_customers": total_customers,
                "total_revenue": round(total_revenue, 2),
                "average_order_value": round(total_revenue / total_orders, 2) if total_orders > 0 else 0
            },
            "updated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Google Sheets data: {str(e)}")


@router.get("/all")
async def get_all_analytics():
    """Get all analytics data in one call"""
    tiktok = await get_tiktok_analytics()
    instagram = await get_instagram_analytics()
    sheets = await get_sheets_analytics()
    
    return {
        "tiktok": tiktok,
        "instagram": instagram,
        "sheets": sheets,
        "updated_at": datetime.utcnow().isoformat()
    }

