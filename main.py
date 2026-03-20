"""Nike Bot Pro - Auth Server (Minimal)"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from nike_bot import NikeBot
from nike_scraper import NikeScraper

# Config
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nike_bot.db")
ALGORITHM = "HS256"

# Database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# Models
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SKUSize(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True)
    size: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NikeProduct(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True)
    name: str
    price: Optional[int] = None
    sizes: str = Field(default="[]")  # JSON string de lista
    image: Optional[str] = None
    url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SKUSizeRequest(BaseModel):
    sku: str
    size: str

class SKUSizeResponse(BaseModel):
    id: int
    sku: str
    size: str
    created_at: datetime

class NikeAddToCartRequest(BaseModel):
    url: str  # URL completa del producto: https://nike.cl/products/12345
    headless: bool = False  # Si True, ejecuta sin mostrar navegador

class NikeProductRequest(BaseModel):
    url: str  # URL de producto a scrapear

class NikeProductResponse(BaseModel):
    sku: str
    name: str
    price: Optional[int] = None
    sizes: List[str]
    image: Optional[str] = None
    url: str

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(days=30),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Database session
def get_session():
    with Session(engine) as session:
        yield session

# App
app = FastAPI(title="Nike Bot Auth", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)

# Routes
@app.get("/")
def root():
    return {"message": "Nike Bot Pro Auth Server - Nike Bot Module v2"}

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0"}

@app.post("/auth/register", response_model=TokenResponse)
def register(req: RegisterRequest, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == req.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(email=req.email, hashed_password=hash_password(req.password))
    session.add(user)
    session.commit()
    
    return TokenResponse(access_token=create_token(req.email))

@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == req.email)).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return TokenResponse(access_token=create_token(req.email))

@app.post("/auth/validate")
def validate(token: str, session: Session = Depends(get_session)):
    email = verify_token(token)
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"email": user.email, "id": user.id, "valid": True}

# Nike Routes
@app.post("/nike/sku/add", response_model=SKUSizeResponse)
def add_sku_mapping(req: SKUSizeRequest, session: Session = Depends(get_session)):
    """Agrega o actualiza el mapeo SKU → Talla"""
    existing = session.exec(select(SKUSize).where(SKUSize.sku == req.sku)).first()
    
    if existing:
        existing.size = req.size
        session.add(existing)
    else:
        sku_size = SKUSize(sku=req.sku, size=req.size)
        session.add(sku_size)
    
    session.commit()
    session.refresh(existing or sku_size)
    return existing or sku_size

@app.get("/nike/sku/{sku}")
def get_sku_size(sku: str, session: Session = Depends(get_session)):
    """Obtiene la talla asociada a un SKU"""
    sku_mapping = session.exec(select(SKUSize).where(SKUSize.sku == sku)).first()
    if not sku_mapping:
        raise HTTPException(status_code=404, detail=f"SKU {sku} no configurado")
    return {"sku": sku_mapping.sku, "size": sku_mapping.size}

@app.post("/nike/add-to-cart")
def nike_add_to_cart(req: NikeAddToCartRequest, session: Session = Depends(get_session)):
    """
    Agrega un producto al carrito de Nike
    
    El proceso:
    1. Abre el navegador con la URL del producto
    2. Busca el SKU en la URL
    3. Obtiene la talla asociada
    4. Agrega al carrito
    5. Navega a checkout
    6. Se detiene en Fintoc para que completes manualmente
    """
    try:
        # Extraer SKU de la URL (soporta dos formatos)
        import re
        
        # Formato 1: /products/SKU
        match = re.search(r'/products/(\d+)', req.url)
        if match:
            sku = match.group(1)
        else:
            # Formato 2: ?skuId=SKU
            match = re.search(r'skuId=(\d+)', req.url)
            if match:
                sku = match.group(1)
            else:
                raise HTTPException(status_code=400, detail="URL inválida - No contiene SKU (/products/SKU o ?skuId=SKU)")
        
        # Obtener talla del SKU
        sku_mapping = session.exec(select(SKUSize).where(SKUSize.sku == sku)).first()
        if not sku_mapping:
            raise HTTPException(status_code=404, detail=f"SKU {sku} no configurado. Primero agrega con POST /nike/sku/add")
        
        size = sku_mapping.size
        
        # Inicializar bot y agregar al carrito
        bot = NikeBot(headless=req.headless)
        success = bot.add_to_cart(req.url, size)
        
        if not success:
            bot.close()
            raise HTTPException(status_code=500, detail="Error al agregar al carrito")
        
        # Mantener navegador abierto para que usuario complete pago
        bot.keep_open()
        
        return {
            "status": "success",
            "message": "Producto agregado al carrito. Completa el pago en Fintoc manualmente.",
            "sku": sku,
            "size": size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nike/scrape", response_model=NikeProductResponse)
def scrape_nike_product(req: NikeProductRequest, session: Session = Depends(get_session)):
    """
    Scrappea un producto de Nike.cl usando BeautifulSoup
    
    Extrae: SKU, nombre, precio, tallas disponibles, imagen
    Guarda en BD para consulta posterior
    """
    try:
        # Scrappear producto
        scraper = NikeScraper()
        product = scraper.scrape_product(req.url)
        
        if not product:
            raise HTTPException(status_code=400, detail="Error al scrappear el producto. Verifica la URL.")
        
        # Guardar en BD (o actualizar si existe)
        existing = session.exec(select(NikeProduct).where(NikeProduct.sku == product['sku'])).first()
        
        if existing:
            # Actualizar
            existing.name = product['name']
            existing.price = product['price']
            existing.sizes = str(product['sizes'])  # Convertir lista a string JSON
            existing.image = product['image']
            existing.url = product['url']
            existing.updated_at = datetime.utcnow()
            session.add(existing)
        else:
            # Crear nuevo
            nike_prod = NikeProduct(
                sku=product['sku'],
                name=product['name'],
                price=product['price'],
                sizes=str(product['sizes']),
                image=product['image'],
                url=product['url']
            )
            session.add(nike_prod)
        
        session.commit()
        
        # Retornar en formato response
        return NikeProductResponse(
            sku=product['sku'],
            name=product['name'],
            price=product['price'],
            sizes=product['sizes'],
            image=product['image'],
            url=product['url']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scrappearing: {str(e)}")

@app.get("/nike/products")
def get_nike_products(session: Session = Depends(get_session), sku: Optional[str] = None):
    """
    Lista todos los productos scrapeados
    
    Parámetros:
    - sku (opcional): Filtrar por SKU específico
    """
    try:
        if sku:
            products = session.exec(select(NikeProduct).where(NikeProduct.sku == sku)).first()
            if not products:
                raise HTTPException(status_code=404, detail=f"SKU {sku} no encontrado")
            return [products]
        else:
            products = session.exec(select(NikeProduct).order_by(NikeProduct.created_at.desc())).all()
            return products
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
