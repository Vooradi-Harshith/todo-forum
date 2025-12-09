from app.models.user import User

def is_admin(user: User) -> bool:
    return bool(
        getattr(user, "role", None) and getattr(user.role, "name", "") == "admin"
    )


def is_admin_or_mod(user: User) -> bool:
    if not user.role:
        return False
    return user.role.name in ["admin", "moderator"]
