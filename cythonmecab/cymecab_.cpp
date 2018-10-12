#include <mecab.h>
#include <vector>
#include <iostream>
#include <string>
#include <string.h>

using namespace std;

namespace cymecab {
  class CyMeCab {
  private:
    MeCab::Tagger *tagger;
  public:
    int word_num;
    char words[256][256];
    CyMeCab() {
      tagger = MeCab::createTagger("");
    }
    ~CyMeCab() {
      delete tagger;
    }
    void parse(char* sentence) {
      word_num = 0;
      const MeCab::Node* node = tagger->parseToNode(sentence);
      for (; node; node = node->next) {
	if (node->posid == 38) {
	  strncpy(words[word_num], node->surface, node->length);
	  words[word_num][node->length] = '\0';
	  word_num++;
	}
      }
    }
  };
}
