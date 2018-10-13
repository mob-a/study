#include "cymecab_.cpp"
#include <codecvt>
#include <iostream>
#include <string>
#include <locale>

using namespace std;

int main(int argc, char **argv) {
  char input[1024] = "A\t鳥𩸽今日";

  cymecab::CyMeCab *cm = new cymecab::CyMeCab();
  cm->parse(input);
  std::cout << "\n";
  for (int j = 0; j < cm->nodes.size(); j++) {
    std::cout << cm->nodes[j]->surface.size() << "\n";
  }
  cm->extract_words();
  std::cout << cm->words.size() << "kkkk\n";
  for (int k = 0; k < cm->words.size(); k++) {
    std::cout << cm->words[k] << "\n";
  }

  std::cout << "\n";
  std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> converter;
  std::u32string u32input = converter.from_bytes(input);

  std::cout << u32input.size();
  std::cout << "\n";
  for (int i = 0; i < u32input.size(); i++) {
    std::cout << u32input[i];
    std::cout << "\n";
  }
}
