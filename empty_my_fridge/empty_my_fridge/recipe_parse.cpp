#include "recipe_parse.h"
using namespace std;



vector<string> measurementUnits = {"teaspoons","tablespoons","cups","containers","packets","bags","quarts","pounds","cans","bottles",
                                  "pints","packages","ounces","jars","heads","gallons","drops","envelopes","bars","boxes","pinches",
                                  "dashes","bunches","recipes","layers","slices","links","bulbs","stalks","squares","sprigs",
                                  "fillets","pieces","legs","thighs","cubes","granules","strips","trays","leaves","loaves","halves",
                                  "cloves", "large", "extra-large", "small", "grams","milliliters", "sticks", "whole", "handful", "unsalted",
                                  "salted", "baby"};

vector<string>measurementUnitsAbbreviations = {"c", "c.", "C","gal", "oz", "oz.", "pt", "pts", "pt.", "lb", "lb.", "lbs", "lbs.",
                                               "Lb", "Lbs", "qt", "qt.", "qts", "qts.", "tbs","tbs.", "tbsp", "tbsp.", "tbspn","tbspn.", "T", "T.","tsp","tsp.", "tspn","tspn.", "t", "t.","g", "g.", "kg", "kg.", "Kg", "Kg.", "l", "l.", "L", "L.", "mg", "mg.", "ml", "ml.", "mL", "mL.", "pkg", "pkgs", "pcs", "pcs."};

vector<string> descriptions = {"baked", "beaten", "blanched", "boiled", "boiling", "boned", "breaded", "brewed", "broken", "chilled",
                               "chopped", "cleaned", "coarse", "cold", "cooked", "cool", "cooled", "cored", "creamed", "crisp", "crumbled",
                               "crushed", "cubed", "cut", "deboned", "deseeded", "diced", "dissolved", "divided", "drained", "dried", "dry",
                               "fine", "firm", "fluid", "fresh", "frozen", "grated", "grilled", "ground", "halved", "hard", "hardened",
                               "heated", "heavy", "juiced", "julienned", "jumbo", "large", "lean", "light", "lukewarm", "marinated",
                               "mashed", "medium", "melted", "minced", "near", "opened", "optional", "packed", "peeled", "pitted", "popped",
                               "pounded", "prepared", "pressed", "pureed", "quartered", "refrigerated", "rinsed", "ripe", "roasted",
                               "roasted", "rolled", "rough", "scalded", "scrubbed", "seasoned", "seeded", "segmented", "separated",
                               "shredded", "sifted", "skinless", "sliced", "slight", "slivered", "small", "soaked", "soft", "softened",
                               "split", "squeezed", "stemmed", "stewed", "stiff", "strained", "strong", "thawed", "thick", "thin", "tied",
                               "toasted", "torn", "trimmed", "wrapped", "vained", "warm", "washed", "weak", "zested", "wedged",
                               "skinned", "gutted", "browned", "patted", "raw", "flaked", "deveined", "shelled", "shucked", "crumbs",
                               "halves", "squares", "zest", "peel", "uncooked", "butterflied", "unwrapped", "unbaked", "warmed", "cracked","good","store",
                               "bought", "fajita-sized", "finely", "freshly","slow", "quality", "sodium", "mixed", "wild", "Asian", "Italian", "Chinese",
                               "American", "garnished", "seedless","coarsely", "natural", "organic", "solid", "heaping","stoned", "homemade"};

vector<string> description_exceptions = {"butter", "oil", "cream", "salt","bread","all", "red"};
vector<string> numbers = {"one", "two","three","four","five","six","seven","eight","nine","ten", "elevin","twelve","dozen"};
vector<string> brands = {"bertolli®", "cook\"s", "hothouse", "NESTLÉ®", "TOLL HOUSE®"};
vector<string> modifier = {"plus", "silvered", "virgin", "seasoning"};
vector<string> precedingAdverbs = {"well", "very", "super"};
vector<string> succeedingAdverbs = {"diagonally", "lengthwise", "overnight"};
vector<string> prepositions = {"as", "such", "for", "with", "without", "if", "about", "e.g.", "in", "into", "at", "until", "won\"t"};
vector<string> descriptionsWithPredecessor = {"removed", "discarded", "reserved", "included", "inch", "inches", "old", "temperature", "up"};
vector<string> unnecessaryDescriptions = {"chunks", "pieces", "rings", "spears"};
vector<string> hypenatedPrefixes = {"non", "reduced", "semi", "low"};
vector<string> hypenatedSuffixes = {"coated", "free", "flavored"};
vector<string> specialCharacters = {"(", ")", "[", "]"};


vector<string> word_2_vector(string ingredient_str){
    istringstream iss(ingredient_str);
    vector<string> tokens{istream_iterator<string>{iss},
                          istream_iterator<string>{}};
    return tokens;
}

bool inVector(string item, vector<string> vec){
    for(int i = 0; i < vec.size(); i++){
        if (vec[i].find(item) != string::npos)
            return true;

    }
    return false;
}
//From Stackoverflow  https://stackoverflow.com/questions/4654636/how-to-determine-if-a-string-is-a-number-with-c
bool is_number(const std::string& s)
{
    std::string::const_iterator it = s.begin();
    while (it != s.end() && std::isdigit(*it)) ++it;
    return !s.empty() && it == s.end();
}
/*
__declspec(dllexport) void removal(char* to_delete){
    delete [] to_delete;
}
 */
char* parser(char* ingredient_str_char)
{
    string ingredient_str = string(ingredient_str_char);
    string ingredient = "";

    replace(ingredient_str.begin(), ingredient_str.end(),'-', ' ');
    replace(ingredient_str.begin(), ingredient_str.end(),':', ' ');
    replace(ingredient_str.begin(), ingredient_str.end(),';', ' ');
    replace(ingredient_str.begin(), ingredient_str.end(),'/', ' ');
    ingredient_str.erase(remove(ingredient_str.begin(), ingredient_str.end(),'\''));
    ingredient_str.erase(remove(ingredient_str.begin(), ingredient_str.end(),'\"'));
    ingredient_str.erase(remove(ingredient_str.begin(), ingredient_str.end(),'.'));
    ingredient_str.erase(remove(ingredient_str.begin(), ingredient_str.end(),'&'));
    ingredient_str.erase(remove(ingredient_str.begin(), ingredient_str.end(),'('));
    ingredient_str.erase(remove(ingredient_str.begin(), ingredient_str.end(),')'));
    ingredient_str.erase(remove(ingredient_str.begin(), ingredient_str.end(),'['));
    ingredient_str.erase(remove(ingredient_str.begin(), ingredient_str.end(),']'));
    vector<string> split_words = word_2_vector(ingredient_str);


    for(int i = 0; i < split_words.size(); i++){
        transform(split_words[i].begin(), split_words[i].end(), split_words[i].begin(), ::tolower);
        if(is_number(split_words[i]))
            continue;
        else if(inVector(split_words[i], description_exceptions))
        {
            split_words[i].append(" ");
            ingredient.append(split_words[i]);
        }
        else if(split_words[i].find(',') != string::npos)
        {
            split_words[i].pop_back();
            ingredient.append(split_words[i]);
            break;
        }
        else if(split_words[i] == "or")
            continue;
        else if(split_words[i] == "and") //Needs work
        {
            //if(ingredient[ingredient.length() -1] == ' ')
              //  ingredient.pop_back();
        }
        else if(inVector(split_words[i], measurementUnits))
            continue;
        else if(inVector(split_words[i], measurementUnitsAbbreviations))
            continue;
        else if(inVector(split_words[i], descriptions))
            continue;
        else if(inVector(split_words[i], numbers))
            continue;
        else if(inVector(split_words[i], brands))
            continue;
        else if(inVector(split_words[i], modifier))
            continue;
        else if(inVector(split_words[i], precedingAdverbs))
            continue;
        else if(inVector(split_words[i], succeedingAdverbs))
            continue;
        else if(inVector(split_words[i], prepositions))
            continue;
        else if(inVector(split_words[i], descriptionsWithPredecessor))
            continue;
        else if(inVector(split_words[i], unnecessaryDescriptions))
            continue;
        else if(inVector(split_words[i], specialCharacters)) //Needs work
            continue;
        else
            ingredient = ingredient + split_words[i] + ' ';
    }

    //if(ingredient[ingredient.length() -1] == ' ')
        //ingredient.pop_back();

    char * cstr = new char [ingredient.length()+1];
    strcpy(cstr, ingredient.c_str());

    return cstr;
}
