cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="ecommerce-analytics-dashboard",
    version="1.0.0",
    author="Rousan Ali",
    author_email="rousan.ali.it@gmail.com",
    description="E-Commerce Analytics Dashboard with Python, Power BI, and SQL",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/89184/E-Commerce-Analytics-Dashboard",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "pyyaml>=6.0",
        "openpyxl>=3.1.0",
        "streamlit>=1.22.0",
        "plotly>=5.14.0",
        "jupyter>=1.0.0",
        "pytest>=7.0.0",
    ],
)
EOF