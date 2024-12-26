from setuptools import setup, find_packages

setup(
    name="nb-fast-gen",
    version="0.1.0",
    description="A CLI tool for generating Python project structures and FastAPI models/schemas.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Nobparat Bunchalor",
    author_email="nobparat.bun@gmail.com",
    url="https://github.com/TeryNobparat/cli-project-generator.git",
    packages=find_packages(),
    py_modules=["cli_project_generator"],
    install_requires=[
        "sqlalchemy",
        "pydantic",
        "fastapi",
        "uvicorn",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "nb=cli_project_generator:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
