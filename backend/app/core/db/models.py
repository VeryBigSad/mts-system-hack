"""
Database models using Tortoise ORM.

Defines the data models for the application:
- Timestamp mixins for created/updated tracking
- Database schema configuration and relationships
"""

import logging

from tortoise import fields
from tortoise.models import Model

logger = logging.getLogger(__name__)


# class User(Model):
#     class Meta:
#         table = "users"
#         ordering = ["created_at"]

#     id = fields.BigIntField(pk=True, unique=True, index=True)
#     first_name = fields.CharField(max_length=64)
#     last_name = fields.CharField(max_length=64, null=True)
#     username = fields.CharField(max_length=32, index=True, null=True)
#     language_code = fields.CharField(max_length=2, null=True)
#     is_premium = fields.BooleanField(null=True)

#     deeplink = fields.CharField(max_length=128, null=True)
#     is_blocked_by_user = fields.BooleanField(default=False)
#     is_blocked_by_bot = fields.BooleanField(default=False)

#     created_at = fields.DatetimeField(auto_now_add=True)
#     updated_at = fields.DatetimeField(auto_now=True)

class User(Model):
    class Meta:
        table = "users"
        ordering = ["created_at"]

    id = fields.BigIntField(pk=True, unique=True, index=True)
