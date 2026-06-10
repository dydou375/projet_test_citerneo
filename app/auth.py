import os
import secrets

from fastapi import Request


# Identifiants configurables via variables d'environnement.
# En dev : admin/admin par défaut. En prod : définir APP_USERNAME et APP_PASSWORD.
APP_USERNAME = os.getenv("APP_USERNAME", "admin")
APP_PASSWORD = os.getenv("APP_PASSWORD", "admin")


class RequiresLogin(Exception):
    """Levée quand une route protégée est accédée sans être connecté."""
    pass


def check_credentials(username: str, password: str) -> bool:
    # compare_digest compare les deux chaînes en temps constant.
    # Sans ça, un attaquant pourrait deviner le mot de passe caractère par
    # caractère en mesurant le temps de réponse (timing attack).
    user_ok = secrets.compare_digest(username, APP_USERNAME)
    pass_ok = secrets.compare_digest(password, APP_PASSWORD)
    return user_ok and pass_ok


def require_auth(request: Request):
    """Dépendance FastAPI : bloque l'accès si l'utilisateur n'est pas connecté."""
    if not request.session.get("logged_in"):
        raise RequiresLogin()
