from distutils.core import setup, Extension

module1 = Extension('matcher',
                    sources = ['Example.cpp', 'BinaryHeap.cpp', 'Matching.cpp', 'Graph.cpp'])

setup (name = 'matcher',
       version = '1.0',
       description = '',
       ext_modules = [module1])
