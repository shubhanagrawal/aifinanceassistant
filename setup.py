from setuptools import setup, find_packages

setup(
    name="ai-finance-assistant",
    version="0.1.0",
    description="AI Finance Research Assistant",
    author="Shubhan Agrawal",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "streamlit",
        "pandas",
        "numpy",
        "yfinance",
        "nsepy",
        "requests",
        "python-dotenv",
        "pydantic",
        "loguru"
    ],
    python_requires=">=3.9",
)
