import importlib
import inspect
from typing import NewType

def type_to_repr(obj):
    return obj.__module__ + ':' + obj.__name__

class StringRegistrationRecord:
    def __init__(self, string):
        self._dependencies = None
        self.record = string

    def _initialize(self):
        package, classname = self.record.split(':')
        package = importlib.import_module(package)
        class_obj = getattr(package, classname)
        spec = inspect.getfullargspec(class_obj)
        self._dependencies = { key: type_to_repr(val) for key, val in spec.annotations.items() }
        self._factory = lambda kwargs: class_obj(**kwargs)
        
    @property
    def dependencies(self):
        if self._dependencies is None:
            self._initialize()
            
        return self._dependencies

    @property
    def factory(self):
        if self._factory is None:
            self._initialize()
            
        return self._factory


class LambdaRegistrationRecord:
    def __init__(self, obj):
        self._dependencies = None
        self.obj = obj

    def _initialize(self):
        class_obj = self.obj
        spec = inspect.getfullargspec(class_obj)
        self._dependencies = { key: type_to_repr(val) for key, val in spec.annotations.items() }
        self._factory = lambda kwargs: class_obj(**kwargs)
        
    @property
    def dependencies(self):
        if self._dependencies is None:
            self._initialize()
            
        return self._dependencies

    @property
    def factory(self):
        if self._factory is None:
            self._initialize()
            
        return self._factory

class ScopedDictionary:
    def __init__(self, global_dict, parent_dict, scoped_dict):
        self.parent_dict = parent_dict
        self.scoped_dict = scoped_dict

        self.global_dict = global_dict

    def __contains__(self, key):
        return key in self.parent_dict or key in self.scoped_dict

    def __getitem__(self, key):
        if key in self.scoped_dict:
            return self.scoped_dict[key]

        return self.parent_dict[key]

    def __setitem__(self, key, value):
        self.scoped_dict[key] = value

    def set_global(self, key, value):
        self.global_dict[key] = value

    def __delitem__(self, key):
        del self.scoped_dict[key]

    def __iter__(self):
        for x in self.parent_dict:
            yield x
        for x in self.scoped_dict:
            yield x

class Provider:
    def __init__(self, registry, container):
        self._registry = registry
        self._scoped_container = container
        self._lookup = self._create_lookup(self._registry)

    def _create_lookup(self, registry):
        lookup = dict()
        for k in registry.keys():
            simplekey = k
            if ':' in simplekey:
                simplekey = simplekey.split(':')[1]

            if simplekey in lookup:
                del lookup[simplekey]
            else:
                lookup[simplekey] = k
        return lookup

    def create(self, typename):
        if isinstance(typename, type):
            typename = type_to_repr(typename)
        elif isinstance(typename, str): 
            if typename in self._lookup:
                typename = self._lookup[typename]

        else:
            raise NotImplementedError()

        record = self._registry.get(typename)
        if (record.lifetime == Lifetime.singleton or record.lifetime == Lifetime.scoped) and \
            typename in self._scoped_container:
            return self._scoped_container[typename]
        
        instance_dependencies = { key: self.create(value) for key, value in record.dependencies.items() }
        instance = record.factory(instance_dependencies)
        if record.lifetime == Lifetime.singleton:
            self._scoped_container.set_global(typename, instance)
        elif record.lifetime == Lifetime.scoped:
            self._scoped_container[typename] = instance
        return instance

    def scope(self):
        return Provider(self._registry, ScopedDictionary(self._scoped_container, self._scoped_container, dict()))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

class Lifetime:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Lifetime) and other.name == self.name

Lifetime.transient = Lifetime('transient')
Lifetime.singleton = Lifetime('singleton')
Lifetime.scoped = Lifetime('scoped')

class Container:
    def __init__(self):
        self._registry = {}
        self._global_container = {}

    def register(self, typename, value = None, lifetime = Lifetime.transient):
        if value is None:
            value = typename

        registration_key = None
        record = None
        if isinstance(typename, str):
            registration_key = typename
        elif isinstance(typename, type):
            registration_key = type_to_repr(typename)
        else:
            raise NotImplementedError()

        if isinstance(value, str):
            record = StringRegistrationRecord(value)
        elif isinstance(value, type):
            if hasattr(value.__module__, value.__name__):
                record = StringRegistrationRecord(type_to_repr(value))
            else:
                record = LambdaRegistrationRecord(value)
        elif callable(value):
            record = LambdaRegistrationRecord(value)

        self._registry[registration_key] = record
        record.lifetime = lifetime

        def register_finalizer(service):
            self.register(typename, service, lifetime=lifetime)
            return service
        return register_finalizer

    def create_provider(self):
        return Provider(self._registry, self._global_container)


container = Container()
