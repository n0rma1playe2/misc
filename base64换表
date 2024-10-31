import base64
str = "qMfZzunurNTuAdfZxZfZxZrUx2v6x2i0C2u2ngrLyZbKzx0="   # 欲解密的字符串
outtab  = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="  #  原生字母表
intab   = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/="  #  换表之后的字母表
print (base64.b64decode(str.translate(str.maketrans(intab,outtab))).decode())
