import time
from .shared_resource import SharedResource


with SharedResource("my_resource", time.sleep, 300) as resource:
    print(f"I got resource {resource.id}")
    print(f"Is main? {resource.is_main}")
    print(f"{resource.id} is ready")
    resource.ready()
    print(f"{resource.id} has come back from waiting")
print(f"{resource.id} is done")

