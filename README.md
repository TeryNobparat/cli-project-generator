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


## License
This project is licensed under the MIT License.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contact
For any inquiries or issues, please contact [Your Name] at [Your Email].

