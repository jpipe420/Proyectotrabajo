from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.router import user
from router.products_router import product_router
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos los routers
app.include_router(user)
app.include_router(product_router)

@app.get("/")
def root():
    return {"message": "API funcionando"}