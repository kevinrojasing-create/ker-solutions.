"""
Plan Enforcement - MVP Feature Restrictions
Middleware and utilities to enforce subscription plan limits
"""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from sql_models import User, Asset, SubscriptionPlan
from schemas import PlanLimits, FeatureAccessResponse


# ============================================================================
# PLAN LIMITS CONFIGURATION
# ============================================================================

PLAN_LIMITS_CONFIG = {
    SubscriptionPlan.FREE: {
        "max_assets": 1,
        "ocr_enabled": False,
        "cost_estimation_enabled": False,
        "iot_visualization_enabled": False,
        "remote_control_enabled": False,
        "human_support_enabled": False,
        "pdf_reports_enabled": False,
    },
    SubscriptionPlan.DIGITAL: {
        "max_assets": 20,
        "ocr_enabled": True,
        "cost_estimation_enabled": True,
        "iot_visualization_enabled": False,
        "remote_control_enabled": False,
        "human_support_enabled": False,
        "pdf_reports_enabled": False,
    },
    SubscriptionPlan.MONITOR: {
        "max_assets": None,  # Unlimited
        "ocr_enabled": True,
        "cost_estimation_enabled": True,
        "iot_visualization_enabled": True,
        "remote_control_enabled": False,
        "human_support_enabled": True,
        "pdf_reports_enabled": True,
    },
    SubscriptionPlan.CONTROL_TOTAL: {
        "max_assets": None,  # Unlimited
        "ocr_enabled": True,
        "cost_estimation_enabled": True,
        "iot_visualization_enabled": True,
        "remote_control_enabled": True,
        "human_support_enabled": True,
        "pdf_reports_enabled": True,
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_plan_limits(plan: SubscriptionPlan) -> PlanLimits:
    """Get limits for a specific plan"""
    config = PLAN_LIMITS_CONFIG.get(plan)
    if not config:
        # Default to FREE plan if unknown
        config = PLAN_LIMITS_CONFIG[SubscriptionPlan.FREE]
    
    return PlanLimits(
        plan=plan,
        **config
    )


async def check_asset_limit(user: User, db: AsyncSession) -> FeatureAccessResponse:
    """Check if user can create more assets based on their plan"""
    limits = get_plan_limits(user.plan)
    
    # If unlimited (None), allow
    if limits.max_assets is None:
        return FeatureAccessResponse(has_access=True)
    
    # Count user's current assets across all their locales
    from sql_models import Local
    result = await db.execute(
        select(func.count(Asset.id))
        .join(Local, Asset.local_id == Local.id)
        .where(
            Local.owner_id == user.id,
            Asset.deleted_at.is_(None)
        )
    )
    current_assets = result.scalar() or 0
    
    if current_assets >= limits.max_assets:
        next_plan = None
        if user.plan == SubscriptionPlan.FREE:
            next_plan = SubscriptionPlan.DIGITAL
        
        return FeatureAccessResponse(
            has_access=False,
            reason=f"Plan {user.plan.value} limitado a {limits.max_assets} activo(s). Tienes {current_assets}.",
            upgrade_plan=next_plan
        )
    
    return FeatureAccessResponse(has_access=True)


def check_feature_access(user: User, feature: str) -> FeatureAccessResponse:
    """Check if user's plan allows access to a specific feature"""
    limits = get_plan_limits(user.plan)
    
    feature_enabled = getattr(limits, feature, False)
    
    if not feature_enabled:
        # Determine which plan provides this feature
        upgrade_plan = None
        for plan, config in PLAN_LIMITS_CONFIG.items():
            if config.get(feature, False) and plan.value > user.plan.value:
                upgrade_plan = plan
                break
        
        return FeatureAccessResponse(
            has_access=False,
            reason=f"Función '{feature}' no disponible en plan {user.plan.value}.",
            upgrade_plan=upgrade_plan
        )
    
    return FeatureAccessResponse(has_access=True)


# ============================================================================
# ENFORCEMENT DECORATORS/MIDDLEWARE
# ============================================================================

def require_feature(feature: str):
    """Decorator to require a specific feature"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs (injected by get_current_user dependency)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Check feature access
            access = check_feature_access(current_user, feature)
            if not access.has_access:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "message": access.reason,
                        "upgrade_to": access.upgrade_plan.value if access.upgrade_plan else None
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def enforce_asset_limit(user: User, db: AsyncSession):
    """Raise exception if user has reached asset limit"""
    access = await check_asset_limit(user, db)
    if not access.has_access:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": access.reason,
                "upgrade_to": access.upgrade_plan.value if access.upgrade_plan else None,
                "locked_feature": "create_asset"
            }
        )


def enforce_feature_access(user: User, feature: str):
    """Raise exception if user doesn't have access to feature"""
    access = check_feature_access(user, feature)
    if not access.has_access:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": access.reason,
                "upgrade_to": access.upgrade_plan.value if access.upgrade_plan else None,
                "locked_feature": feature
            }
        )
