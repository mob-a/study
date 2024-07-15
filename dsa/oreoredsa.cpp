#include <bits/stdc++.h>
// clang-format off
using namespace std; using ll=long long; using ull=unsigned long long; using pll=pair<ll,ll>; const ll INF=4e18;
void print0(){}; template<typename H,typename... T> void print0(H h,T... t){cout<<h;print0(t...);}
void print1(){print0("\n");}; template<typename H,typename... T>void print1(H h,T... t){print0(h);if(sizeof...(T)>0)print0(" ");print1(t...);}
void ioinit() { cout<<fixed<<setprecision(15); cerr<<fixed<<setprecision(6); ios_base::sync_with_stdio(0); cin.tie(0); }
#define debug1(a) { cerr<<#a<<":"<<a<<endl; }
#define debug2(a,b) { cerr<<#a<<":"<<a<<" "<<#b<<":"<<b<<endl; }
#define debug3(a,b,c) { cerr<<#a<<":"<<a<<" "<<#b<<":"<<b<<" "<<#c<<":"<<c<<endl; }
#define debug4(a,b,c,d) { cerr<<#a<<":"<<a<<" "<<#b<<":"<<b<<" "<<#c<<":"<<c<<" "<<#d<<":"<<d<<endl; }
// clang-format on

namespace md5_64 {

string tohex(uint32_t v) {
    std::stringstream stream;
    stream << setw(2) << setfill('0') << hex << (v & 255);
    stream << setw(2) << setfill('0') << hex << ((v >> 8) & 255);
    stream << setw(2) << setfill('0') << hex << ((v >> 16) & 255);
    stream << setw(2) << setfill('0') << hex << ((v >> 24) & 255);
    std::string result(stream.str());
    return result;
}

string tohex64(uint64_t v) {
    std::stringstream stream;
    stream << setw(2) << setfill('0') << hex << (v & 255);
    stream << setw(2) << setfill('0') << hex << ((v >> 8) & 255);
    stream << setw(2) << setfill('0') << hex << ((v >> 16) & 255);
    stream << setw(2) << setfill('0') << hex << ((v >> 24) & 255);
    stream << setw(2) << setfill('0') << hex << ((v >> 32) & 255);
    stream << setw(2) << setfill('0') << hex << ((v >> 40) & 255);
    stream << setw(2) << setfill('0') << hex << ((v >> 48) & 255);
    stream << setw(2) << setfill('0') << hex << ((v >> 56) & 255);
    std::string result(stream.str());
    return result;
}

uint32_t leftrotate(uint32_t f, uint32_t s) {
    return (f << s) | (f >> (32 - s));
}

ull hash(string &in) {
    // 参考:
    // https://ja.wikipedia.org/wiki/MD5
    // https://ryozi.hatenadiary.jp/entry/20100626/1277529116
    // https://www.ipa.go.jp/security/rfc/RFC1321JA.html

    // 定数の宣言
    static const uint32_t K[64] = {
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391};

    static const uint32_t S[64] = {
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
        5, 9, 14, 20, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 6, 10, 15, 21, 6, 10, 15,
        21, 6, 10, 15, 21, 6, 10, 15, 21};

    const uint32_t A0INIT = 0x67452301;
    const uint32_t B0INIT = 0xefcdab89;
    const uint32_t C0INIT = 0x98badcfe;
    const uint32_t D0INIT = 0x10325476;

    uint init_len = in.size();

    auto buf = in;
    // パディング
    buf.push_back(0x80);
    while (true) {
        if (buf.size() % 64 == 56) {
            break;
        } else {
            buf.push_back(0x00);
        }
    }

    // 入力データのサイズを末尾に追加   (2^64bitより長いものは考えない)
    //   長さの下位バイトから順に、bufの前方バイトから入れていく
    uint length = init_len * 8;
    buf.push_back(length % 256);
    buf.push_back((length >> 8) % 256);
    buf.push_back((length >> 16) % 256);
    buf.push_back((length >> 24) % 256);
    buf.push_back((length >> 32) % 256);
    buf.push_back((length >> 40) % 256);
    buf.push_back((length >> 48) % 256);
    buf.push_back((length >> 56) % 256);

    uint32_t A0 = A0INIT;
    uint32_t B0 = B0INIT;
    uint32_t C0 = C0INIT;
    uint32_t D0 = D0INIT;

    uint32_t msg_idx = 0;
    uint32_t M[16];

    uint msg_size = buf.size();
    while (msg_idx < msg_size) {
        for (int i = 0; i < 16; i++) {
            // 注意：bufの前方にあるバイトが、Mの後方に入る
            M[i] = (uint32_t(buf[msg_idx + 3]) << 24) + (uint32_t(buf[msg_idx + 2]) << 16) + (uint32_t(buf[msg_idx + 1]) << 8) + (buf[msg_idx + 0]);
            msg_idx += 4;
        }

        uint32_t A = A0;
        uint32_t B = B0;
        uint32_t C = C0;
        uint32_t D = D0;

        uint32_t F = 0;
        int g = 0;
        for (int i = 0; i < 64; i++) {
            if (i < 16) {
                F = (B & C) | ((~B) & D);
                g = i;
            } else if (i < 32) {
                F = (B & D) | (C & (~D));
                g = (5 * i + 1) % 16;
            } else if (i < 48) {
                F = (B ^ C) ^ D;
                g = (3 * i + 5) % 16;
            } else {
                F = C ^ (B | (~D));
                g = (7 * i) % 16;
            }

            F = F + A + M[g] + K[i];
            A = D;
            D = C;
            C = B;
            B = B + leftrotate(F, S[i]);
        }
        A0 = A0 + A;
        B0 = B0 + B;
        C0 = C0 + C;
        D0 = D0 + D;
    }
    ull h = (ull(B0) << 32) + ull(A0);
    return h;
}
}  // namespace md5_64

class oreoredsa_signer {
    // https://qiita.com/angel_p_57/items/f2350f2ba729dc2c1d2e
    // https://ja.wikipedia.org/wiki/Digital_Signature_Algorithm
   private:
    ull x;
    mt19937 engine;

   public:
    ull p;
    ull q;
    ull g;
    ull y;

    ull mpow(ull v, int n, ull m) {
        if (n == 0) {
            return 1;
        } else if (n & 1) {
            return v * mpow(v * v % m, n / 2, m) % m;
        } else {
            return mpow(v * v % m, n / 2, m);
        }
    }
    ull minv(ull v, ull m) {
        return mpow(v, m - 2, m);
    }
    ull hash(string m) {
        return md5_64::hash(m);
    }
    bool isprime(ull v) {
        assert(v >= 2);
        for (int i = 2; i * i <= v; i++) {
            if (v % i == 0) return false;
        }
        return true;
    }
    oreoredsa_signer() {
        random_device seed_gen;
        engine.seed(seed_gen());
        //
        ull _q = 0;
        int _q_low = 1000000;
        int _q_high = 2000000;
        for (int _q1 = _q_low + engine() % (_q_high - _q_low); true; _q1++) {
            if (isprime(_q1)) {
                _q = _q1;
                break;
            }
        }
        ull _p = 0;
        for (int _p1 = _q + 1; true; _p1 += _q) {
            if (isprime(_p1)) {
                _p = _p1;
                break;
            }
        }
        ull _g = 0;
        for (int _g1 = 2; _g1 < _p; _g1++) {
            if (mpow(_g1, _q, _p) == 1) {
                _g = _g1;
                break;
            }
        }
        p = _p;
        q = _q;
        g = _g;
        assert(mpow(g, q, p) == 1);
        assert(q < p);
        assert(g < p);
        assert(isprime(q));
        assert(isprime(p));

        x = 1 + engine() % (q - 1);
        y = mpow(g, x, p);
        //
    }
    pair<ull, ull> sign(string m) {
        ull k = 1 + engine() % (q - 1);
        ull r = mpow(g, k, p) % q;
        assert(r > 0);  // TODO
        ull s = (hash(m) % q + x * r % q) * minv(k, q) % q;
        assert(s > 0);  // TODO
        return {r, s};
    }
    tuple<ull, ull, ull, ull> show_pubkey() {
        return {p, q, g, y};
    }
};
class oreoredsa_verifier {
   public:
    ull p;
    ull q;
    ull g;
    ull y;

    ull mpow(ull v, int n, ull m) {
        if (n == 0) {
            return 1;
        } else if (n & 1) {
            return v * mpow(v * v % m, n / 2, m) % m;
        } else {
            return mpow(v * v % m, n / 2, m);
        }
    }
    ull minv(ull v, ull m) {
        return mpow(v, m - 2, m);
    }
    ull hash(string m) {
        return md5_64::hash(m);
    }
    oreoredsa_verifier(tuple<ull, ull, ull, ull> pubkey) {
        tie(p, q, g, y) = pubkey;
    }
    bool verify(string m, pair<ull, ull> sign) {
        ull r = sign.first;
        ull s = sign.second;
        if (!(0 < r && r < q)) {
            return false;
        }
        if (!(0 < s && s < q)) {
            return false;
        }
        ull w = minv(s, q);
        ull u1 = (hash(m) % q) * w % q;
        ull u2 = r * w % q;
        ull v = (mpow(g, u1, p) * mpow(y, u2, p) % p) % q;
        return v == r;
    }
};
int main() {
    string msg;
    cin >> msg;

    auto signer = oreoredsa_signer();
    auto verifier = oreoredsa_verifier(signer.show_pubkey());

    auto sign = signer.sign(msg);
    if (verifier.verify(msg, sign)) {
        print0("msg=", msg, "\n");
        print0("pubkey(p,q,g,y)=", verifier.p, ":", verifier.q, ":", verifier.g, ":", verifier.y, "\n");
        print0("sign(r,s)=", sign.first, ":", sign.second, "\n");
        print1("verify success!");
    } else {
        print1("verify failure!");
    }
    return 0;
}
