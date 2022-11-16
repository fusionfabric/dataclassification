import setuptools

from dataclassification import __version__

with open("README.md", encoding="utf8") as readme_file:
    readme = readme_file.read()

requirements = ["pandas>=1.4.3", "openpyxl>=3.0.10", "xlsxwriter>=3.0.3"]


def setup_package():
    setuptools.setup(
        name="dataclassification",
        version=__version__,
        author="Amiket Kumar Srivastava",
        author_email="amiket.kumarsrivastava@finastra.com",
        description="A python package to classify API swaggers and datasets.",
        long_description_content_type="text/markdown",
        url="https://github.com/fusionfabric/dataclassification",
        packages=setuptools.find_packages(),
        install_requires=requirements,
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires=">=3.7",
        long_description=readme,
        options={"console_scripts": {"dataclassification": "dataclassification:main"}},
    )


if __name__ == "__main__":
    setup_package()
