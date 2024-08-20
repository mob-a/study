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

// const uint b = 16;
// const uint c = 4;
// const uint w = 32;
// const uint t = 26;
// const uint r = 12;
const uint rounds = 12;
const uint subkey_len = 26; //(rounds + 1) * 2;
const uint key_len = 16;
const uint size_of_word = 4;
const uint key_len_as_word = 4;

using WORD = uint32_t;
const WORD P = 0xb7e15163;
const WORD Q = 0x9e3779b9;


const uint w = 32; //word size in bits
WORD ROTL(WORD x,WORD y){
  return (((x)<<(y&(w-1))) | ((x)>>(w-(y&(w-1)))));
}
WORD ROTR(WORD x,WORD y){
  return (((x)>>(y&(w-1))) | ((x)<<(w-(y&(w-1)))));
}


array<WORD, subkey_len> rc5_setup(array<uint8_t, key_len> K) {
  // L[] – A temporary working array used during key scheduling, initialized to the key in words.
  array<WORD, subkey_len> S;
  array<WORD, key_len_as_word> L;
  {
    L[key_len_as_word-1] = 0;
    for (int i = key_len-1; i >= 0; i--) {
      int j = i / size_of_word;
      L[j] = (L[j] << 8) + K[i];
    }
    /*
    // keyを8ビット16個から32ビット4個に直す
    for (int i = key_len-1; i >= 0; i-=size_of_word) {
    L[i / size_of_word] = (K[i]<<24)+(K[i+1]<<16)+(K[i+2]<<8)+K[i+3];
    }
    */
  }
  {
    // subkeyを謎の定数で初期化
    S[0] = P;
    for (int i = 1; i < subkey_len; i++) {
      S[i] = S[i - 1] + Q;
    }
  }
  {
    // Lを利用してsubkeyを更新
    WORD pre_s = 0;
    WORD pre_l = 0;
    int i = 0;
    int j = 0;
    for(int _loop = 0; _loop < 3 * subkey_len; _loop++) {
      S[i] = ROTL(S[i] + pre_s + pre_l, 3);
      L[j] = ROTL(L[j] + pre_s + pre_l, pre_s + pre_l);

      pre_s = S[i];
      pre_l = L[j];

      i = (i + 1) % subkey_len;
      j = (j + 1) % key_len_as_word;
    }
  }
  return S;
}
array<WORD, 2> rc5_encrypt(array<WORD, 2> msg, array<WORD, subkey_len> S) {
  WORD A = msg[0] + S[0];
  WORD B = msg[1] + S[1];
  for (int i = 1; i <= rounds; i++) {
    A = ROTL(A ^ B, B) + S[2 * i];
    B = ROTL(B ^ A, A) + S[2 * i + 1];
  }
  return {A, B};
}
array<WORD, 2> rc5_decrypt(array<WORD, 2> encrypted, array<WORD, subkey_len> S) {
  WORD A = encrypted[0];
  WORD B = encrypted[1];
  for (int i = rounds; i > 0; i--) {
    B = ROTR(B - S[2 * i + 1], A) ^ A;
    A = ROTR(A - S[2 * i], B) ^ B;
  }
  return {A - S[0], B - S[1]};
}

int main(){
  mt19937 engine;
  engine.seed(123);
  array<uint8_t, key_len> K;
  for(int i=0;i<key_len;i++){
    K[i]=engine()%256;
  }

  auto subkey = rc5_setup(K);

  array<WORD, 2> msg = {2222222222, 3333333333};
  auto encrypted = rc5_encrypt(msg, subkey);

  print1(encrypted[0], encrypted[1]);

  auto decrypted = rc5_decrypt(encrypted, subkey);

  print1(decrypted[0], decrypted[1]);

  return 0;
}
