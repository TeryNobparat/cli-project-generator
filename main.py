import os
import argparse
import subprocess
from app.feature import FeatureManager

REQUIRED_LIBS = {
    "add-auth": ["fastapi", "pyjwt", "passlib[bcrypt]", "python-multipart"],
    "add-docker": [],
    "add-websocket": ["fastapi"],
    "add-graphql": ["fastapi", "strawberry-graphql"],
    "add-grpc": ["fastapi", "grpcio", "grpcio-tools"],
    "gen ms": ["fastapi", "sqlalchemy", "pydantic"]
}

def install_requirements(command):
    """ ตรวจสอบและติดตั้ง dependencies ที่จำเป็น """
    missing_libs = [lib for lib in REQUIRED_LIBS.get(command, []) if not is_installed(lib)]

    if missing_libs:
        user_input = input(f"📌 ต้องการติดตั้ง {', '.join(missing_libs)} หรือไม่? (y/n): ").strip().lower()
        if user_input == "y":
            subprocess.run(["pip", "install"] + missing_libs)
            print("✅ ติดตั้ง dependencies เรียบร้อยแล้ว!")
        else:
            print("⚠️ บางฟีเจอร์อาจทำงานไม่ได้เนื่องจาก dependencies ไม่ครบ!")

def is_installed(lib):
    """ ตรวจสอบว่าแพ็กเกจติดตั้งแล้วหรือยัง """
    try:
        __import__(lib)
        return True
    except ImportError:
        return False

def main():
    parser = argparse.ArgumentParser(description="CLI tool for project generation.")
    parser.add_argument("command", type=str, help="Command to execute (e.g., create, gen ms, add-auth, etc.)")
    parser.add_argument("--table", type=str, help="Table name for generating models and schemas.")
    parser.add_argument("--name", type=str, help="Custom filename for models, schemas, CRUD, and router.")
    args = parser.parse_args()

    if args.command in REQUIRED_LIBS:
        install_requirements(args.command)

    if args.command == "gen ms":
        if not args.table or not args.name:
            print("❌ Error: ต้องระบุ `--table` และ `--name` สำหรับ `gen ms`")
            return
        output_dir = os.getenv('ROOT_PATH', os.getcwd())
        FeatureManager.generate_models_and_schemas(args.table, output_dir, args.name)

    elif args.command == "add-auth":
        FeatureManager.add_auth(os.getenv('ROOT_PATH', os.getcwd()))

    elif args.command == "add-docker":
        FeatureManager.add_docker(os.getenv('ROOT_PATH', os.getcwd()))

    elif args.command == "add-websocket":
        FeatureManager.add_websocket(os.getenv('ROOT_PATH', os.getcwd()))

    elif args.command == "add-graphql":
        FeatureManager.add_graphql(os.getenv('ROOT_PATH', os.getcwd()))

    elif args.command == "add-grpc":
        FeatureManager.add_grpc(os.getenv('ROOT_PATH', os.getcwd()))

    else:
        print("⚠️ คำสั่งไม่ถูกต้อง! ใช้ 'create', 'gen ms', 'add-auth', 'add-docker', 'add-websocket', 'add-graphql', หรือ 'add-grpc'.")

if __name__ == "__main__":
    main()