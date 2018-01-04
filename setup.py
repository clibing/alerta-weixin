
from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name="alerta-weixin",
    version=version,
    description='Alerta plugin for weixin push',
    url='https://github.com/clibing/alerta-weixin.git',
    license='MIT',
    author='clibing',
    author_email='wmsjhappy@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_weixin'],
    install_requires=[
        'datetime',
        'pytz',
        'os',
        'json',
        'requests',
        'logging'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'weixin =alerta_weixin:WeixinPush'
        ]
    }
)
