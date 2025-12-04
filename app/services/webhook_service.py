import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import aiohttp

logger = logging.getLogger(__name__)


class WebhookManager:
    """Manage webhook registrations and dispatching"""
    
    def __init__(self):
        self.webhooks: Dict[str, Dict[str, Any]] = {}
        self.pending_events: Dict[str, Dict[str, Any]] = {}
    
    def register_webhook(self, url: str, events: list) -> str:
        """Register a webhook URL"""
        webhook_id = str(uuid.uuid4())
        self.webhooks[webhook_id] = {
            "url": url,
            "events": events,
            "created_at": datetime.utcnow(),
            "active": True
        }
        logger.info(f"Registered webhook {webhook_id}: {url}")
        return webhook_id
    
    def list_webhooks(self) -> list:
        """List all registered webhooks"""
        return list(self.webhooks.values())
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """Unregister a webhook"""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            logger.info(f"Unregistered webhook {webhook_id}")
            return True
        return False
    
    async def emit_event(self, event_type: str, task_id: str, data: Dict[str, Any], error: Optional[str] = None):
        """Emit an event to all registered webhooks"""
        tasks = []
        
        for webhook_id, webhook_config in self.webhooks.items():
            if event_type in webhook_config.get("events", []):
                payload = {
                    "event_type": event_type,
                    "task_id": task_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": data,
                    "error": error
                }
                
                task = self._dispatch_webhook(webhook_config["url"], payload)
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _dispatch_webhook(self, url: str, payload: Dict[str, Any], retries: int = 3):
        """Dispatch webhook with retry logic"""
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                        if 200 <= resp.status < 300:
                            logger.info(f"Webhook delivered successfully: {url}")
                            return
                        else:
                            logger.warning(f"Webhook returned status {resp.status}: {url}")
            except asyncio.TimeoutError:
                logger.warning(f"Webhook timeout (attempt {attempt + 1}): {url}")
            except Exception as e:
                logger.warning(f"Webhook dispatch failed (attempt {attempt + 1}): {str(e)}")
            
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Failed to deliver webhook after {retries} attempts: {url}")
