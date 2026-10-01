from app.database.models.base_model import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"
