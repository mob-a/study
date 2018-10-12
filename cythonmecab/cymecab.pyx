from libcpp.vector cimport vector
from libcpp.string cimport string

cdef extern from "cymecab_.cpp" namespace "cymecab":
    cdef cppclass CyMeCab:
        CyMeCab() except +
        void parse(char* sentence)
        int word_num
        char words[256][256]

cdef class CyMeCabWrapper(object):
    cdef CyMeCab* thisptr

    def __cinit__(self):
        self.thisptr = new CyMeCab()

    def __dealloc(self):
        del self.thisptr

    def parse(self, text):
        return self.thisptr.parse(
            text.encode("utf-8")
        )

    property word_num:
        def __get__(self):
            return self.thisptr.word_num
        # def __set__(self, n_iter):
        #     self.thisptr.word_num = word_num

    property words:
        def __get__(self):
            return [
                self.thisptr.words[i].decode("utf-8")
                for i in range(self.word_num)
            ]
        # def __set__(self, words):
        #     self.thisptr.words = words
