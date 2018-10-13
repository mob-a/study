#include <mecab.h>
#include <vector>
#include <iostream>
#include <string>
#include <string.h>
#include <codecvt>
#include <locale>


using namespace std;

namespace cymecab {
  class NodeClone {
  public:
    std::u32string surface;
    std::u32string feature;
    int posid;
    int rlength;
    int length;
    int stat;

    NodeClone(
	      char* surface_char,
	      const char* feature_char,
	      int posid,
	      int rlength,
	      int length,
	      int stat
	      ):
      posid(posid),
      rlength(rlength),
      length(length),
      stat(stat)
    {
      std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> converter; //[TODO]
      surface = converter.from_bytes(surface_char);
      feature = converter.from_bytes(feature_char);
    }
  };

  class CyMeCab {
  private:
    MeCab::Tagger *tagger;
    char surface_buf[1024];
    vector<NodeClone*> nodes;
  public:
    vector<string> words;
    CyMeCab() {
      tagger = MeCab::createTagger("");
    }
    ~CyMeCab() {
      delete tagger;
    }
    void parse(char* sentence) {
      nodes.clear(); //[TODO] 過去Nodeのゴミが残るかも.わからん.

      const MeCab::Node* node = tagger->parseToNode(sentence);
      for (; node; node = node->next) {
	strncpy(surface_buf, node->surface, node->length);
	surface_buf[node->length] = '\0';
	nodes.push_back(new NodeClone(surface_buf, node->feature, node->posid, node->rlength, node->length, node->stat));
      }
    }
    void extract_words() {
      words.clear(); //[TODO] 過去stringのゴミが残るかも.わからん.

      std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> converter; //[TODO]
      for (int i = 0; i < nodes.size(); i++) {
	if (nodes[i]->posid == 38) {
	  words.push_back(converter.to_bytes(nodes[i]->surface));
	}
      }
    }
  };
}
