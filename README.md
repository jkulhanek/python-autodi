# Simple Dependency Injection for Python 3.6+
Type-based DI container for Python.

## Introduction
AutoDI is a simple dependency injection container for python. Install it by running:
```
python3 -m pip install autodi
```

## Concepts
The main entrypoint is the `Container` class. There is a default container created when you import the package called `container`. The container class allows you to register your classes so that they can be instantiated in the future. Container itself cannot create any service instances. It is there only to register your services. To create new instances, you need to create a `Provider` first. Look at the next example:

```
from autodi import container

class Service:
  def __init__(self):
    pass
    
# The service is now registered in the container
container.register(Service)

# Creates a new provider
provider = container.create_provider()

# Resolves the service instance from the container
service = provider.create(Service)
```

The default lifetime for all services is `transient`. It means a new instance is created with each call. There are two other options: `singleton`, `scoped`.

The service dependencies are dynamically resolved using type annotations.
```
from autodi import container

class Service:
  def __init__(self):
    pass
    
class ComplexService:
  def __init__(self, simple: Service):
    self.simple = simple
    
# Both services now registered in the container
container.register(Service)
container.register(ComplexService)

# Creates a new provider
provider = container.create_provider()

# Resolves the service instance from the container
service = provider.create(ComplexService)

# service.simple is now a new Service instance
```

## Registration
There are several ways how to register a new service.

#### By strong name
You can register a service by its strong name. It is in the form "<module name>:<class name>". You can register the service as its own implementation or you can bind it to an interface:
```
container.register("my_package:ServiceInterface", "my_package:ServiceImpl")
```
or simply by:
```
container.register("my_package:ServiceImpl")
```
  
#### By type
You can register the service as its own implementation or you can bind it to an interface:
```
container.register(my_package:ServiceInterface, my_package:ServiceImpl)
```
or simply by:
```
container.register(my_package:ServiceImpl)
```

#### As a factory
You can register your own factory that will create your service:
```
def create_service(other: SimpleDependency):
  return Service(other, "some argument")
  
container.register(my_package:ServiceInterface, create_service)
```

#### Using decorator
You can use decorator to register your class to the default container:
```
from autodi import container

@container.register
class Service:
  def __init__(self, x: Dependency):
    self.dependency = x

```

or as an interface implementation:
```
from autodi import container

class Interface:
  def __init__(self):
    pass
    
@container.register(Interface)
class Service(Interface):
  def __init__(self, x: Dependency):
    self.dependency = x
    
service = container.create_provider().create(Interface)
```

You can specify the lifetime type by another parameter to the registration call
```
from autodi import container, Lifetime
container.register("my_package:Service", lifetime = Lifetime.singleton)
```

## Scoping
Scoping is supported by the container. It is a simple way how to create a new service for each http request for example.

```
from autodi import container, Lifetime
class HttpRequestService:
  def __init__(self):
    pass

container.register(HttpRequestService, Lifetime.scoped)
provider = container.create_provider()

# When handling requests
with provider.scope() as s:
  service = s.create(HttpRequestService)
 
```
