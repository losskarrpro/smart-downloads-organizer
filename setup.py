from setuptools import setup, find_packages

setup(
    name="smart-downloads-organizer",
    version="1.0.0",
    author="Smart Downloads Team",
    author_email="contact@example.com",
    description="Smart Downloads Organizer - Daemon to auto-organize Downloads folder",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/smart-downloads-organizer",
    packages=find_packages(),
    package_data={
        '': [
            'config.json',
            'templates/*.html',
            'static/css/*.css',
            'static/js/*.js',
            'database/*.sql',
            'docs/*.md'
        ]
    },
    include_package_data=True,
    install_requires=[
        'watchdog>=3.0.0',
        'Flask>=2.3.0',
        'python-dateutil>=2.8.0'
    ],
    entry_points={
        'console_scripts': [
            'smart-downloads-organizer=organizer:main',
            'smart-downloads-web=web_interface:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)