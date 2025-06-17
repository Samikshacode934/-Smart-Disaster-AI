from setuptools import setup, find_packages

setup(
    name="disaster_ai",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        'flask',
        'pymongo',
        'python-dotenv',
        'tensorflow',
        'transformers'
    ],
    python_requires='>=3.8',
)