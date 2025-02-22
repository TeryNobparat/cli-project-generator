import os
import argparse
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import subprocess

Base = declarative_base()

# Load environment variables
load_dotenv()

def get_database_url():
    return os.getenv("DATABASE_URL")

# ฟังก์ชันสำหรับสร้างไฟล์และใส่เนื้อหา
def create_file(file_path, content=""):
    with open(file_path, "w") as f:
        f.write(content)

# ฟังก์ชันสร้างโครงสร้าง
def create_structure(base_path, structure):
    for key, value in structure.items():
        path = os.path.join(base_path, key)
        if isinstance(value, dict):  
            os.makedirs(path, exist_ok=True)
            create_structure(path, value)
        else:  
            create_file(path, value)

def generate_project(base_path, project_name,db_type = "sqlite"):
    database_urls = {
        "sqlite": "sqlite:///./test.db",
        "postgresql": "postgresql://user:password@localhost/dbname",
        "mysql": "mysql://user:password@localhost/dbname",
        "mssql": "mssql+pyodbc://user:password@localhost/dbname",
        "oracle": "oracle://user:password@localhost/dbname",
    }

    if db_type not in database_urls:
        print(f"Error: Unsupported database type '{db_type}'. Use ''sqlite', 'postgresql', 'mysql', 'mssql', or 'oracle'.")
        return

    project_structure = {
        project_name: {
            "backend": {
                "app": {
                    "api": {
                        "routers": {
                            "router.py": 
"""
from fastapi import APIRouter

from app.api.routers import ticket, coin

api_router = APIRouter()

api_router.include_router(ticket.hello_world, prefix="/hello", tags=["hello"])
""",
                            "hello_world.py":
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db

router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}
"""
                            
                        },
                        "dependencies.py": 
                            """
from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
                            """
                    },
                    "core": {
                        "config.py": 
                            """
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

class Settings(BaseSettings):
    APP_NAME: str = "My FastAPI Application"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    class Config:
        env_file = ".env"

settings = Settings()

# ตรวจสอบประเภทฐานข้อมูล
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}  # สำหรับ SQLite
else:
    connect_args = {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
                            """,
                        "database.py": 
                            """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "My FastAPI Application"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["*"]  
    DATABASE_URL: str  

    class Config:
        env_file = ".env"

settings = Settings()
                            """
                    },
                    "crud": {},
                    "db": {},
                    "models": {},
                    "schemas": {
                        "user_schema.py":
                            """
from pydantic import BaseModel, EmailStr

class UserSchema(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "johndoe@example.com"
            }
        }
}
                            """
                    },
                },
                "tests": {
                    "test_main.py": "def test_sample():\n    assert 1 + 1 == 2"
                },
                ".env": f"APP_ENV=development\nDATABASE_URL={database_urls[db_type]}",
                "main.py": 
                    """
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routers.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="API Documentation for the FastAPI project",
    version=settings.APP_VERSION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
                    """,
                "README.md": "# Backend for the project\n\nThis is a backend built with FastAPI.",
                "requirements.txt": 
                """
fastapi
sqlalchemy
uvicorn
dotenv
pydantic
pydantic-settings
alembic
"""
            }
        }
    }

    create_structure(base_path, project_structure)
    print(f"✅ Project created with {db_type} database at {base_path}/{project_name}")

def map_sqlalchemy_to_python(sqlalchemy_type):
    mapping = {
        'INTEGER': 'int',
        'TEXT': 'str',
        'VARCHAR': 'str',
        'FLOAT': 'float',
        'BOOLEAN': 'bool',
    }
    return mapping.get(sqlalchemy_type.upper(), 'str')

def get_table_columns(engine, table_name):
    inspector = inspect(engine)
    columns_info = []
    for column in inspector.get_columns(table_name):
        columns_info.append({
            'name': column['name'],
            'type': str(column['type']),
            'python_type': map_sqlalchemy_to_python(str(column['type']))
        })
    return columns_info

def generate_model(table_name, columns, name):
    fields = "\n".join([f"    {col['name']} = Column({col['type']})" for col in columns])
    model_template = f"""
class {name.capitalize()}(Base):
    __tablename__ = '{table_name}'
{fields}
    """
    return model_template

def generate_schema(table_name, columns, name):
    fields = "\n".join([f"    {col['name']}: {col['python_type']}" for col in columns])
    schema_template = f"""
class {name.capitalize()}Schema(BaseModel):
{fields}

    class Config:
        orm_mode = True
    """
    return schema_template

def generate_crud_and_router(output_dir, filename):
    crud_code = f"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import update,and_
from app.models.{filename} import {filename.capitalize()}
from app.schemas.{filename}_schema import {filename.capitalize()}Create, {filename.capitalize()}Update
from app.crud.base import CRUDBase

class CRUD{filename.capitalize()}(CRUDBase[{filename.capitalize()}, {filename.capitalize()}Create, {filename.capitalize()}Update]):
    def __init__(self):
        super().__init__({filename.capitalize()})

    def get_{filename}_all(self, db: Session) -> Optional[{filename.capitalize()}]:
        {filename} = db.query({filename.capitalize()}).all()
        return {filename}
    """

    router_code = f"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.crud.{filename}_crud import CRUD{filename.capitalize()}

router = APIRouter()

crud_{filename} = CRUD{filename.capitalize()}()

@router.get("/{filename}/")
def get_{filename}_all(db: Session = Depends(get_db)):
    {filename} = crud_{filename}.get_{filename}_all(db)
    if not {filename}:
        raise HTTPException(status_code=404, detail="{filename} not found")
    return {filename}
    """

    crud_file = os.path.join(output_dir, "crud", f"{filename}_crud.py")
    router_file = os.path.join(output_dir, "api", "routers", f"{filename}.py")

    create_file(crud_file, crud_code)
    create_file(router_file, router_code)

    router_update_path = os.path.join(output_dir, "api", "routers", "router.py")
    with open(router_update_path, "a") as router_update_file:
        router_update_file.write(f"api_router.include_router({filename}.router,prefix=\"/{filename}\",tags=[\"{filename}\"])")

def generate_models_and_schemas(table_name, output_dir, name):
    database_url = get_database_url()
    if not database_url:
        print("Error: DATABASE_URL is not set in the .env file.")
        return
    engine = create_engine(database_url)
    columns = get_table_columns(engine, table_name)
    model_code = generate_model(table_name, columns, name)
    schema_code = generate_schema(table_name, columns, name)

    models_dir = os.path.join(output_dir, "models")
    schemas_dir = os.path.join(output_dir, "schemas")
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(schemas_dir, exist_ok=True)

    with open(os.path.join(models_dir, f"{name}.py"), "w") as model_file:
        model_file.write(model_code)

    with open(os.path.join(schemas_dir, f"{name}_schema.py"), "w") as schema_file:
        schema_file.write(schema_code)

    generate_crud_and_router(output_dir, name)

    print(f"Model, schema, CRUD, and router for '{name}' generated in {output_dir}")



def generate_api_docs():
    """Export OpenAPI JSON"""
    base_url = "http://127.0.0.1:8000/api/v1/openapi.json"
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            with open("openapi.json", "w") as f:
                f.write(response.text)
            print("✅ API Documentation exported as openapi.json")
        else:
            print("❌ Failed to retrieve API Docs")
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI server is not running. Start the server and try again.")

def init_alembic():
    """Initialize Alembic migration"""
    if not os.path.exists("alembic.ini"):
        subprocess.run(["alembic", "init", "migrations"])
        print("✅ Alembic initialized!")
    else:
        print("⚠️ Alembic already initialized.")

def run_migrations():
    """Run Alembic migrations (generate & upgrade)"""
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"])
    subprocess.run(["alembic", "upgrade", "head"])
    print("✅ Database migrated successfully!")

def main():
    parser = argparse.ArgumentParser(description="CLI tool for project generation.")
    parser.add_argument("command", type=str, help="Command to execute (e.g., create, gen ms)")
    parser.add_argument("project_name", type=str, nargs="?", help="Name of the project to create.")
    parser.add_argument("--table", type=str, help="Table name for generating models and schemas and other files.")
    parser.add_argument("--name", type=str, help="Custom filename for models, schemas, CRUD, and router.")
    args = parser.parse_args()

    if args.command == "create":
        if not args.project_name:
            print("Error: Project name is required for 'create' command.")
            return
        db_type = args.db if args.db else "sqlite"
        generate_project(os.getenv('ROOT_PATH', os.getcwd()), args.project_name, db_type)
    elif args.command == "gen ms":
        if not args.table:
            print("Error: Table name is required for 'gen ms' command.")
            return
        if not args.name:
            print("Error: Custom filename (--name) is required for 'gen ms' command.")
            return
        output_dir = os.getenv('ROOT_PATH', os.getcwd())  # ใช้ ROOT_PATH หรือ current directory
        generate_models_and_schemas(args.table, output_dir, args.name)
    elif args.command == "gen docs":
        generate_api_docs()
    else:
        print("Unsupported command. Use 'create' to create a project or 'gen ms' to generate models and schemas.")

if __name__ == "__main__":
    main()
