from setuptools import setup, find_packages

setup(
    name="fiphopha",
    version="0.2.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "tk",
        "setuptools",
        "openpyxl",
    ], 
    entry_points={
        "console_scripts": [
            "fiphopha=fiphopha.run_fiphopha:main",
        ],
    },
    author="Vasilios Drakopoulos",
    author_email="Vasilios.Drakopoulos@monash.edu",
    description="FiPhoPHA - A fiber photometry Python package for post-hoc analysis",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VasiliDrakopoulos/fiphopha", 
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    license="MIT",  
)
