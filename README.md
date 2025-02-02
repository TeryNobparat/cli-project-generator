# CLI Project Generator

CLI Project Generator is a command-line tool designed to streamline the creation of FastAPI projects. It helps you generate project structures, models, schemas, CRUD logic, and routers based on a predefined pattern, making the process of developing APIs faster and more consistent.

## Features

- **Project Structure Generation**: Create a complete FastAPI project structure with just one command.
- **Models and Schemas**: Automatically generate SQLAlchemy models and Pydantic schemas based on a given database table.
- **CRUD Logic**: Quickly scaffold CRUD operations for your database models.
- **Router Integration**: Generate API routers and automatically register them.
- **Environment Variables**: Leverage `.env` for database configuration.

## Requirements

- Python 3.6+
- `fastapi`
- `sqlalchemy`
- `uvicorn`
- `python-dotenv`

## Installation

1. Clone the repository or download the code.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the CLI tool locally:
   ```bash
   pip install .
   ```

## Usage

### Create a New Project

To generate a new FastAPI project structure:

```bash
nb create <project-name>
```

This will create a project directory named `<project-name>` with a predefined structure.

### Generate Models, Schemas, CRUD, and Router

To generate models, schemas, CRUD, and router for a specific database table:

```bash
nb gen ms --table <table-name> --name <filename>
```

- `--table`: Name of the database table.
- `--name`: Custom name for the files and classes.

Example:

```bash
nb gen ms --table users --name user
```

This command will:

1. Generate `models/user.py`.
2. Generate `schemas/user_schema.py`.
3. Generate `crud/user_crud.py`.
4. Generate `api/routers/user.py`.
5. Update `api/routers/router.py` to include the new router.

### Environment Variables

Ensure you have a `.env` file in the root of your project with the following variable:

```env
DATABASE_URL=sqlite:///./test.db
```

This tool will use `DATABASE_URL` to connect to your database.

## Example Project Structure

After running `nb create my_project`, the generated structure will look like this:

```
my_project/
├── backend/
│   ├── main.py
│   ├── app/
│   │   ├── api/
│   │   │   ├── routers/
│   │   │   │   ├── router.py
│   │   │   │   └── ...
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── crud/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── main.py
│   │   └── dependencies.py
│   ├── tests/
│   │   └── test_main.py
│   ├── .env
│   ├── README.md
│   └── requirements.txt
├── worker/
└── ...
```

# CLI Project Generator

CLI Project Generator เป็นเครื่องมือที่ช่วยสร้างโครงสร้างโปรเจค **FastAPI** พร้อมรองรับ **WebSocket, GraphQL, gRPC, และ Docker**  
รองรับการสร้าง **Models, Schemas, CRUD, และ Router** อัตโนมัติ 🚀

---

## **📌 Features**

✅ **สร้างโครงสร้างโปรเจค FastAPI อัตโนมัติ**  
✅ **สร้าง Models และ Schemas จากฐานข้อมูล**  
✅ **เพิ่ม Authentication (JWT)**  
✅ **รองรับ WebSocket, GraphQL, และ gRPC**  
✅ **รองรับ Docker และ Docker Compose**  
✅ **ติดตั้ง Dependencies อัตโนมัติ**

---

## **📌 คำสั่งที่รองรับ**

| คำสั่ง                                             | คำอธิบาย                                                               |
| -------------------------------------------------- | ---------------------------------------------------------------------- |
| `nb create <project-name> --db <database>`         | สร้างโครงสร้างโปรเจค (รองรับ SQLite, PostgreSQL, MySQL, MSSQL, Oracle) |
| `nb gen ms --table <table-name> --name <filename>` | สร้าง Models, Schemas, CRUD, และ Router                                |
| `nb add-auth`                                      | เพิ่มระบบ JWT Authentication                                           |
| `nb add-docker`                                    | เพิ่ม Docker และ Docker Compose                                        |
| `nb add-websocket`                                 | เพิ่ม WebSocket API                                                    |
| `nb add-graphql`                                   | เพิ่ม GraphQL API                                                      |
| `nb add-grpc`                                      | เพิ่ม gRPC API                                                         |
| `nb migrate init`                                  | สร้าง Alembic Migrations                                               |
| `nb migrate upgrade`                               | อัปเดตฐานข้อมูลด้วย Alembic                                            |
| `nb generate-docs`                                 | Export API Documentation เป็น `openapi.json`                           |

---

## **📌 วิธีติดตั้ง**

1. **ติดตั้งแพ็กเกจ**

   ```bash
   pip install cli_project_generator
   ```

2. **สร้างโปรเจค**

   ```bash
   nb create my_project --db postgresql
   ```

3. **เพิ่ม Authentication**

   ```bash
   nb add-auth
   ```

4. **เพิ่ม WebSocket**

   ```bash
   nb add-websocket
   ```

5. **เพิ่ม GraphQL**

   ```bash
   nb add-graphql
   ```

6. **เพิ่ม gRPC**

   ```bash
   nb add-grpc
   ```

7. **เพิ่ม Docker**

   ```bash
   nb add-docker
   ```

8. **สร้าง Models & Schemas**
   ```bash
   nb gen ms --table users --name user
   ```

---

## **📌 การใช้งาน Docker**

1. **เพิ่ม Docker Support**

   ```bash
   nb add-docker
   ```

2. **รันโปรเจคด้วย Docker Compose**
   ```bash
   docker-compose up --build
   ```

📌 **Swagger UI:** `http://localhost:8000/docs`  
📌 **GraphQL Playground:** `http://localhost:8000/graphql`  
📌 **gRPC Server:** `localhost:50051`

---

## **📌 License**

MIT License  
Developed by **Nopparat**
