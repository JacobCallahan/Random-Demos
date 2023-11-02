import types


def version(cls, version):
    def decorator(new_cls):
        cls._versions[version] = new_cls
        return new_cls
    return decorator


class VersionedClass(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls._versions = {}
        cls.version = classmethod(version)

    def __call__(cls, *args, version=None, **kwargs):
        created = super().__call__(*args, **kwargs)
        if version and (ver_cls := cls._versions.get(version)):
            for attr, obj in ver_cls.__dict__.items():
                if attr.startswith("__"):
                    continue
                if callable(obj):  # normal instance methods
                    if "self" in obj.__code__.co_varnames:
                        obj = types.MethodType(obj, created)
                elif isinstance(obj, classmethod):
                    raise TypeError("Classmethods are not supported by versioned classes")
                created.__dict__[attr] = obj
        return created


class SomeEntity(metaclass=VersionedClass):
    class_var = "stream"

    def do_something(self):
        print("I'm the latest and greatest!")


@SomeEntity.version("6.13.z")
class _:  # noqa
    class_var = "6.13.z"

    def do_something(self):
        print("I'm a bit older, but still good!")
