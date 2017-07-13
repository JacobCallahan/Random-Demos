"""This demo shows the concept of how to write one test,
   and run it on multiple interfaces.
"""
import attr

@attr.s()
class API():
    @staticmethod
    def move_forward(dist=5):
        print ('Running forward {} spaces.'.format(dist))

    @staticmethod
    def move_left(dist=5):
        print ('Running left {} spaces.'.format(dist))

    @staticmethod
    def move_right(dist=5):
        print ('Running right {} spaces.'.format(dist))

    @staticmethod
    def move_back(dist=5):
        print ('Running back {} spaces.'.format(dist))


@attr.s()
class CLI():
    @staticmethod
    def move_forward(dist=5):
        print ('Walking forward {} spaces.'.format(dist))

    @staticmethod
    def move_left(dist=5):
        print ('Walking left {} spaces.'.format(dist))

    @staticmethod
    def move_right(dist=5):
        print ('Walking right {} spaces.'.format(dist))

    @staticmethod
    def move_back(dist=5):
        print ('Walking back {} spaces.'.format(dist))


@attr.s()
class UI():
    @staticmethod
    def move_forward(dist=5):
        print ('Crawling forward {} spaces.'.format(dist))

    @staticmethod
    def move_left(dist=5):
        print ('Crawling left {} spaces.'.format(dist))

    @staticmethod
    def move_right(dist=5):
        print ('Crawling right {} spaces.'.format(dist))

    @staticmethod
    def move_back(dist=5):
        print ('Crawling back {} spaces.'.format(dist))


def run_on(*args):
    def wrapper(func):
        def interface_runner():
            if 'api' in args:
                func(API)
            if 'cli' in args:
                func(CLI)
            if 'ui' in args:
                func(UI)
        return interface_runner
    return wrapper


@run_on('api', 'cli', 'ui')
def test1(interface):
    """Example test for multiple and targeted interfaces"""
    print ('*** Running test on {} ***'.format(interface.__name__))

    API.move_forward()
    interface.move_left(6)
    API.move_back(20)
    interface.move_right(15)
    interface.move_forward(50)


if __name__ == '__main__':
    test1()
