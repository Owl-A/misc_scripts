import cgi
from PIL import Image
import copy
import os
import sys
import binascii
print "Content-type: text/html\n\n"
form = cgi.FieldStorage()
user_password = form.getvalue('password')
encrypt_id = form.getvalue('Id')

def convert(img):
    im1=copy.copy(img)
    im1.save("h.bmp")
def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return int2bytes(n).decode(encoding, errors)

def int2bytes(i):
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))
def eight_bit_bin(r_int):
    r_bin=bin(r_int)[2:]
    k=len(r_bin)
    for i in range (0,8-k):
        r_bin="0"+r_bin
    return r_bin
def twentyfour_bit_bin(r_int):
    r_bin=bin(r_int)[2:]
    k=len(r_bin)
    for i in range (0,24-k):
        r_bin="0"+r_bin
    return r_bin
def bit_xor(bit_s1,bit_s2):
    r_int=int(bit_s1,2)^int(bit_s2,2)
    r_bin=bin(r_int)[2:]
    l=len(bit_s1)
    k=len(r_bin)
    for i in range (0,l-k):
        r_bin="0"+r_bin
    return r_bin
def length_equalizer(a,b):
    l_a=len(a)
    l_b=len(b)
    k=""
    if l_a>=l_b:
        for i in range (0,int(l_a/l_b)):
            k+=b
    k+=b[0:l_a%l_b]
    return k
#function to encrypt given plain text return type is binary string
def encrypt(message,password):
    message_b=text_to_bits(message)
    if password =='':
        password='\0'
    xor_k=length_equalizer(message,password)
    xor_b=text_to_bits(xor_k)
    cipher_bin=bit_xor(message_b,xor_b)
    return cipher_bin
#function to decode the supplied cipher using user provided password
def decrypt(cipher_bin,password):
    if password =='':
        password='\0'
    passk=length_equalizer(cipher_bin,text_to_bits(password))
    bin_r=bit_xor(passk,cipher_bin)
    return text_from_bits(bin_r)

def mount(im,a):
    # for y in range (0,u/80):
    #     a+=text_to_bits(message[y*80:(y+1)*80])
    # a+=text_to_bits(message[u-(u%80):])
    i=len(a)
    (j,k)=(im.size)
    pix=im.load()
    for p in range (0,k):

        for q in range (0,j):
            if i==((p*j)+q):
                break
            (r,g,b)=pix[q,p]
            z=eight_bit_bin(r)
            z=z[:7]+a[(p*j)+q]
            r=int(z,2)
            pix[q,p]=(r,g,b)
        if i==((p*j)+q):
            break
    f=twentyfour_bit_bin(i)
    pix[j-1,k-1]=(int(f[:8],2),int(f[8:16],2),int(f[16:24],2))
    return im
#s=raw_input('Enter your message\n')
#password=raw_input('Enter your password\n')
def decode(im):
    (j,k)=(im.size)
    pix=im.load()
    (R,G,B)=pix[j-1,k-1]
    f=eight_bit_bin(R)+eight_bit_bin(G)+eight_bit_bin(B)
    i=int(f,2)
    result=''
    for p in range (0,k):
        for q in range (0,j):
            if i==((p*j)+q):
                break
            (r,g,b)=pix[q,p]
            z=eight_bit_bin(r)
            result+=z[7]
        if i==((p*j)+q):
            break
    # resulting=''
    # h=i/8
    # for p in range (0,h):
    #     resulting+=text_from_bits(result[(p*8):(p*8)+8])
    return result
def take_this(user_password,encrypt_id):
    im3 = Image.open(encrypt_id+".bmp")
    r=decrypt(decode(im3),user_password)
    print "<HTML>"
    print "<HEAD>"
    print "<title> Decrypt </title>\n</HEAD>\n<BODY background = \"background.jpg\">\n<p style=\"color:#ffffff;font-family:verdana;font-size:200%\">\n"
    print "<p>" +r + "</p>"
    print "\n </p>\n\n</BODY>\n</HTML>"

take_this(user_password,encrypt_id)
