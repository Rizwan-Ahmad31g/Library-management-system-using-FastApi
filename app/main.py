from fastapi import FastAPI
from app.api import librarian, library_patron, user, user_credentials

app = FastAPI()
app.include_router(user_credentials.router_cred)
app.include_router(librarian.router, prefix="/api")
app.include_router(librarian.router_member, prefix="/api")
app.include_router(librarian.router_report, prefix="/api")
app.include_router(library_patron.router, prefix="/api")

