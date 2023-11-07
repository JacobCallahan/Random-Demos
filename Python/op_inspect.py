import inspect

class Dummy:
    def __init__(self, name):
        self.name = name

    def print_name(self):
        print(f"My name is {self.name}")

    def call_meth(self, meth):
        print(f"I am calling the method: {meth}")
        return meth()

class Gadget:
    def totally_innocent(self):
        caller = inspect.stack()[1][0].f_locals["self"]
        setattr(caller, "name", "Dr. Claw")

    def add_meth(self):
        caller = inspect.stack()[1][0].f_locals["self"]
        def nefarious():
            for _ in range(5):
                print("I'm doing something bad")
        setattr(caller, "print_name", nefarious)

    def swap(self):
        d2 = Dummy("jAcK")
        caller = inspect.stack()[1][0].f_locals["self"]
        caller.__dict__ = d2.__dict__


my_dummy = Dummy("Todd")
inspector = Gadget()
my_dummy.print_name()
my_dummy.call_meth(inspector.totally_innocent)
my_dummy.print_name()
my_dummy.call_meth(inspector.add_meth)
my_dummy.print_name()
my_dummy.call_meth(inspector.swap)
print(id(my_dummy))
my_dummy.print_name()
print(id(my_dummy))