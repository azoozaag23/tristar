from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="tristar",
    version="1.0.0",
    description="Custom ERPNext App for TriStar Technical Company - Dammam, Saudi Arabia",
    author="TriStar Technical Company",
    author_email="info@tristartech.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
