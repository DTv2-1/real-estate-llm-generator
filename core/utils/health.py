# =============================================================================
# HEALTH CHECK ENDPOINT
# Add this to config/urls.py
# =============================================================================

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 if all systems are operational.
    """
    logger.info("🏥 Health check started")
    health_status = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown',
        'celery': 'unknown'
    }
    
    # Check database
    try:
        logger.info("🔍 Checking database connection...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['database'] = 'ok'
        logger.info("✅ Database OK")
    except Exception as e:
        logger.error(f"❌ Database error: {str(e)}")
        health_status['status'] = 'unhealthy'
        health_status['database'] = f'error: {str(e)}'
    
    # Check Redis cache (optional)
    try:
        logger.info("🔍 Checking Redis cache...")
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['cache'] = 'ok'
            logger.info("✅ Redis cache OK")
        else:
            health_status['cache'] = 'error'
            logger.warning("⚠️ Redis cache check failed")
    except Exception as e:
        logger.warning(f"⚠️ Redis unavailable: {str(e)}")
        health_status['cache'] = f'unavailable: {str(e)}'
        # Don't mark as unhealthy - Redis is optional
    
    # Check Celery (via Redis) - optional
    try:
        logger.info("🔍 Checking Celery broker...")
        from django.conf import settings
        redis_client = redis.from_url(settings.CELERY_BROKER_URL)
        redis_client.ping()
        health_status['celery'] = 'ok'
        logger.info("✅ Celery broker OK")
    except Exception as e:
        logger.warning(f"⚠️ Celery unavailable: {str(e)}")
        health_status['celery'] = f'unavailable: {str(e)}'
        # Don't mark as unhealthy - Celery is optional
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    logger.info(f"🏥 Health check completed: {health_status['status']} (HTTP {status_code})")
    logger.info(f"📊 Status details: {health_status}")
    return JsonResponse(health_status, status=status_code)
