import httpx # Using httpx for synchronous HTTP requests in Celery task
import hmac
import hashlib
import json
from celery import Celery
from typing import Dict, Any, Optional

# Initialize Celery app
# This should ideally use configuration from app/config.py
# For simplicity, hardcoding a Redis broker URL for now.
# In a real setup, you'd pass the broker URL from settings.
celery_app = Celery(
    'webhook_tasks',
    broker='redis://localhost:6379/1', # Use a different DB than the main app's Redis if possible
    backend='redis://localhost:6379/2' # Use a different DB for results
)

@celery_app.task(bind=True, max_retries=5, default_retry_delay=60)
def send_webhook_task(self, target_url: str, payload: Dict[str, Any], secret: str, headers: Optional[Dict[str, Any]] = None):
    """
    Celery task to send a webhook payload to the target URL.
    Includes retry logic.
    """
    try:
        # Sign the payload
        signature = hmac.new(
            secret.encode('utf-8'),
            json.dumps(payload, sort_keys=True).encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if headers is None:
            headers = {}
        headers['X-Webhook-Signature'] = signature
        headers['Content-Type'] = 'application/json'

        # Use httpx for making the HTTP request
        response = httpx.post(target_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        print(f"Celery: Webhook successfully sent to {target_url}. Status: {response.status_code}")

    except httpx.RequestError as exc:
        print(f"Celery: Request error while sending webhook to {target_url}: {exc}")
        try:
            self.retry(exc=exc)
        except Exception as retry_exc:
            print(f"Celery: Max retries exceeded for {target_url}. Final error: {retry_exc}")
    except httpx.HTTPStatusError as exc:
        print(f"Celery: HTTP error {exc.response.status_code} while sending webhook to {target_url}: {exc}")
        if 400 <= exc.response.status_code < 500:
            # Client error, usually no point in retrying (e.g., bad URL)
            print(f"Celery: Not retrying client error for {target_url}.")
        else:
            # Server error, retry
            try:
                self.retry(exc=exc)
            except Exception as retry_exc:
                print(f"Celery: Max retries exceeded for {target_url}. Final error: {retry_exc}")
    except Exception as e:
        print(f"Celery: An unexpected error occurred while sending webhook to {target_url}: {e}")
        # For unexpected errors, also consider retrying
        try:
            self.retry(exc=e)
        except Exception as retry_exc:
            print(f"Celery: Max retries exceeded for {target_url}. Final error: {retry_exc}")