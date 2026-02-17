"""
Google Analytics 4 Integration for Forbidden Command Center
Pulls real GA4 data via the Google Analytics Data API v1.

Setup:
1. Go to https://console.cloud.google.com
2. Create a project (or use existing)
3. Enable "Google Analytics Data API"
4. Create a Service Account under IAM & Admin > Service Accounts
5. Download the JSON key file
6. In GA4 Admin > Property > Property Access Management, add the service account email as Viewer
7. Set env vars on Render:
   GA4_PROPERTY_ID = your numeric property ID (found in GA4 Admin > Property Settings)
   GA4_CREDENTIALS_JSON = the entire JSON key file contents (paste it all)
"""

import os
import json
from datetime import datetime, timedelta

# Will be None if library not installed
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric,
        RunRealtimeReportRequest, OrderBy, Filter, FilterExpression
    )
    from google.oauth2 import service_account
    GA4_AVAILABLE = True
except ImportError:
    GA4_AVAILABLE = False

PROPERTY_ID = os.environ.get('GA4_PROPERTY_ID', '')
CREDENTIALS_JSON = os.environ.get('GA4_CREDENTIALS_JSON', '')


def is_configured():
    """Check if GA4 is properly configured"""
    return bool(GA4_AVAILABLE and PROPERTY_ID and CREDENTIALS_JSON)


def _get_client():
    """Create authenticated GA4 client"""
    if not is_configured():
        return None
    try:
        creds_dict = json.loads(CREDENTIALS_JSON)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        return BetaAnalyticsDataClient(credentials=credentials)
    except Exception as e:
        print(f"GA4 auth error: {e}")
        return None


def get_realtime():
    """Get real-time active users"""
    client = _get_client()
    if not client:
        return {'active_users': 0}
    
    try:
        request = RunRealtimeReportRequest(
            property=f"properties/{PROPERTY_ID}",
            metrics=[Metric(name="activeUsers")],
            dimensions=[Dimension(name="country")]
        )
        response = client.run_realtime_report(request)
        
        total = 0
        countries = []
        for row in response.rows:
            count = int(row.metric_values[0].value)
            total += count
            countries.append({
                'country': row.dimension_values[0].value,
                'users': count
            })
        
        return {
            'active_users': total,
            'countries': sorted(countries, key=lambda x: x['users'], reverse=True)[:10]
        }
    except Exception as e:
        print(f"GA4 realtime error: {e}")
        return {'active_users': 0, 'countries': []}


def get_overview(days=30):
    """Get overview metrics for a date range"""
    client = _get_client()
    if not client:
        return None
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Previous period for comparison
        prev_end = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        prev_start = (datetime.now() - timedelta(days=days * 2)).strftime('%Y-%m-%d')
        
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            date_ranges=[
                DateRange(start_date=start_date, end_date=end_date),
                DateRange(start_date=prev_start, end_date=prev_end)
            ],
            metrics=[
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
                Metric(name="engagedSessions"),
                Metric(name="eventCount"),
            ]
        )
        response = client.run_report(request)
        
        current = response.rows[0].metric_values if response.rows else None
        previous = response.rows[0].metric_values if len(response.rows) > 0 else None
        
        # Current period values
        if current:
            # The response has 2 date ranges, so metrics alternate
            # Actually with multiple date ranges, each row has metrics for each date range
            # Let me parse properly
            result = {
                'users': int(current[0].value) if current else 0,
                'new_users': int(current[1].value) if current else 0,
                'sessions': int(current[2].value) if current else 0,
                'pageviews': int(current[3].value) if current else 0,
                'avg_duration': float(current[4].value) if current else 0,
                'bounce_rate': float(current[5].value) if current else 0,
                'engaged_sessions': int(current[6].value) if current else 0,
                'events': int(current[7].value) if current else 0,
            }
            
            # Previous period for comparison (second set of values, indices 8-15)
            if len(current) > 8:
                prev_users = int(current[8].value) if current[8].value else 1
                prev_sessions = int(current[10].value) if current[10].value else 1
                prev_pageviews = int(current[11].value) if current[11].value else 1
                result['users_change'] = round(((result['users'] - prev_users) / max(prev_users, 1)) * 100, 1)
                result['sessions_change'] = round(((result['sessions'] - prev_sessions) / max(prev_sessions, 1)) * 100, 1)
                result['pageviews_change'] = round(((result['pageviews'] - prev_pageviews) / max(prev_pageviews, 1)) * 100, 1)
            
            # Format duration as m:ss
            mins = int(result['avg_duration'] // 60)
            secs = int(result['avg_duration'] % 60)
            result['avg_duration_formatted'] = f"{mins}:{secs:02d}"
            result['bounce_rate_formatted'] = f"{result['bounce_rate']:.1f}%"
            
            return result
        
        return None
    except Exception as e:
        print(f"GA4 overview error: {e}")
        return None


def get_daily_traffic(days=30):
    """Get daily users/sessions/pageviews for charting"""
    client = _get_client()
    if not client:
        return []
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="date")],
            metrics=[
                Metric(name="totalUsers"),
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
            ],
            order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))]
        )
        response = client.run_report(request)
        
        daily = []
        for row in response.rows:
            date_str = row.dimension_values[0].value  # YYYYMMDD
            daily.append({
                'date': f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}",
                'users': int(row.metric_values[0].value),
                'sessions': int(row.metric_values[1].value),
                'pageviews': int(row.metric_values[2].value),
            })
        
        return daily
    except Exception as e:
        print(f"GA4 daily error: {e}")
        return []


def get_top_pages(days=30, limit=15):
    """Get top pages by pageviews"""
    client = _get_client()
    if not client:
        return []
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="pagePath"),
                Dimension(name="pageTitle"),
            ],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="totalUsers"),
                Metric(name="averageSessionDuration"),
            ],
            order_bys=[OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"),
                desc=True
            )],
            limit=limit
        )
        response = client.run_report(request)
        
        pages = []
        for row in response.rows:
            pages.append({
                'path': row.dimension_values[0].value,
                'title': row.dimension_values[1].value,
                'pageviews': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value),
                'avg_duration': float(row.metric_values[2].value),
            })
        
        return pages
    except Exception as e:
        print(f"GA4 pages error: {e}")
        return []


def get_traffic_sources(days=30, limit=10):
    """Get traffic sources / channels"""
    client = _get_client()
    if not client:
        return []
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="sessionDefaultChannelGroup"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="screenPageViews"),
                Metric(name="engagedSessions"),
            ],
            order_bys=[OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name="sessions"),
                desc=True
            )],
            limit=limit
        )
        response = client.run_report(request)
        
        sources = []
        for row in response.rows:
            sessions = int(row.metric_values[0].value)
            engaged = int(row.metric_values[3].value)
            sources.append({
                'channel': row.dimension_values[0].value,
                'sessions': sessions,
                'users': int(row.metric_values[1].value),
                'pageviews': int(row.metric_values[2].value),
                'engagement_rate': round((engaged / max(sessions, 1)) * 100, 1),
            })
        
        return sources
    except Exception as e:
        print(f"GA4 sources error: {e}")
        return []


def get_referrals(days=30, limit=10):
    """Get top referring sites"""
    client = _get_client()
    if not client:
        return []
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="sessionSource")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
            ],
            order_bys=[OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name="sessions"),
                desc=True
            )],
            limit=limit
        )
        response = client.run_report(request)
        
        referrals = []
        for row in response.rows:
            referrals.append({
                'source': row.dimension_values[0].value,
                'sessions': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value),
            })
        
        return referrals
    except Exception as e:
        print(f"GA4 referrals error: {e}")
        return []


def get_devices(days=30):
    """Get device category breakdown"""
    client = _get_client()
    if not client:
        return []
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="deviceCategory")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
            ],
            order_bys=[OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name="sessions"),
                desc=True
            )]
        )
        response = client.run_report(request)
        
        devices = []
        total = sum(int(r.metric_values[0].value) for r in response.rows)
        for row in response.rows:
            sessions = int(row.metric_values[0].value)
            devices.append({
                'device': row.dimension_values[0].value.title(),
                'sessions': sessions,
                'users': int(row.metric_values[1].value),
                'percentage': round((sessions / max(total, 1)) * 100, 1),
            })
        
        return devices
    except Exception as e:
        print(f"GA4 devices error: {e}")
        return []


def get_geo(days=30, limit=10):
    """Get geographic breakdown by country"""
    client = _get_client()
    if not client:
        return []
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="country")],
            metrics=[
                Metric(name="totalUsers"),
                Metric(name="sessions"),
            ],
            order_bys=[OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name="totalUsers"),
                desc=True
            )],
            limit=limit
        )
        response = client.run_report(request)
        
        geo = []
        for row in response.rows:
            geo.append({
                'country': row.dimension_values[0].value,
                'users': int(row.metric_values[0].value),
                'sessions': int(row.metric_values[1].value),
            })
        
        return geo
    except Exception as e:
        print(f"GA4 geo error: {e}")
        return []


def get_cities(days=30, limit=15):
    """Get geographic breakdown by city"""
    client = _get_client()
    if not client:
        return []
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="city"),
                Dimension(name="region"),
            ],
            metrics=[
                Metric(name="totalUsers"),
                Metric(name="sessions"),
            ],
            order_bys=[OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name="totalUsers"),
                desc=True
            )],
            limit=limit
        )
        response = client.run_report(request)
        
        cities = []
        for row in response.rows:
            city = row.dimension_values[0].value
            if city and city != '(not set)':
                cities.append({
                    'city': city,
                    'region': row.dimension_values[1].value,
                    'users': int(row.metric_values[0].value),
                    'sessions': int(row.metric_values[1].value),
                })
        
        return cities
    except Exception as e:
        print(f"GA4 cities error: {e}")
        return []


def get_all_data(days=30):
    """Fetch all GA4 data in one call for the dashboard"""
    if not is_configured():
        return None
    
    return {
        'configured': True,
        'overview': get_overview(days),
        'daily': get_daily_traffic(days),
        'top_pages': get_top_pages(days),
        'sources': get_traffic_sources(days),
        'referrals': get_referrals(days),
        'devices': get_devices(days),
        'geo': get_geo(days),
        'cities': get_cities(days),
        'realtime': get_realtime(),
    }
