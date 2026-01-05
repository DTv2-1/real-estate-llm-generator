# =============================================================================
# HEALTH CHECK ENDPOINT
# Add this to config/urls.py
# =============================================================================

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis

def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 if all systems are operational.
    """
    health_status = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown',
        'celery': 'unknown'
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['database'] = 'ok'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['database'] = f'error: {str(e)}'
    
    # Check Redis cache
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['cache'] = 'ok'
        else:
            health_status['cache'] = 'error'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['cache'] = f'error: {str(e)}'
    
    # Check Celery (via Redis)
    try:
        from django.conf import settings
        redis_client = redis.from_url(settings.CELERY_BROKER_URL)
        redis_client.ping()
        health_status['celery'] = 'ok'
    except Exception as e:
        health_status['celery'] = f'error: {str(e)}'
        # Don't mark as unhealthy - Celery is optional
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)
