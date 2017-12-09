# python svm_kernel.py |grep -E '.*2.000,.*2.000,'

# 言語処理のための機械学習入門の4.4カーネル法を実装
#   (間違いはあるかもしれません)
#
# 最急勾配法で最適化する方針でいく. aiでの偏微分について考える.
# なお、最小化問題として解く。目的関数は書籍にあるものに -1 倍したもの。
#
# データ数D個とすると、a1~aDのD個の変数
# 条件から、aD = -yD*(y1*a1+y2*a2+...+yD-1*aD-1) なので実質D-1個の変数
# aDの中でIに依存する部分は
#  -yD*yI*aI
# ai,ajの組み合わせの和のところで、偏微分で考慮すべきところ
# yI*yj*aI*aj*k(dI,dj)*2
#   => 2*yI*yj*aj*k(dI,dj)
# yI*yI*aI*aI*k(dI,dI)*1
#   => 2*yI*yI*aI*k(dI,dI)
# yD*yj*aD*aj*k(dD,dj)*2
#   => 2*yD*yj*(-yD*yI)*aj*k(dD,dj)
#   = -2*yI*yj*aj*k(dD,dj) # yD*yD=1
# yD*yI*aD*aI*k(dD,dI)*2
#   = 2*yD*yI*k(dD,dI)*(-yD)*{aI*(sigma(k=1~D-1&&k!=I)(yk*ak)) + yI*aI*aI}
#   = -2*yI*k(dD,dI)*{aI*(sigma(k=1~D-1&&k!=I)(yk*ak)) + yI*aI*aI}
#   => -2*yI*k(dD,dI)*{sigma(k=1~D-1)(yk*ak) + yI*aI}
# yD*yD*aD*aD*k(dD,dD)*1
#   = yD*yD*{(-yD)*sigma(k=1~D-1)(yk*ak)}*{(-yD)*sigma(l=1~D-1)(yl*al)}*k(dD,dD)
#   = sigma(k=1~D-1)(yk*ak)*sigma(l=1~D-1)(yl*al)*k(dD,dD)
#   = k(dD,dD)*{sigma(k=1~D-1&&k!=I)(yk*ak)+yI*aI}*{sigma(l=1~D-1&&l!=I)(yl*al)+yI*aI}
#   => k(dD,dD)*{2*sigma(k=1~D-1&&k!=I)(yI*yk*ak)+2*yI*yI*aI}
#   => 2*k(dD,dD)*yI*sigma(k=1~D-1)(yk*ak)

# df/daI
#  = yI*sigma(j=1~D-1) (yj*aj*k(dI,dj)) - yI*sigma(j=1~D-1)(yj*aj*k(dD,dj)) + yI*k(dD,dD)*sigma(j=1~D-1)(yj*aj)
#    - 1 + yD*yI
#  = yI*sigma(j=1~D-1){ (yj*aj*k(dI,dj) - yj*aj*k(dD,dj) + yj*aj*k(dD,dD) } + yI*yD - 1

# というわけでやってみる

import random
def abs(val):
    if val < 0:
        return -val
    return val

def innerprod(v1,v2):
    length = len(v1)
    return sum([
        v1[_i] * v2[_i] for _i in range(length)
    ])

def kernel(v1, v2):
    return (innerprod(v1, v2) + 1.0) ** 2.0

# def kernel(v1, v2):
#     return innerprod(v1, v2)

def kernel_table(x, D):
    k = [None] * D
    for i in range(D):
        k[i] = [0] * D
        for j in range(D):
            k[i][j] = kernel(x[i], x[j])
    return k

def gd(D,x,y,k):
    # 最適化のやりかた、もっとマシな方法があると思う
    # 以下の条件を満たしながら進める
    # sigma(i)(yi*ai) = 0
    # ai>=0

    a = [0]*(D)
    for j in range(D):
        a[j] = (1.0 - 0.2*random.random()) / D
    a[D-1] = y[D-1] * (1.0 - sum(a))

    ITERATION = 100000
    rate = 0.001

    NONZERO_LAST = D-1
    for iteration in range(ITERATION):
        # 偏微分を求めるのは a(1)~a(D-1)まで(配列インデックスではa[0]~a[D-2]).
        # a(D)はsigma(i)(yi*ai) = 0 の等号条件の調整用
        # ただし、a(D)=0が最適と思われるなら、a(D)=0に固定する
        # そのとき、等号条件の調整用をa(D-1)に変更する
        grada = [0]*NONZERO_LAST
        for i in range(NONZERO_LAST):
            sigma = 0
            for j in range(NONZERO_LAST):
                sigma += y[j] * a[j] * (k[i][j] - k[NONZERO_LAST][j] + k[NONZERO_LAST][NONZERO_LAST])
            grada[i] = y[i] * sigma + y[i] * y[NONZERO_LAST] - 1

        for i in range(NONZERO_LAST):
            a[i] = a[i] - rate * grada[i]
            if a[i] < 0:
                a[i] = 0

        aLAST = 0
        for i in range(NONZERO_LAST):
            aLAST += y[i] * a[i]
        aLAST = -y[NONZERO_LAST]*aLAST
        if aLAST < 0:
            a[NONZERO_LAST] = 0
            NONZERO_LAST -= 1

    a[NONZERO_LAST] = -y[NONZERO_LAST] * sum([
        y[_i] * a[_i] for _i in range(NONZERO_LAST)
    ])

    sum_yi = sum([
        y[i] * a[i] for i in range(D)
    ])
    assert(abs(sum_yi) < 0.0001)

    return a

def classify(target_x, observed_x, observed_y, a, b, D):
    result = 0
    for i in range(D):
        result += a[i] * observed_y[i] * kernel(target_x, observed_x[i])
    return result - b

def get_bias(x, y, a, D):
    min_classify = 1.0 * (10.0**10.0)
    for i in range(D):
        # 正例の中から、最もclassifyした値が小さいものを探す
        if y[i] < 0:
            continue
        classify_result = classify(x[i], x, y, a, 0, D) # この時点ではbias=0としておく
        if classify_result < min_classify:
            min_classify = classify_result
    return min_classify - 1.0 # (正誤表参照) http://www.lr.pi.titech.ac.jp/~takamura/ml4nl.html

def main():
    x = [
        # # 2乗カーネルテスト用
        [1.0,1.0],[2.0,2.0],
        [-1.0,-1.0],[-2.0,-2.0],
        [-1.0,1.0],[-2.0,2.0],
        [1.0,-1.0],[2.0,-2.0],
        # # 線形カーネルテスト用
        # [1.0,1.0],[2.0,2.0],
        # [-1.0,2.0],[2.0,-1.0],
        # [-1.0,-1.0],[-2.0,-2.0],
        # [1.0,-2.0],[-2.0,1.0],
        # # (範囲狭い)
        # [0.1,0.1],[2.0,2.0],
        # [-1.0,1.1],[1.1,-1.0],
        # [-0.1,-0.1],[-2.0,-2.0],
        # [1.0,-1.1],[-1.1,1.0],
        # # (バイアスあり)
        # [0.1, 3.0],[3.0, 0.1],
        # [1.5,1.5],[3.0,3.0],
        # [2.0,-1.0],[-1.0,2.0],
        # [-0.5,0.5],[-1.0,-1.0],
    ]
    y = [
        1,1,
        1,1,
        -1,-1,
        -1,-1,
    ]

    D = len(x)
    k = kernel_table(x, D)
    a = gd(D,x,y,k)
    b = get_bias(x,y,a,D)

    #グリッド
    print("x,y,val")
    p = -2.0
    while p < 2.000001:
        q = -2.0
        while q < 2.000001:
            result = classify([p,q], x,y,a,b,D)
            print("{0:.3f},{1:.3f},{2:.3f}".format(p,q,result))
            q += 0.25
        p += 0.25

if __name__ == "__main__":
    main()
