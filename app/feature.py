import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import subprocess

Base = declarative_base()

# Load environment variables
load_dotenv()

class FeatureManager:
    
    @staticmethod
    def get_database_url(db_type="sqlite"):
        """ ดึง URL ของฐานข้อมูลจากประเภทที่เลือก """
        database_urls = {
            "sqlite": "sqlite:///./test.db",
            "postgresql": "postgresql://user:password@localhost/dbname",
            "mysql": "mysql://user:password@localhost/dbname",
            "mssql": "mssql+pyodbc://user:password@localhost/dbname",
            "oracle": "oracle://user:password@localhost/dbname",
        }
        return database_urls.get(db_type, None)

    @staticmethod
    def create_file(file_path, content=""):
        """ สร้างไฟล์พร้อมเนื้อหา """
        with open(file_path, "w") as f:
            f.write(content)

    @staticmethod
    def create_structure(base_path, structure):
        """ สร้างโครงสร้างโฟลเดอร์และไฟล์ """
        for key, value in structure.items():
            path = os.path.join(base_path, key)
            if isinstance(value, dict):  
                os.makedirs(path, exist_ok=True)
                FeatureManager.create_structure(path, value)
            else:  
                FeatureManager.create_file(path, value)

    @staticmethod
    def generate_env_file(db_type, project_path):
        """ สร้างไฟล์ .env สำหรับกำหนดค่า DATABASE_URL """
        database_url = FeatureManager.get_database_url(db_type)
        if database_url is None:
            print(f"❌ Error: Unsupported database type '{db_type}'.")
            return
        
        env_content = f"APP_ENV=development\nDATABASE_URL={database_url}"
        FeatureManager.create_file(os.path.join(project_path, ".env"), env_content)

    @staticmethod
    def generate_core_files(base_path):
        """ สร้างไฟล์ config.py และ database.py """
        core_files = {
            "app/core/config.py": """
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
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
            """,
            "app/core/database.py": """
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
        }

        for file_path, content in core_files.items():
            full_path = os.path.join(base_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            FeatureManager.create_file(full_path, content)

    @staticmethod
    def generate_api_files(base_path):
        """ สร้างไฟล์ Router และ API """
        api_files = {
            "app/api/routers/router.py": """
from fastapi import APIRouter
from app.api.routers import users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/auth", tags=["auth"])


            """,
            "app/api/routers/users.py": """
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.auth import create_access_token, hash_password, verify_password, get_current_user
from datetime import timedelta

router = APIRouter()

fake_users_db = {"admin": {"username": "admin", "hashed_password": hash_password("password")}}

@router.post("/register")
def register(username: str, password: str):
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    fake_users_db[username] = {"username": username, "hashed_password": hash_password(password)}
    return {"msg": "User registered successfully"}

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user["user_id"]}
            """
        }

        for file_path, content in api_files.items():
            full_path = os.path.join(base_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            FeatureManager.create_file(full_path, content)

    @staticmethod
    def generate_main_file(base_path):
        """ สร้างไฟล์ main.py """
        main_content = """
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
        """
        FeatureManager.create_file(os.path.join(base_path, "main.py"), main_content)


    @staticmethod
    def add_auth(base_path):
        """เพิ่มระบบ JWT Authentication"""
        auth_files = {
            "app/core/auth.py": """
import os
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"user_id": user_id}
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
            """,
            "app/api/routers/users.py": """
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.auth import create_access_token, hash_password, verify_password, get_current_user
from datetime import timedelta

router = APIRouter()

fake_users_db = {"admin": {"username": "admin", "hashed_password": hash_password("password")}}

@router.post("/register")
def register(username: str, password: str):
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    fake_users_db[username] = {"username": username, "hashed_password": hash_password(password)}
    return {"msg": "User registered successfully"}

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user["user_id"]}
            """
        }

        for file_path, content in auth_files.items():
            full_path = os.path.join(base_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            FeatureManager.create_file(full_path, content)

        print("✅ Authentication added successfully!")

    @staticmethod
    def add_docker(base_path):
        """เพิ่มไฟล์ Docker ให้โปรเจค"""
        docker_files = {
            "Dockerfile": """
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
            """,
            ".dockerignore": """
__pycache__/
.env
*.pyc
*.pyo
*.pyd
migrations/
            """,
            "docker-compose.yml": """
version: '3.8'

services:
  backend:
    build: .
    container_name: fastapi_app
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file:
      - .env

  db:
    image: postgres:15
    container_name: postgres_db
    restart: always
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydatabase
            """
        }

        for file_path, content in docker_files.items():
            full_path = os.path.join(base_path, file_path)
            FeatureManager.create_file(full_path, content)

        print("✅ Docker support added successfully!")


    @staticmethod
    def add_websocket(base_path):
        """ เพิ่ม WebSocket support ให้โปรเจค """
        websocket_files = {
            "app/api/routers/websocket.py": """
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

connected_clients = []

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in connected_clients:
                await client.send_text(f"Message from server: {data}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
            """
        }

        for file_path, content in websocket_files.items():
            full_path = os.path.join(base_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            FeatureManager.create_file(full_path, content)

        print("✅ WebSocket support added successfully!")

    @staticmethod
    def add_graphql(base_path):
        """ เพิ่ม GraphQL API ให้โปรเจค """
        graphql_files = {
            "app/api/routers/graphql.py": """
import strawberry
from fastapi import APIRouter
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, GraphQL!"

schema = strawberry.Schema(query=Query)
graphql_router = GraphQLRouter(schema)

router = APIRouter()
router.include_router(graphql_router, prefix="/graphql")
            """
        }

        for file_path, content in graphql_files.items():
            full_path = os.path.join(base_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            FeatureManager.create_file(full_path, content)

        print("✅ GraphQL support added successfully!")

    @staticmethod
    def add_grpc(base_path):
        """ เพิ่ม gRPC Server และ Client """
        grpc_files = {
            "app/grpc/service.proto": """
syntax = "proto3";

package grpcservice;

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply);
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
            """,
            "app/grpc/server.py": """
import grpc
from concurrent import futures
import app.grpc.service_pb2 as service_pb2
import app.grpc.service_pb2_grpc as service_pb2_grpc

class Greeter(service_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        return service_pb2.HelloReply(message=f"Hello, {request.name}!")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("✅ gRPC Server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
            """,
            "app/grpc/client.py": """
import grpc
import app.grpc.service_pb2 as service_pb2
import app.grpc.service_pb2_grpc as service_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = service_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(service_pb2.HelloRequest(name="Nopparat"))
        print(f"✅ Response from server: {response.message}")

if __name__ == "__main__":
    run()
            """
        }

        for file_path, content in grpc_files.items():
            full_path = os.path.join(base_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            FeatureManager.create_file(full_path, content)

        print("✅ gRPC support added successfully!")

    @staticmethod
    def generate_project(base_path, project_name, db_type="sqlite"):
        """ สร้างโปรเจคทั้งหมด """
        project_path = os.path.join(base_path, project_name)

        # สร้างโครงสร้างโฟลเดอร์
        project_structure = {
            "backend": {
                "app": {
                    "api": {"routers": {}},
                    "core": {},
                    "crud": {},
                    "db": {},
                    "models": {},
                    "schemas": {},
                },
                "tests": {}
            }
        }
        FeatureManager.create_structure(project_path, project_structure)

        # สร้างไฟล์หลัก
        FeatureManager.generate_env_file(db_type, project_path)
        FeatureManager.generate_core_files(project_path)
        FeatureManager.generate_api_files(project_path)
        FeatureManager.generate_main_file(project_path)
        FeatureManager.add_auth(project_path)

        print(f"✅ Project '{project_name}' created with {db_type} database at {project_path}")

    @staticmethod
    def map_sqlalchemy_to_python(sqlalchemy_type):
        mapping = {
            'INTEGER': 'int',
            'TEXT': 'str',
            'VARCHAR': 'str',
            'FLOAT': 'float',
            'BOOLEAN': 'bool',
        }
        return mapping.get(sqlalchemy_type.upper(), 'str')

    @staticmethod
    def get_table_columns(engine, table_name):
        inspector = inspect(engine)
        columns_info = []
        for column in inspector.get_columns(table_name):
            columns_info.append({
                'name': column['name'],
                'type': str(column['type']),
                'python_type': FeatureManager.map_sqlalchemy_to_python(str(column['type']))
            })
        return columns_info

    @staticmethod
    def generate_model(table_name, columns, name):
        fields = "\n".join([f"    {col['name']} = Column({col['type']})" for col in columns])
        model_template = f"""
    class {name.capitalize()}(Base):
        __tablename__ = '{table_name}'
    {fields}
        """
        return model_template
    
    @staticmethod
    def generate_schema(table_name, columns, name):
        fields = "\n".join([f"    {col['name']}: {col['python_type']}" for col in columns])
        schema_template = f"""
    class {name.capitalize()}Schema(BaseModel):
    {fields}

        class Config:
            orm_mode = True
        """
        return schema_template

    @staticmethod
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

        FeatureManager.create_file(crud_file, crud_code)
        FeatureManager.create_file(router_file, router_code)

        router_update_path = os.path.join(output_dir, "api", "routers", "router.py")
        with open(router_update_path, "a") as router_update_file:
            router_update_file.write(f"api_router.include_router({filename}.router,prefix=\"/{filename}\",tags=[\"{filename}\"])")

    @staticmethod
    def generate_models_and_schemas(table_name, output_dir, name):
        database_url = FeatureManager.get_database_url()
        if not database_url:
            print("Error: DATABASE_URL is not set in the .env file.")
            return
        engine = create_engine(database_url)
        columns = FeatureManager.get_table_columns(engine, table_name)
        model_code = FeatureManager.generate_model(table_name, columns, name)
        schema_code = FeatureManager.generate_schema(table_name, columns, name)

        models_dir = os.path.join(output_dir, "models")
        schemas_dir = os.path.join(output_dir, "schemas")
        os.makedirs(models_dir, exist_ok=True)
        os.makedirs(schemas_dir, exist_ok=True)

        with open(os.path.join(models_dir, f"{name}.py"), "w") as model_file:
            model_file.write(model_code)

        with open(os.path.join(schemas_dir, f"{name}_schema.py"), "w") as schema_file:
            schema_file.write(schema_code)

        FeatureManager.generate_crud_and_router(output_dir, name)

        print(f"Model, schema, CRUD, and router for '{name}' generated in {output_dir}")


    @staticmethod
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

    @staticmethod
    def init_alembic():
        """Initialize Alembic migration"""
        if not os.path.exists("alembic.ini"):
            subprocess.run(["alembic", "init", "migrations"])
            print("✅ Alembic initialized!")
        else:
            print("⚠️ Alembic already initialized.")

    @staticmethod
    def run_migrations():
        """Run Alembic migrations (generate & upgrade)"""
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"])
        subprocess.run(["alembic", "upgrade", "head"])
        print("✅ Database migrated successfully!")