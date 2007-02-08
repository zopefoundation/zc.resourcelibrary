from setuptools import setup, find_packages

setup(
    name="zc.resourcelibrary",
    version="0.7dev",
    packages=find_packages('src'),
    
    package_dir= {'':'src'},
    
    namespace_packages=['zc'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },

    zip_safe=False,
    author='Zope Project',
    author_email='zope3-dev@zope.org',
    description="""\
The resource library is a Zope 3 extension that is designed to make the
inclusion of JavaScript, CSS, and other resources easy, cache-friendly,
and component-friendly.
""",
    license='ZPL',
    keywords="zope zope3",
    classifiers = ['Framework :: Zope3'],
    install_requires=['setuptools'],    
    )
