from setuptools import find_packages, setup


if __name__ == '__main__':
    setup(

        # standard info
        name='titansemail',
        version='0.0.5',
        description='package for mass-sending emails using ms graph api',
        author='Mike Powell PhD',
        author_email='mike@lakeslegendaries.com',

        # longer info
        long_description=open('README.rst').read(),
        license='MIT License',

        # packages to include
        packages=find_packages(),

        # requirements
        install_requires=['numpy', 'pyyaml'],
        python_requires='>=3.9',

        # include MANIFEST.in files
        include_package_data=True,
    )
