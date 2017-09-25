import hashlib
md5_object = hashlib.md5()
print(md5_object.digestsize)
print(md5_object.block_size)
print(md5_object.hexdigest())
m=md5_object.update("Hello")
print(md5_object.hexdigest())
