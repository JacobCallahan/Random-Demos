with open("something") as my_file:
    for line in my_file:
        print(line)


import _io

class SafeWrite(_io.TextIOWrapper):
    def write(self, text, /):
        undo = UndoWrite.from_change(self, text)
        super().write(text)
        return undo

class UndoWrite:
    def __init__(self, fh, pos, contents):
        self.fh = fh
        self.pos = pos
        self.contents = contents

    def undo(self):
        self.fh.seek(self.pos)
        self.fh.write(self.contents)

    @classmethod
    def from_change(cls, fh, new_content):
        pos = fh.tell()
        old_content = fh.read(len(new_content))
        fh.seek(pos)
        return cls(fh, pos, old_content)

    def __call__(self):
        self.undo()
