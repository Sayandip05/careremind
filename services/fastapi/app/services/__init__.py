# ── Services Package ─────────────────────────────────────────
# Services are imported directly where needed (e.g., from app.services import patient_service)
# No eager imports here to avoid circular dependency issues.
from app.services.tenant_service import update_profile
from app.services import auth_service
