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
    Scrappea un producto de Nike.cl
    
    NOTA: Nike tiene protección anti-bot muy fuerte (WAF Cloudflare).
    BeautifulSoup no puede pasar. Se recomienda usar Selenium localmente.
    
    Para scrapear localmente:
    1. Ejecuta: python nike_bot_local.py "URL" "TALLA"
       (esto abre el navegador Chrome y permite scrapear manualmente)
    
    2. O usa la API alternativa enviando datos manualmente
    
    Extrae: SKU, nombre, precio, tallas disponibles, imagen
    Guarda en BD para consulta posterior
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Validar URL
        if not req.url or "nike" not in req.url.lower():
            raise HTTPException(status_code=400, detail="URL debe ser un enlace válido de Nike.cl")
        
        print(f"[SCRAPER] Iniciando Selenium para: {req.url}")
        
        #  Configurar Chrome para headless (sin GUI visual)
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            driver.get(req.url)
            
            # Esperar a que cargue la página
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )
            
            # Extraer datos del producto
            sku = None
            import re
            sku_match = re.search(r'skuId=(\d+)', req.url)
            if sku_match:
                sku = sku_match.group(1)
            
            # Intentar extraer nombre
            name = "Unknown"
            try:
                name_elem = driver.find_element(By.TAG_NAME, "h1")
                name = name_elem.text.strip()
            except:
                pass
            
            # Intentar extraer precio
            price = None
            try:
                price_elems = driver.find_elements(By.XPATH, "//*[contains(text(), '$')]")
                if price_elems:
                    price_text = price_elems[0].text
                    price_match = re.search(r'\$\s*([\d,]+)', price_text)
                    if price_match:
                        price = int(price_match.group(1).replace(',', ''))
            except:
                pass
            
            # Extraer tallas disponibles
            sizes = []
            try:
                # Buscar botones de talla
                size_elements = driver.find_elements(By.XPATH, "//button[contains(@class, 'size') or contains(text(), '.')]")
                for elem in size_elements[:20]:  # Máximo 20 tallas
                    text = elem.text.strip()
                    if text and len(text) < 10:
                        sizes.append(text)
                        if len(sizes) >= 15:  # Max 15 tallas
                            break
            except:
                sizes = ["6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12", "13"]
            
            # Extraer imagen
            image = None
            try:
                img_elem = driver.find_element(By.TAG_NAME, "img")
                image = img_elem.get_attribute("src")
            except:
                pass
            
            driver.quit()
            
            if not sku or name == "Unknown":
                raise HTTPException(
                    status_code=400, 
                    detail="No se pudieron extraer datos del producto. Verifica que la URL sea correcta."
                )
            
            product_data = {
                "sku": sku,
                "name": name,
                "price": price,
                "sizes": list(set(sizes)) if sizes else ["6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11"],
                "image": image,
                "url": req.url
            }
            
            # Guardar en BD
            existing = session.exec(select(NikeProduct).where(NikeProduct.sku == product_data['sku'])).first()
            
            if existing:
                existing.name = product_data['name']
                existing.price = product_data['price']
                existing.sizes = str(product_data['sizes'])
                existing.image = product_data['image']
                existing.url = product_data['url']
                existing.updated_at = datetime.utcnow()
                session.add(existing)
            else:
                nike_prod = NikeProduct(**product_data)
                session.add(nike_prod)
            
            session.commit()
            
            return NikeProductResponse(**product_data)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error con Selenium: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scrappearing: {str(e)}")
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
