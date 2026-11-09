"""Composition root: wires concrete SQLAlchemy repositories into services."""
from flask import current_app

from ..repositories.implementations import (
    SqlAlchemyAttachmentRepository, SqlAlchemyAuditLogRepository, SqlAlchemyCategoryRepository,
    SqlAlchemyCommentRepository, SqlAlchemyComplaintHistoryRepository,
    SqlAlchemyComplaintRepository, SqlAlchemyNotificationRepository, SqlAlchemyUserRepository)
from ..utils.files import UploadPolicy
from .auth_service import AuthService
from .complaint_service import ComplaintService
from .stats_service import StatsService

users = SqlAlchemyUserRepository
categories = SqlAlchemyCategoryRepository
notifications = SqlAlchemyNotificationRepository
attachments = SqlAlchemyAttachmentRepository
audit = SqlAlchemyAuditLogRepository
complaints = SqlAlchemyComplaintRepository


def upload_policy():
    cfg = current_app.config
    return UploadPolicy(folder=cfg["UPLOAD_FOLDER"], allowed=set(cfg["ALLOWED_EXTENSIONS"]),
                        max_size=cfg["MAX_FILE_SIZE"])


def auth_service():
    return AuthService(users(), audit())


def complaint_service():
    return ComplaintService(complaints(), SqlAlchemyComplaintHistoryRepository(), notifications(),
                            users(), categories(), SqlAlchemyCommentRepository(), attachments(),
                            audit(), upload_policy())


def stats_service():
    return StatsService(complaints(), users(), current_app.config["OVERDUE_DAYS"])
