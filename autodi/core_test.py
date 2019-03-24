import unittest
from . import core

class DummyNoDependency:
    def __init__(self):
        pass

    def get(self):
        return 'testok'

class DummySingleDependency:
    def __init__(self, other: DummyNoDependency):
        self.other = other
    
    def get(self):
        return self.other.get()

class CoreTestCase(unittest.TestCase):
    def test_createInstanceNoDependencies(self):
        container = core.Container()
        container.register('autodi.core_test:DummyNoDependency')

        provider = container.create_provider()
        obj = provider.create('autodi.core_test:DummyNoDependency')
        self.assertIsInstance(obj, DummyNoDependency)

    def test_createInstanceSimpleName(self):
        container = core.Container()
        container.register('autodi.core_test:DummyNoDependency')

        provider = container.create_provider()
        obj = provider.create('DummyNoDependency')
        self.assertIsInstance(obj, DummyNoDependency)

    def test_createInstanceNoDependenciesUsingType(self):
        container = core.Container()
        container.register(DummyNoDependency)

        provider = container.create_provider()
        obj = provider.create(DummyNoDependency)
        self.assertIsInstance(obj, DummyNoDependency)

    def test_registerFactory(self):
        container = core.Container()
        container.register(DummyNoDependency)
        def func(x: DummyNoDependency):
            return { 'test': x.get() }

        container.register('tested', func)

        provider = container.create_provider()
        obj = provider.create('tested')
        self.assertDictEqual(obj, {'test': 'testok'})

    def test_createInstanceSingleDependencies(self):
        container = core.Container()
        container.register('autodi.core_test:DummyNoDependency')
        container.register('autodi.core_test:DummySingleDependency')

        provider = container.create_provider()
        obj = provider.create('autodi.core_test:DummySingleDependency')
        self.assertIsInstance(obj, DummySingleDependency)

    def test_transient(self):
        container = core.Container()
        container.register(DummyNoDependency)

        provider = container.create_provider()
        obj = provider.create(DummyNoDependency)
        obj.test = 'Valid'

        obj = provider.create(DummyNoDependency)
        self.assertFalse(hasattr(obj, 'test'))

    def test_sigleton(self):
        container = core.Container()
        container.register(DummyNoDependency, lifetime=core.Lifetime.scoped)

        provider = container.create_provider()
        obj = provider.create(DummyNoDependency)
        obj.test = 'Valid'

        obj = provider.create(DummyNoDependency)
        self.assertTrue(hasattr(obj, 'test'))

    def test_scoped(self):
        container = core.Container()
        container.register(DummyNoDependency, lifetime = core.Lifetime.scoped)
        provider = container.create_provider()

        with provider.scope() as s:
            obj = s.create(DummyNoDependency)
            obj.test = 'Valid'
            obj = s.create(DummyNoDependency)
            self.assertTrue(hasattr(obj, 'test'))

            with s.scope() as s1:
                obj = s1.create(DummyNoDependency)
                self.assertTrue(hasattr(obj, 'test'))   

        with provider.scope() as s:
            obj = s.create(DummyNoDependency)
            self.assertFalse(hasattr(obj, 'test'))

if __name__ == '__main__':
    unittest.main()