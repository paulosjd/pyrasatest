import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


requires = [
    'pyramid',
    'SQLAlchemy'
]

setuptools.setup(
    name='Pyrasatest',
    version="1.0.2",
    author="Paul Davis",
    author_email="pjdavis@gmx.com",
    license='MIT',
    description="Unit testing utilities for Pyramid applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paulosjd/pyrasatest",
    packages=setuptools.find_packages(),  # ['pyrasatest', ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requires,
)
