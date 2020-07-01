#include <iostream>
#include <sstream>
#include <string>
#include <cstring>
#include <vector>
#include <algorithm>
#include <iterator>

using namespace std;

#ifndef RECIPE_PARSER_RECIPE_PARSE_H
#define RECIPE_PARSER_RECIPE_PARSE_H

extern "C"
{
char* parser(char* ingredient_str_char);
//__declspec(dllexport) void removal(char* to_delete);
}

vector<string> word_2_vector(string);
bool inVector(string, vector<string>);
bool is_number(const std::string& s); //From Stackoverflow

#endif //RECIPE_PARSER_RECIPE_PARSE_H
