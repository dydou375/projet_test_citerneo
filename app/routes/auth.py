from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import check_credentials
from app.config import templates

router = APIRouter(tags=["Auth"])


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    # Si déjà connecté, on redirige directement vers l'app.
    if request.session.get("logged_in"):
        return RedirectResponse(url="/commandes/", status_code=302)
    return templates.TemplateResponse(request, "auth/login.html", {})


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if check_credentials(username, password):
        request.session["logged_in"] = True
        request.session["username"] = username
        # 302 : redirection temporaire vers la page principale après connexion.
        return RedirectResponse(url="/commandes/", status_code=302)

    # Identifiants incorrects : on réaffiche le formulaire avec un message d'erreur.
    return templates.TemplateResponse(
        request, "auth/login.html",
        {"error": "Nom d'utilisateur ou mot de passe incorrect."},
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
