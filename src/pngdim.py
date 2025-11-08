class NotAPNGImageError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

def is_png_image(data:bytes) -> bool:
    if not data[0:4] == b'\x89\x50\x4e\x47':
        return False
    return True

class PNGImage:
    def __init__(self,data:bytes):
        self.width = 0
        self.height = 0
        
        if not is_png_image(data):
            raise NotAPNGImageError("The specified data is not a valid PNG Image file")
        else:
            self.data = data
        try:
            self.width,self.height = self.get_dimensions()
        except:
            raise NotAPNGImageError("The specified data is not a valid PNG Image file")
    def get_dimensions(self) -> tuple[int,int]:
        """Get the width,height of the PNG image"""
        block_width = self.data[0x10:0x14]
        block_height = self.data[0x14:0x18]

        self.width = int.from_bytes(block_width)
        self.height = int.from_bytes(block_height)
        return (self.width,self.height)
    def is_valid_minecraft_server_image(self) -> bool:
        return self.width == 64 and self.height == 64
def load(file:str):
    with open(file,'rb') as f:
        bt = f.read()
    return PNGImage(bt)