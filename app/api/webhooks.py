from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from typing import List

from app.services.webhook_service import WebhookManager
from app.models.schemas import WebhookRegistration

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
webhook_manager = WebhookManager()


@router.post("/register")
async def register_webhook(request: WebhookRegistration):
    """Register a webhook URL"""
    try:
        webhook_id = webhook_manager.register_webhook(request.url, request.events)
        return {
            "webhook_id": webhook_id,
            "url": request.url,
            "events": request.events,
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Webhook registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook registration failed")


@router.get("/list")
async def list_webhooks():
    """List all registered webhooks"""
    webhooks = webhook_manager.list_webhooks()
    return [
        {
            "id": k,
            "url": v["url"],
            "events": v["events"],
            "active": v["active"],
            "created_at": v["created_at"].isoformat()
        }
        for k, v in {webhook_manager.webhooks[wid]["id"]: v for wid, v in webhook_manager.webhooks.items()}.items()
    ]


@router.delete("/{webhook_id}")
async def unregister_webhook(webhook_id: str):
    """Unregister a webhook"""
    if webhook_manager.unregister_webhook(webhook_id):
        return {"message": "Webhook unregistered"}
    raise HTTPException(status_code=404, detail="Webhook not found")


logger = logging.getLogger(__name__)
