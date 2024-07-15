#include <bits/stdc++.h>
// clang-format off
using namespace std; using ll=long long; using ull=unsigned long long; using pll=pair<ll,ll>; const ll INF=4e18;
void print0(){}; template<typename H,typename... T> void print0(H h,T... t){cout<<h;print0(t...);}
void print1(){print0("\n");}; template<typename H,typename... T>void print1(H h,T... t){print0(h);if(sizeof...(T)>0)print0(" ");print1(t...);}
#define debug1(a) { cerr<<#a<<":"<<a<<endl; }
#define debug2(a,b) { cerr<<#a<<":"<<a<<" "<<#b<<":"<<b<<endl; }
#define debug3(a,b,c) { cerr<<#a<<":"<<a<<" "<<#b<<":"<<b<<" "<<#c<<":"<<c<<endl; }
#define debug4(a,b,c,d) { cerr<<#a<<":"<<a<<" "<<#b<<":"<<b<<" "<<#c<<":"<<c<<" "<<#d<<":"<<d<<endl; }
// clang-format on

class oreoredh {
    // https://ja.wikipedia.org/wiki/%E3%83%87%E3%82%A3%E3%83%95%E3%82%A3%E3%83%BC%E3%83%BB%E3%83%98%E3%83%AB%E3%83%9E%E3%83%B3%E9%8D%B5%E5%85%B1%E6%9C%89
    // https://okumuralab.org/~okumura/python/diffie_hellman.html
   private:
    ull a;
    mt19937 engine;
    ull key() {
        return mpow(mid_received, a, p);
    }

   public:
    ull p;
    ull g;
    ull mid_received;

    ull danger_show_key() {
        return mpow(mid_received, a, p);
    }
    vector<ull> encrypt(string m) {
        ull k = hash(key());
        vector<ull> result;
        for (auto c : m) {  // かなり弱い
            ull s = k ^ c;
            result.push_back(s);
            k = hash(k);
        }
        return result;
    }
    string decrypt(vector<ull> e) {
        ull k = hash(key());
        string result;
        for (auto s : e) {  // かなり弱い
            ull c = k ^ s;
            assert(0 <= c && c < 256);
            result.push_back(c);
            k = hash(k);
        }
        return result;
    }
    ull hash(ull dat) {
        static const ull FNV_OFFSET_BASIS_64 = 14695981039346656037LLU;
        static const ull FNV_PRIME_64 = 1099511628211LLU;
        ull hash = FNV_OFFSET_BASIS_64;
        for (ll i = 0; i < 8; i++) {
            hash = (FNV_PRIME_64 * hash) ^ (dat & 255);
            dat = dat >> 8;
        }
        return hash;
    }
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

    bool isprime(ull v) {
        assert(v >= 2);
        for (int i = 2; i * i <= v; i++) {
            if (v % i == 0) return false;
        }
        return true;
    }
    oreoredh() {
        random_device seed_gen;
        engine.seed(seed_gen());
    }
    pair<ull, ull> send_init() {
        int _p_low = 1000000;
        int _p_high = 2000000;
        for (int _p1 = _p_low + engine() % (_p_high - _p_low); true; _p1++) {
            if (isprime(_p1)) {
                p = _p1;
                break;
            }
        }

        // gは原始根にするらしい
        // https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange
        for (int _g1 = 2; true; _g1++) {
            bool ok = true;
            for (int n = 1; n <= p - 2; n++) {
                if (mpow(_g1, n, p) == 1) {
                    ok = false;
                    break;
                }
            }
            if (ok) {
                g = _g1;
                break;
            }
        }
        assert(1 < g);
        assert(g < p);
        assert(isprime(p));
        make_secret();
        return {p, g};
    }
    void receive_init(pair<ull, ull> ini) {
        p = ini.first;
        g = ini.second;
        make_secret();
    }
    void make_secret() {
        a = 1 + engine() % (p - 1);
    }
    ull send_my_mid() {
        return mpow(g, a, p);
    }
    void receive_mid(ull m) {
        mid_received = m;
    }
};
int main() {
    auto alice = oreoredh();
    auto bob = oreoredh();
    bob.receive_init(alice.send_init());

    bob.receive_mid(alice.send_my_mid());
    alice.receive_mid(bob.send_my_mid());

    string m = "SuperSecretMessage!";
    auto enc = alice.encrypt(m);
    auto dec = bob.decrypt(enc);

    print0("[");
    for (int i = 0; i < enc.size(); i++) {
        print0(enc[i], ", ");
    }
    print0("]\n");
    print1(dec);
    debug3(alice.p, alice.g, alice.mid_received);
    debug3(bob.p, bob.g, bob.mid_received);
    debug2(alice.danger_show_key(), bob.danger_show_key());
    return 0;
}
