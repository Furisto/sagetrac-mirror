#include <stdint.h>

typedef uint64_t uint64;
typedef unsigned int uint;

typedef Automate Automaton;
typedef NAutomate NAutomaton;

struct Dict
{
	int *e;
	int n;
};
typedef struct Dict Dict;

int hashAutomaton (Automaton a);
bool findWord (Automaton a, Dict *w, bool verb); //rend un mot dans le langage de a
Dict NewDict (int n);
void FreeDict (Dict *d);
void printDict (Dict d);
void dictAdd (Dict *d, int e); //ajoute un élément au dictionnaire (même s'il était déjà présent)
Automaton NewAutomaton (int n, int na);
void ReallocNAutomaton (NAutomaton *a, int n);
void FreeAutomaton (Automaton *a);
void FreeAutomates (Automate* a, int n);
void FreeNAutomaton (NAutomaton *a);
Automaton CopyAutomaton (Automaton a, int nalloc, int naalloc);
Automaton PieceAutomaton (Automaton a, int *w, int n, int e); //donne un automate reconnaissant w(w^(-1)L) où L est le langage de a partant de e
void init (Automaton *a);
void printAutomaton (Automaton a);
void plotTikZ (Automaton a, const char **labels, const char *graph_name, double sx, double sy);
bool equalsAutomaton (Automaton a1, Automaton a2); //détermine si les automates sont les mêmes (différents si états permutés)
int contract (int i1, int i2, int n1);
int geti1 (int c, int n1);
int geti2 (int c, int n1);
Automaton Product (Automaton a1, Automaton a2, Dict d, bool verb);
void AddEtat (Automaton *a, bool final);

struct Etats
{
	int *e;
	int n;	
};
typedef struct Etats Etats;

Etats NewEtats (int n);
void FreeEtats (Etats e);
void initEtats (Etats e);
void printEtats (Etats e);
bool equals (Etats e1, Etats e2);
Etats copyEtats (Etats e);

struct ListEtats
{
	Etats *e;
	int n;
};
typedef struct ListEtats ListEtats;

void printListEtats (ListEtats l);
bool AddEl (ListEtats *l, Etats e, int* res); //ajoute un élément s'il n'est pas déjà dans la liste
void AddEl2 (ListEtats *l, Etats e); //ajoute un élément même s'il est déjà dans la liste

////////////////
struct Etats2
{
	uint n;
	uint64 *e;
};
typedef struct Etats2 Etats2;

Etats2 NewEtats2 (int n);
void FreeEtats2 (Etats2 e);
void initEtats2 (Etats2 e);
void printEtats2 (Etats2 e);
bool isNullEtats2 (Etats2 e);
bool equalsEtats2 (Etats2 e1, Etats2 e2);
bool hasEtats2 (Etats2 e, uint64 i);
Etats2 copyEtats2 (Etats2 e);
void addEtat (Etats2 *e, uint64 i);

struct ListEtats2
{
	Etats2 *e;
	int n; //nombre d'états
	int na; //mémoire allouée
};
typedef struct ListEtats2 ListEtats2;

ListEtats2 NewListEtats2(int n, int na);
void ReallocListEtats2(ListEtats2* l, int n, bool marge);
void FreeListEtats2 (ListEtats2* l);
void printListEtats2 (ListEtats2 l);
//bool AddEtats2 (ListEtats2 *l, Etats2 e, int* res); //ajoute un élément s'il n'est pas déjà dans la liste
//void addEtats2 (ListEtats2 *l, Etats2 e); //ajoute un élément même s'il est déjà dans la liste
////////////////

//inverse d'un dictionnaire
struct InvertDict
{
	Dict *d;
	int n;
};
typedef struct InvertDict InvertDict;

InvertDict NewInvertDict (int n);
InvertDict invertDict (Dict d);
void FreeInvertDict (InvertDict id);
void printInvertDict (InvertDict id);
void putEtat (Etats *f, int ef); ////////////////////////////////// à améliorer !!!!
void Determinise_rec (Automaton a, InvertDict id, Automaton* r, ListEtats* l, bool onlyfinals, bool nof, int niter);
Automaton Determinise (Automaton a, Dict d, bool noempty, bool onlyfinals, bool nof, bool verb);

Automaton DeterminiseN (NAutomaton a, bool puits);

//change l'alphabet en dupliquant des arêtes si nécessaire
//the result is assumed deterministic !!!!
Automaton Duplicate (Automaton a, InvertDict id, int na2, bool verb);

//ajoute tous les mots qui se complètent en un mot du langage en ajoutant des 0 à la fin
void ZeroComplete (Automaton a, int l0, bool verb);

//retire tous les états à partir desquels il n'y a pas de chemin infini
Automaton emonde_inf (Automaton a, bool verb);

//Compute the transposition, assuming it is deterministic
Automaton TransposeDet (Automaton a);

//Compute the transposition
NAutomaton Transpose (Automaton a);

//Tarjan algorithm
int StronglyConnectedComponents (Automaton a, int *res);

//retire tous les états non accessible ou non co-accessible
Automaton emonde (Automaton a, bool verb);

//retire tous les états non accessible
Automaton emondeI (Automaton a, bool verb);

Automaton SubAutomaton (Automaton a, Dict d, bool verb);

//permute les labels des arêtes
//l donne les anciens indices à partir des nouveaux
Automaton Permut (Automaton a, int *l, int na, bool verb);
//idem mais SUR PLACE
void PermutOP (Automaton a, int *l, int na, bool verb);

//minimisation par l'algo d'Hopcroft
//voir "Around Hopcroft’s Algorithm" de Manuel BACLET and Claire PAGETTI
Automaton Minimise (Automaton a, bool verb);

void DeleteVertexOP (Automaton *a, int e);
Automaton DeleteVertex (Automaton a, int e);

//détermine si les langages des automates sont les mêmes
//le dictionnaires donne les lettres de a2 en fonction de celles de a1 (-1 si la lettre de a1 ne correspond à aucune lettre de a2). Ce dictionnaire est supposé inversible.
//if minimized is true, the automaton a1 and a2 are assumed to be minimal.
bool equalsLangages (Automaton *a1, Automaton *a2, Dict a1toa2, bool minimized, bool verb);

//détermine si le langage de l'automate a1 est inclus dans celui de a2
//le dictionnaires donne les lettres de a2 en fonction de celles de a1 (-1 si la lettre de a1 ne correspond à aucune lettre de a2). Ce dictionnaire est supposé inversible.
//if emonded is true, the automaton a1 and a2 are assumed to be emonded.


//détermine si les langages des automates ont une intersection non vide
//le dictionnaires donne les lettres de a2 en fonction de celles de a1 (-1 si la lettre de a1 ne correspond à aucune lettre de a2). Ce dictionnaire est supposé inversible.
//if emonded is true, the automaton a1 and a2 are assumed to be emonded otherwise it emondes.
//bool intersectLangage (Automaton *a1, Automaton *a2, Dict a1toa2, bool emonded, bool verb);

//détermine si l'intersection est vide ou non
bool Intersect (Automaton a1, Automaton a2, bool verb);

//détermine si l'on a inclusion des langages
bool Included (Automaton a1, Automaton a2, bool emonded, bool verb);

//détermine si le langage de l'automate est vide
bool emptyLangage (Automaton a);

//determine if the automaton is complete (i.e. with his hole state)
bool IsCompleteAutomaton (Automaton a);

//complete the automaton (i.e. add a hole state if necessary)
bool CompleteAutomaton (Automaton *a);

//copy the automaton with a new bigger alphabet
Automaton BiggerAlphabet (Automaton a, Dict d, int nna);


