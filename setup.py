import setuptools

setuptools.setup(
    name="thiefringer",
    version="0.0.2",
    author="KyuzoM",
    author_email="99549950+kyuzom@users.noreply.github.com",
    description="ThiefRinger alarm system",
    long_description="ThiefRinger alarm system - Onion Omega specific python package, motion detection, SMS notification.",
    url="https://github.com/kyuzom/thiefringer",
    license="MIT",
    packages=[
        "thiefringer",
    ],
    package_data={
        "thiefringer": ["**/*"],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=2.7",
)
