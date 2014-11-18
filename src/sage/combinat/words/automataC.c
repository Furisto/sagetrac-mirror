#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "Automaton.h"
#include "automataC.h"

/*
static PyObject *DAError;

static PyMethodDef dautomataMethods[] =
{
    {"system",  system, METH_VARARGS,
     "Execute a shell command."},
    {NULL, NULL, 0, NULL}        // Sentinel
};

PyMODINIT_FUNC initdautomata(void)
{
    PyObject *m;

    m = Py_InitModule("dautomata", dautomataMethods);
    if (m == NULL)
        return;

    DAError = PyErr_NewException("dautomata.error", NULL, NULL);
    Py_INCREF(DAError);
    PyModule_AddObject(m, "error", DAError);
}
*/

typedef Automate Automaton;

Dict NewDict (int n)
{
	Dict r;
	r.n = n;
	if (n == 0)
		return r;
	r.e = (int *)malloc(sizeof(int)*n);
	if (!r.e)
	{
		printf("Out of memory !\n");
		exit(15);
	}
	int i;
	for (i=0;i<n;i++)
	{
		r.e[i] = -1;
	}
	return r;
}

void FreeDict (Dict d)
{
	if (d.n == 0)
		return;
	free(d.e);
}

void printDict (Dict d)
{
	int i;
	printf("[ ");
	for (i=0;i<d.n;i++)
	{
		printf("%d ", d.e[i]);
	}
	printf("]\n");
}

//ajoute un élément au dictionnaire (même s'il était déjà présent)
void dictAdd (Dict *d, int e)
{
	d->n++;
	d->e = (int *)realloc(d->e, sizeof(int)*d->n);
	if (!d->e)
	{
		printf("Out of memory !");
		exit(1);
	}
	d->e[d->n-1] = e;
}

#define DISP_MEMORY	false

Automaton NewAutomaton (int n, int na)
{
#if DISP_MEMORY
	printf("New %d...\n", n);
#endif
	Automaton a;
	a.n = n;
	a.na = na;
	if (n == 0)
	{
		a.i = -1;
		a.e = NULL;
		return a;
	}
	a.e = (Etat *)malloc(sizeof(Etat)*n);
	//a.nalloc = n;
	if (!a.e)
	{
		printf("Out of memory !");
		exit(6);
	}
	int i;
	for (i=0;i<n;i++)
	{
		a.e[i].f = (int *)malloc(sizeof(int)*na);
		if (!a.e[i].f)
		{
			printf("Out of memory !");
			exit(7);
		}
	}
	return a;
}

void FreeAutomaton (Automaton *a)
{
#if DISP_MEMORY
	printf("Free %d ...\n", a->n);
#endif
	//if (a.nalloc == 0 || a.n==0)
	if (a->n == 0)
		return;
	int i;
	for (i=0;i<a->n;i++)
	{
		free(a->e[i].f);
	}
	free(a->e);
	//a.nalloc = 0;
	a->n = 0;
}

void ReallocAutomaton (Automaton *a, int n)
{	//////////////////fonction BUGUéE !!!!!!!!!!!!!!!!!!!
	int i;
	if (a->n > n)
	{ //libère les états à supprimmer
		printf("dealloc %d -> %d...\n", a->n, n);
		for (i=n;a->n;i++)
		{
			free(a->e[i].f);
		}
		a->e = (Etat*)realloc(a->e, n);
		if (!a->e)
		{
			printf("Out of memory !");
			exit(29);
		}
	}else
	{ //aloue les nouveaux états
		printf("realloc %d -> %d...\n", a->n, n);
		a->e = (Etat*)realloc(a->e, n);
		if (!a->e)
		{
			printf("Out of memory !");
			exit(27);
		}
		for (i=a->n;i<n;i++)
		{
			a->e[i].f = malloc(sizeof(int)*a->na);
		}
	}
	if (a->i >= n)
		a->i = -1;
	a->n = n;
	/*
	int i;
	if (n > a->n)
	{
		if (n > a->nalloc)
		{
			a->e = (Etat *)realloc(a->e, sizeof(Etat)*n*2);
			if (!a->e)
			{
				printf("Out of memory !");
				exit(29);
			}
			a->nalloc = 2*n;
		}
		
		for (i=a->n;i<n;i++)
		{
			a->e[i].f = (int *)malloc(sizeof(int)*a->na);
			if (!a->e[i].f)
			{
				printf("Out of memory !");
				exit(27);
			}
		}
	}else
	{
		if (n < a->nalloc/2)
		{
			for (i=n;i<a->n;i++)
			{
				free(a->e[i].f);
			}
			a->e = (Etat *)realloc(a->e, sizeof(Etat)*n);
			a->nalloc = n;
		}
	}
	a->n = n;
	*/
}

Automaton CopyAutomaton (Automaton a, int nalloc, int naalloc)
{
	//a.n, a.na
	Automaton r = NewAutomaton(nalloc, naalloc);
	int i,j;
	for (i=0;i<a.n;i++)
	{
		r.e[i].final = a.e[i].final;
		for (j=0;j<a.na;j++)
		{
			r.e[i].f[j] = a.e[i].f[j];
		}
	}
	r.i = a.i;
	return r;
}

void init (Automaton *a)
{
	int i,j;
	a->i = -1;
	for (i=0;i<a->n;i++)
	{
		a->e[i].final = false;
		for (j=0;j<a->na;j++)
		{
			a->e[i].f[j] = -1;
		}
	}
}

void printAutomaton (Automaton a)
{
	printf("Automate ayant %d états, %d lettres.\n", a.n, a.na);
	int i, j;
	for (i=0;i<a.n;i++)
	{
		for (j=0;j<a.na;j++)
		{
			if (a.e[i].f[j] != -1)
			{
				printf("%d --%d--> %d\n", i, j, a.e[i].f[j]);
			}
		}
	}
	printf("Etat initial %d.\n", a.i);
}

void plotTikZ (Automaton a, const char **labels, const char *graph_name, double sx, double sy)
{
	bool verb = false;
	const char *name = "/Users/mercat/Desktop/a.dot";
	char tamp[1024];
	FILE *f = fopen(name, "w");
	if (!f)
	{
		printf("Impossible d'ouvrir le fichier a.dot !\n");
		return;
	}
	
	if (verb)
		printf("start...\n");
	fprintf(f, "digraph %s\n{\n"\
	"	node[fontsize=20]"\
	"	edge[fontsize=20, arrowhead = open]"\
	"	rankdir = LR;\n"\
	"	size = \"%lf, %lf\";\n"\
	"	center = 1;\n"\
	"	nodesep = \"0.2\"\n", graph_name, sx, sy);
//	"	ranksep = \"0.4 equally\";\n", graph_name);
//	"	rotate = -90\n"\
//	"	orientation=landscape\n"\
//	"orientation = Landscape\n");
	if (verb)
		printf("write...\n");
    
    fprintf(f, "	\n");
    int i,j;
    for (i=0;i<a.n;i++)
    {
    	fprintf(f, "	%d [shape=", i);
    	if (a.e[i].final)
    		fprintf(f, "doublecircle");
    	else
    		fprintf(f, "circle");
    	fprintf(f, ", style=");
    	if (i == a.i)
    		fprintf(f, "bold");
    	else
    		fprintf(f, "solid");
    	fprintf(f, ", fontsize=20, margin=0]\n");
    }
    fprintf(f, "	\n");
    for (i=0;i<a.n;i++)
    {
    	for (j=0;j<a.na;j++)
    	{
    		if (a.e[i].f[j] != -1)
	    		fprintf(f, "	%d -> %d [label=\"%s\"]\n", i, a.e[i].f[j], labels[j]);
    	}
    }
    fprintf(f, "}\n");
	
	fclose(f);
	if (verb)
		printf("draw...\n");
	sprintf(tamp, "dot %s -Gname -Tsvg > output%d%d.svg", name, time(NULL), clock());
	system(tamp);
}

//determine if the automaton is complete (i.e. with his hole state)
bool IsCompleteAutomaton (Automaton a)
{
	int i,j;
	for (i=0;i<a.n;i++)
	{
		for (j=0;j<a.na;j++)
		{
			if (a.e[i].f[j] == -1)
				return false;
		}
	}
	return true;
}

//complete the automaton (i.e. add a hole state if necessary)
//return true iff a state was added
bool CompleteAutomaton (Automaton *a)
{
	int ne = a->n; //nouvel état
	int i,j;
	bool add_etat = false;
	for (i=0;i<ne;i++)
	{
		for (j=0;j<a->na;j++)
		{
			if (a->e[i].f[j] == -1)
			{
				a->e[i].f[j] = ne;
				add_etat = true;
			}
		}
	}
	if (a->i == -1)
	{
		a->i = ne;
		add_etat = true;
	}
	if (!add_etat)
		return false;
	AddEtat(a, false); //ajoute l'état puits
	for (j=0;j<a->na;j++)
	{
		a->e[ne].f[j] = ne;
	}
	if (a->i == -1)
		a->i = ne;
	return true;
}

//détermine si les automates sont les mêmes (différents si états permutés)
bool equalsAutomaton (Automaton a1, Automaton a2)
{
	if (a1.n != a2.n || a1.na != a2.na)
		return false;
	int i, j;
	for (i=0;i<a1.n;i++)
	{
		for (j=0;j<a1.na;j++)
		{
			if (a1.e[i].f[j] != a2.e[i].f[j])
				return false;
		}
	}
	return true;
}

//utilisé par equalsLangages
//détermine si les langages des états e1 de a1 et e2 de a2 sont les mêmes
bool equalsLangages_rec (Automaton a1, Automaton a2, Dict a1toa2, Dict a2toa1, int e1, int e2)
{
	if (a1.e[e1].final & 2 && a2.e[e2].final & 2)
		return true;
	//indique que le sommet a été vu
	a1.e[e1].final |= 2;
	a2.e[e2].final |= 2;
	//parcours les fils de e1 dans a1
	int i;
	for (i=0;i<a1.na;i++)
	{
		if (a1.e[e1].f[i] != -1)
		{//cette arête dans a1 existe
			if (a1toa2.e[i] != -1)
			{//cette lettre correspond à une lettre dans a2
				if (a2.e[e2].f[a1toa2.e[i]] == -1)
				{//cette arête ne correspond pas à une arête dans a2
					return false;
				}
				equalsLangages_rec(a1, a2, a1toa2, a2toa1, a1.e[e1].f[i], a2.e[e2].f[a1toa2.e[i]]);
			}else
			{
				return false;
			}
		}
	}
	//parcours les fils de e2 dans a2 (pour vérifier qu'il n'y a pas de transition en plus)
	for (i=0;i<a2.na;i++)
	{
		if (a2.e[e2].f[i] != -1)
		{//cette arête dans a2 existe
			if (a2toa1.e[i] != -1)
			{//cette lettre correspond à une lettre dans a1
				if (a1.e[e1].f[a2toa1.e[i]] == -1)
				{//cette arête ne correspond pas à une arête dans a1
					return false;
				}
			}else
			{
				return false;
			}
		}
	}
	return true;
}

//détermine si les langages des automates sont les mêmes
//le dictionnaires donne les lettres de a2 en fonction de celles de a1 (-1 si la lettre de a1 ne correspond à aucune lettre de a2). Ce dictionnaire est supposé inversible.
//if minimized is true, the automaton a1 and a2 are assumed to be minimal.
bool equalsLangages (Automaton *a1, Automaton *a2, Dict a1toa2, bool minimized)
{
	int i;
	if (!minimized)
	{
		//minimise les automates
		Automaton a3 = Minimise(*a1, false);
		FreeAutomaton(a1);
		*a1 = a3;
		a3 = Minimise(*a2, false);
		FreeAutomaton(a2);
		*a2 = a3;
	}
	//inverse le dictionnaire
	Dict a2toa1 = NewDict(a2->na);
	for (i=0;i<a1toa2.n;i++)
	{
		a2toa1.e[a1toa2.e[i]] = i;
	}
	//
	bool res = equalsLangages_rec(*a1, *a2, a1toa2, a2toa1, a1->i, a2->i);
	//remet les états finaux
	for (i=0;i<a1->n;i++)
	{
		a1->e[i].final &= 1;
	}
	for (i=0;i<a2->n;i++)
	{
		a2->e[i].final &= 1;
	}
	return res;
}

//utilisé par emptyLangage
//détermine si le langage de l'état e est vide
bool emptyLangage_rec (Automaton a, int e)
{
	if (a.e[e].final)
		return false;
	//indique que le sommet a été vu
	a.e[e].final |= 2;
	//parcours les fils
	int i;
	for (i=0;i<a.na;i++)
	{
		if (a.e[e].f[i] != -1)
		{
			if (a.e[a.e[e].f[i]].final & 2)
				continue; //ce fils a déjà été vu
			if (!emptyLangage_rec(a, a.e[e].f[i]))
				return false;
		}
	}
	return true;
}

//détermine si le langage de l'automate est vide
bool emptyLangage (Automaton a)
{
	if (a.i == -1)
		return true;
	bool res = emptyLangage_rec(a, a.i);
	//remet les états finaux
	int i;
	for (i=0;i<a.n;i++)
	{
		a.e[i].final &= 1;
	}
	return res;
}

inline int contract (int i1, int i2, int n1)
{
	return i1+n1*i2;
}

inline int geti1 (int c, int n1)
{
	return c%n1;
}

inline int geti2 (int c, int n1)
{
	return c/n1;
}

void Product_rec(Automaton r, int i1, int i2, Automaton a1, Automaton a2, Dict d)
{
	//printf("Product_rec %d %d...\n", i1, i2);
	int i,j;
	int e1, e2;
	int a;
	Etat *current = &r.e[contract(i1, i2, a1.n)];
	int *next;
	current->final = true; //indicate that the state has been visited
	for (i=0;i<a1.na;i++)
	{
		e1 = a1.e[i1].f[i];
		if (e1 < 0)
			continue;
		for (j=0;j<a2.na;j++)
		{
			e2 = a2.e[i2].f[j];
			a = d.e[contract(i,j,a1.na)];
			next = &current->f[a];
			if (a != -1)
			{
				if (e2 < 0)
					*next = -1;
				else
				{
					//printf("(%d, %d)=%d -> (%d,%d)=%d\n", i, j, a, e1, e2, contract(e1, e2, a1.n));
					*next = contract(e1, e2, a1.n);
					if (!r.e[*next].final)
						Product_rec(r, e1, e2, a1, a2, d);
				}
			}
		}
	}
}

Automaton Product(Automaton a1, Automaton a2, Dict d)
{
	//printf("a1.na=%d, a2.na=%d\n", a1.na, a2.na);
	//compte le nombre de lettres de l'alphabet final
	int i, na=0;
	for (i=0;i<d.n;i++)
	{
		if (d.e[i] >= na)
			na = d.e[i]+1;
	}
	Automaton r = NewAutomaton(a1.n*a2.n, na);
	init(&r);
	if (a1.i == -1 || a2.i == -1)
	{
		r.i = -1;
		return r;
	}
	r.i = contract(a1.i, a2.i, a1.n);
	Product_rec(r, a1.i, a2.i, a1, a2, d);
	//met les états finaux
	for (i=0;i<r.n;i++)
	{
		r.e[i].final = a1.e[geti1(i, a1.n)].final && a2.e[geti2(i, a1.n)].final;
	}
	return r;
}

void AddEtat (Automaton *a, bool final)
{
	/**/
	a->n++;
	a->e = (Etat *)realloc(a->e, sizeof(Etat)*a->n);
	if (!a->e)
	{
		printf("Out of memory !");
		exit(2);
	}
	a->e[a->n-1].f = (int *)malloc(sizeof(int)*a->na);
	if (!a->e[a->n-1].f)
	{
		printf("Out of memory !");
		exit(3);
	}
	/**/
	//ReallocAutomaton(a, a->n+1);
	int i;
	for (i=0;i<a->na;i++)
	{
		a->e[a->n-1].f[i] = -1;
	}
	a->e[a->n-1].final = final;
}

Etats NewEtats (int n)
{
	Etats e;
	e.n = n;
	e.e = (int *)malloc(sizeof(int)*n);
	if (!e.e)
	{
			printf("Out of memory !");
		exit(7);
	}
return e;
}

void FreeEtats (Etats e)
{
	free(e.e);
}

void initEtats (Etats e)
{
	int i;
	for (i=0;i<e.n;i++)
	{
		e.e[i] = 0;
	}
}

void printEtats (Etats e)
{
	int i;
	printf("[ ");
	for (i=0;i<e.n;i++)
	{
		printf("%d ", e.e[i]);
		fflush(stdout);
	}
	printf("]\n");
}

bool equals (Etats e1, Etats e2)
{
	if (e1.n != e2.n)
		return false;
	int i;
	for (i=0;i<e1.n;i++)
	{
		if (e1.e[i] != e2.e[i])
			return false;
	}
	return true;
}

Etats copy (Etats e)
{
	Etats r = NewEtats(e.n);
	int i;
	for (i=0;i<e.n;i++)
	{
		r.e[i] = e.e[i];
	}
	return r;
}

void printListEtats (ListEtats l)
{
	int i;
	for (i=0;i<l.n;i++)
	{
		printf("%d : ", i);
		printEtats(l.e[i]);
	}
}

//ajoute un élément s'il n'est pas déjà dans la liste
bool AddEl (ListEtats *l, Etats e, int* res)
{
	int i;
	for (i=0;i<l->n;i++)
	{
		if (equals(l->e[i], e))
		{
			if (res)
				*res = i;
			return false;
		}
	}
	//ajoute l'élément
	l->n++;
	l->e = (Etats*)realloc(l->e, sizeof(Etats)*l->n);
	if (!l->e)
	{
		printf("Out of memory !");
		exit(4);
	}
	l->e[l->n-1] = copy(e);
	if (res)
		*res = l->n-1;
	return true;
}

//ajoute un élément même s'il est déjà dans la liste
void AddEl2 (ListEtats *l, Etats e)
{
	//ajoute l'élément
	l->n++;
	l->e = (Etats*)realloc(l->e, sizeof(Etats)*l->n);
	if (!l->e)
	{
		printf("Out of memory !");
		exit(5);
	}
	l->e[l->n-1] = copy(e);
}

Dict* lhash;
int nhash = 10000019;

void AllocHash ()
{
	lhash = (Dict*)malloc(sizeof(Dict)*nhash);
	if (!lhash)
	{
			printf("Out of memory !");
		exit(8);
	}
	int i;
	for (i=0;i<nhash;i++)
	{
		lhash[i].e = NULL;
		lhash[i].n = 0;
	}
}

void FreeHash ()
{
	free(lhash);
}

int hash (Etats e)
{
	int i;
	int h = 1;
	for (i=0;i<e.n;i++)
	{
		h *= 2;
		h += e.e[i];
		h %= nhash;
	}
	return h;
}

//ajoute l'élément s'il n'est pas déjà dans la table de hashage
bool add (const ListEtats *l, Etats e, int* nf)
{
	int h = hash(e);
	
	//printf("hash = %d, n=%d, ", h, lhash[h].n);
	//printEtats(e);
	
	int i, v;
	for (i=0;i<lhash[h].n;i++)
	{
		////////verif
		if (lhash[h].e[i] >= l->n)
		{
			printf("***************\nErreur : élément de la table de hachage trop grand !!!\n****************\n");
		}
		/////////////
		v = lhash[h].e[i];
		if (nf)
			*nf = v;
		if (v < 0)
			return false;
		if (equals(l->e[v], e))
		{
			//printf("equals !\n");
			return false;
		}
	}
	//ajoute l'élément
	if (nf)
		*nf = l->n;
	//printf("Add dict...\n");
	dictAdd(&lhash[h], l->n);
	return true;
}

InvertDict NewInvertDict (int n)
{
	InvertDict r;
	r.n = n;
	if (n == 0)
		return r;
	r.d = (Dict*)malloc(sizeof(Dict)*n);
	if (!r.d)
	{
		printf("Out of memory !");
		exit(9);
	}
	return r;
}

InvertDict invertDict (Dict d)
{
	//compte le nombre de valeurs différentes (supposées consécutives)
	int i;
	int nv = 0;
	for (i=0;i<d.n;i++)
	{
		if (d.e[i] >= nv)
			nv = d.e[i]+1;
	}
	//printf("nombre d'éléments : %d\n", nv);
	//alloue l'inverse
	InvertDict r;
	r.n = nv;
	r.d = (Dict *)malloc(sizeof(Dict)*nv);
	if (!r.d)
	{
		printf("Out of memory !");
		exit(10);
	}
	//initialise
	for (i=0;i<nv;i++)
	{
		r.d[i].n = 0;
		r.d[i].e = NULL;
	}
	//remplit le dictionnaire
	for (i=0;i<d.n;i++)
	{
		//printf("Add %d %d\n", d.e[i], i);
		if (d.e[i] != -1)
			dictAdd(&r.d[d.e[i]], i);
	}
	return r;
}

void FreeInvertDict (InvertDict id)
{
	if (id.n == 0)
		return;
	int i;
	for (i=0;i<id.n;i++)
	{
		FreeDict(id.d[i]);
	}
	free(id.d);
}

void printInvertDict (InvertDict id)
{
	int i;
	for (i=0;i<id.n;i++)
	{
		printf("%d : ", i);
		printDict(id.d[i]);
	}
}

////////////////////////////////// à améliorer avec une table de hachage !!!!
void putEtat (Etats *f, int ef)
{
	int i;
	for (i=0;i<f->n;i++)
	{
		if (f->e[i] == ef)
			return;
	}
	f->e[f->n] = ef;
	f->n++;
}

//Etats : liste d'états de a
void Determinise_rec (Automaton a, InvertDict id, Automaton *r, ListEtats* l, bool onlyfinals, bool nof, int niter)
{
	int current = l->n-1;
	Etats c = l->e[current];
	//Parcours les fils
	Etats f = NewEtats(a.n);
	int nf;
	Etat e;
	int i,j,k;
	int ef;
	bool final;
	
	//printf("%d\n", niter);
	//printf("l = ");
	//printListEtats(*l);
	//printf("c = ");
	//printEtats(c);
	
	for (i=0;i<id.n;i++) //parcours les lettres du nouvel alphabet
	{
		//remplit f (liste d'états de a correspondant à l'état de r sur lequel on tombe)
		f.n = 0;
		final = false;
		for (j=0;j<c.n;j++) //parcours les états de la liste
		{
			e = a.e[c.e[j]]; //état correspondant
			for (k=0;k<id.d[i].n;k++) //parcours les lettres originales correspondant à la nouvelle lettre choisie
			{
				ef = e.f[id.d[i].e[k]];
				if (ef != -1)
				{
					//vérifie que l'état de a n'est pas déjà dans la liste
					putEtat(&f, ef);
					if (a.e[ef].final)
						final = true;
				}
			}
		}
		if (onlyfinals && !final)
			continue;
		if (nof && final)
			continue;
		//printf("i=%d : f=", i);
		//printEtats(f);
		//teste si l'état a déjà été vu et sinon on le note comme vu
		if (add(l, f, &nf)) //ajoute l'état à la table de hachage si nouveau
		{
			/*
			printf("add %d ", nf);
			printEtats(f);
			printf("from %d ", i);
			printEtats(c);
			*/
			
			//ajoute l'état à la liste
			AddEl2(l, f);
			//ajoute l'état à r
			if (nof)
				final = true;
			AddEtat(r, final);
			//récurrence
			Determinise_rec(a, id, r, l, onlyfinals, nof, niter+1);
		}
		if (nf != -1)
		{
			//ajoute l'arête
			r->e[current].f[i] = nf;
			//printf("Add %d --%d--> %d\n", current, i, nf);
			//printAutomaton(*r);
		}
	}
	FreeEtats(f);
}

Automaton Determinise (Automaton a, Dict d, bool noempty, bool onlyfinals, bool nof, bool verb)
{
	int i;
	
	//increase the stack size
	const rlim_t kStackSize = 32 * 1024 * 1024;   // min stack size = 1024 MB
    struct rlimit rl;
    int result;
    result = getrlimit(RLIMIT_STACK, &rl);
    if (result == 0)
    {
        if (rl.rlim_cur < kStackSize)
        {
        	if (verb)
	        	printf("limite : %d -> %d\n", rl.rlim_cur, kStackSize);
            rl.rlim_cur = kStackSize;
            result = setrlimit(RLIMIT_STACK, &rl);
            if (result != 0)
            {
                fprintf(stderr, "setrlimit returned result = %d\n", result);
            }
        }
    }
    //
    
	if (verb)
	{
		if (onlyfinals)
			printf("onlyfinals\n");
		if (nof)
			printf("nof\n");
		if (noempty)
			printf("noempty\n");
		printf("Dictionnaire : ");
		printDict(d);
	}
	
	//calcule l'inverse du dictionnaire
	InvertDict id = invertDict(d);
	if (verb && id.n == d.n)
	{
		printf("Le dictionnaire est inversible : déterminisation triviale !\n");
	}
	
	if (verb)
	{
		printf("Dictionnaire inverse :\n");
		printInvertDict(id);
	}
	
	//alloue la table de hachage
	AllocHash();
	//met l'ensemble vide dans la table de hachage si cet état n'est pas souhaité dans r
	if (noempty)
	{
		Etats e = NewEtats(0); //ensemble vide
		int h = hash(e);
		if (verb)
			printf("hash vide : %d\n", h);
		dictAdd(&lhash[h], -1);
	}
	
	//initialise l'automate résultat avec juste l'état initial
	if (verb)
		printf("Init r...\n");
	Automaton r;
	if (a.i == -1)
	{
		if (verb)
			printf("Pas d'état initial !\n");
		if (nof)
		{
			r = NewAutomaton(1, id.n);
			r.i = 0;
			r.e[0].final = true;
			for (i=0;i<id.n;i++)
			{
				r.e[0].f[i] = 0;
			}
		}else
			r = NewAutomaton(0, id.n);
		return r;
	}
	r.n = 1;
	r.na = id.n;
	r.i = 0;
	r.e = (Etat *)malloc(sizeof(Etat));
	if (!r.e)
	{
		printf("Out of memory !");
		exit(11);
	}
	if (nof)
		r.e[0].final = true;
	else
		r.e[0].final = a.e[a.i].final;
	r.e[0].f = (int *)malloc(sizeof(int)*r.na);
	if (!r.e[0].f)
	{
		printf("Out of memory !");
		exit(12);
	}
	for (i=0;i<r.na;i++)
	{
		r.e[0].f[i] = -1;
	}
	if (verb)
		printAutomaton(r);
		
	//initialise la liste des états du nouvel automate et la table de hachage
	//(cette liste sert à numéroter par des nombres consécutifs les états du nouvel automate qui sont des listes d'états de a)
	if (verb)
		printf("Init l...\n");
	ListEtats l;
	l.n = 0;
	l.e = NULL;
	Etats e = NewEtats(1);
	e.e[0] = a.i; //l'état initial du nouvel automate est la liste des états initiaux (ici de cardinal 1)
	//printf("add...\n");
	add(&l, e, NULL);
	//printf("Add...\n");
	AddEl2(&l, e);
	
	//initialise la table de hachage
	bool b = add(&l, l.e[0], NULL); //ajoute l'état initial à la table de hachage
	//printf("b = %d\n", b);
	if (verb)
		printListEtats(l);
	
	if (verb)
		printf("Récurrence...\n");
	
	Determinise_rec(a, id, &r, &l, onlyfinals, nof, 0);
	
	if (verb)
		printf("Free...\n");
	
	FreeInvertDict(id);
	FreeHash();
	
	//printf("1ere transition : ");
	//fflush(stdout);
	//printf("%d\n", r.e[0].f[0]);
	
	//printAutomaton(r);
	
	return r;
}

//change l'alphabet en dupliquant des arêtes si nécessaire
//the result is assumed deterministic !!!!
Automaton Duplicate (Automaton a, InvertDict id, int na2, bool verb)
{
	if (verb)
	{
		printf("NewAutomaton(%d, %d)\n", a.n, na2);
	}
	Automaton r = NewAutomaton(a.n, na2);
	int i,j,k;
	r.i = a.i;
	for (i=0;i<r.n;i++)
	{
		r.e[i].final = a.e[i].final;
		for (j=0;j<r.na;j++)
		{
			r.e[i].f[j] = -1;
		}
		for (j=0;j<a.na;j++)
		{
			//printf("i=%d, j=%d, n=%d\n", i, j, id.d[j].n);
			for (k=0;k<id.d[j].n;k++)
			{
				r.e[i].f[id.d[j].e[k]] = a.e[i].f[j];
			}
		}
	}
	return r;
}

int compteur = 0;
bool emonde_inf_rec (Automaton a, int etat)
{
	int i, f;
	bool cycle = false;
	a.e[etat].final = 1; //note que le sommet est en cours d'étude
	for (i=0;i<a.na;i++)
	{
		f = a.e[etat].f[i];
		if (f == -1)
			continue;
		if (a.e[f].final == 1)
			cycle = true; //le sommet fait parti d'un cycle
		if (a.e[f].final == 0)
		{
			if (emonde_inf_rec(a, f))
				cycle = true; //le sommet permet d'atteindre un cycle
		}
	}
	if (!cycle)
		a.e[etat].final = 2; //indique que le sommet ne doit pas être gardé (mais a été vu)
	else
		compteur++; //compte le nombre de sommets à garder
	return cycle;
}

/*
void emonde_inf_rec2 (Automaton a, Automaton r, int *l, int etat)
{
	int i, f;
	int current = compteur;
	a.e[etat].final = 0; //note que le sommet a été vu
	l[etat] = current; //correspondance entre les nouveaux et les anciens états
	compteur++;
	for (i=0;i<a.na;i++)
	{
		r.e[current].f[i] = -1; //valeur par défaut
		f = a.e[etat].f[i];
		if (f == -1)
			continue;
		if (a.e[f].final == 1) //le sommet n'a encore jamais été vu et doit être gardé
		{
			//appel récursif
			emonde_inf_rec2(a, r, l, f);
		}
		if (a.e[f].final != 2) //le sommet doit être gardé, donc l'arête vers ce sommet aussi
		{
			//ajoute l'arête
			r.e[current].f[i] = l[f];
		}
	}
}
*/

//retire tous les états à partir desquels il n'y a pas de chemin infini
Automaton emonde_inf (Automaton a, bool verb)
{
	int *l = (int *)malloc(sizeof(int)*a.n);
	if (!l)
	{
		printf("Out of memory !\n");
		exit(25);
	}
	
	//commence par établir la liste des sommets de a à garder
	int i;
	int *finaux = (int *)malloc(sizeof(int)*a.n);
	if (!finaux)
	{
		printf("Out of memory !\n");
		exit(13);
	}
	for (i=0;i<a.n;i++)
	{
		finaux[i] = a.e[i].final;
		a.e[i].final = 0; //états non vus
	}
	if (verb)
		printf("récurrence...\n");
	compteur = 0;
	if (a.i != -1)
		emonde_inf_rec (a, a.i);
	//printf("compteur = %d\n", compteur);
	
	if (verb)
	{
		printf("compteur=%d\n", compteur);
		printf("comptage...\n");
	}
	
	//compte le nombre de sommets à garder
	int cpt = 0;
	for (i=0;i<a.n;i++)
	{
		if (a.e[i].final & 1)
		{ //nouveau sommet à ajouter
			l[i] = cpt;
			cpt++;
		}else
			l[i] = -1;
	}
	
	if (verb)
		printf("cpt = %d\n", cpt);
	
	//créé le nouvel automate
	int j, f;
	Automaton r = NewAutomaton(cpt, a.na);
	for (i=0;i<a.n;i++)
	{
		if (l[i] == -1)
			continue;
		for (j=0;j<a.na;j++)
		{
			f = a.e[i].f[j];
			r.e[l[i]].f[j] = -1;
			if (f == -1)
				continue;
			if (l[f] != -1)
			{
				r.e[l[i]].f[j] = l[f];
			}
		}
	}
	
	if (verb)
		printf("états finaux...\n");
	
	//remet les états finaux comme ils étaient
	for (i=0;i<a.n;i++)
	{
		a.e[i].final = finaux[i];
		if (l[i] != -1)
			r.e[l[i]].final = finaux[i];
	}
	
	//état initial
	if (a.i != -1)
		r.i = l[a.i];
	else
		r.i = -1;
	
	/*
	printf("a.n = %d\n", a.n);
	printf("l = [ ");
	for (i=0;i<a.n;i++)
	{
		printf("%d ", l[i]);
		fflush(stdout);
	}
	printf("]\n");
	*/
	free(finaux);
	free(l);
	return r;
}

//Compute the transposition, assuming it is deterministic
Automaton Transpose (Automaton a)
{
	Automaton r = NewAutomaton(a.n, a.na);
	int i,j;
	for (i=0;i<a.n;i++)
	{
		if (a.e[i].final)
			r.i = i;
		if (i == a.i)
			r.e[i].final = true;
		else
			r.e[i].final = false;
		for (j=0;j<a.na;j++)
		{
			r.e[i].f[j] = -1;
		}
	}
	int f;
	for (i=0;i<a.n;i++)
	{
		for (j=0;j<a.na;j++)
		{
			f = a.e[i].f[j];
			if (f != -1)
			{
				//printf("%d --%d--> %d\n", i, j, f);
				r.e[f].f[j] = i;
			}
		}
	}
	return r;
}

int min (int a, int b)
{
	if (a < b)
		return a;
	return b;
}

int compteur2;
void StronglyConnectedComponents_rec(Automaton a, int etat, int *pile, int *m, int *res)
{
	//printf("etat=%d, cpt=%d, cpt2=%d\n", etat, compteur, compteur2);
	int j,f,c;
	pile[compteur] = etat;
	m[etat] = compteur;
	c = compteur;
	a.e[etat].final |= 2; //note que l'état a été vu
	compteur++;
	for (j=0;j<a.na;j++)
	{
		f = a.e[etat].f[j];
		if (f == -1)
			continue;
		//printf("%d --%d--> %d\n", f);
		if (!(a.e[f].final & 2))
		{
			StronglyConnectedComponents_rec(a, f, pile, m, res);
			m[etat] = min(m[etat], m[f]);
		}else if (res[f] == -1)
		{
			m[etat] = min(m[etat], m[f]);
		}
	}
	//printf("m[%d]=%d, c=%d\n", etat, m[etat], c);
	if (m[etat] == c)
	{ //on a une composante fortement connexe
		//dépile la composante
		do
		{
			compteur--;
			res[pile[compteur]] = compteur2;
		}while(pile[compteur] != etat);
		compteur2++;
	}
}

//Tarjan algorithm
int StronglyConnectedComponents (Automaton a, int *res)
{
	int *m = (int *)malloc(sizeof(int)*a.n);
	int *pile = (int *)malloc(sizeof(int)*a.n);
	int i;
	for (i=0;i<a.n;i++)
	{
		res[i] = -1;
	}
	compteur = 0; //compte les éléments ajoutés à la pile
	compteur2 = 0; //compte les composantes fortement connexes
	for (i=0;i<a.n;i++)
	{
		if (res[i] == -1)
			StronglyConnectedComponents_rec(a, i, pile, m, res);
	}
	//remet les états finaux
	for (i=0;i<a.n;i++)
	{
		a.e[i].final &= 1;
	}
	free(pile);
	free(m);
	return compteur2;
}

/*
//rend le sous-automate dont les sommets sont les images par l
//on suppose que les images par l sont des entiers consécutifs partant de 0
//problème : le résultat n'est pas déterministe
Automaton Contract (Automaton a, int *l)
{
	int i, c = 0;
	//compte le nombre de nouveaux sommets
	for (i=0;i<a.n;i++)
	{
		if (l[i] >= c)
			c = l[i]+1;
	}
	//créé le nouvel automate
	Automaton r = NewAutomaton(c, a.na);
	
	/////////////////////////////////////////////Not implemented !!!
	
	return r;
}
*/

//détermine les sommets accessible et co-accessibles
bool emonde_rec (Automaton a, int *l, InvertDict id, int etat)
{
	//printf("emonde_rec %d...\n", etat);
	int i, j, f;
	a.e[etat].final |= 2; //note que le sommet est en cours d'étude
	for (i=0;i<a.na;i++)
	{
		f = a.e[etat].f[i];
		if (f == -1)
			continue;
		if (!(a.e[f].final & 2))
		{ //le sommet n'a pas encore été vu
			emonde_rec(a, l, id, f);
		}
		if ((a.e[f].final & 4) && !(a.e[etat].final & 4))
		{ //on tombe sur un état co-final mais etat n'est pas encore noté co-final
			//propage l'information à la composante fortement connexe
			for (j=0;j<id.d[l[etat]].n;j++)
			{
				a.e[id.d[l[etat]].e[j]].final |= 4;
				//printf("rec : %d co-acc\n", id.d[l[etat]].e[j]);
			}
		}
	}
}

/*
//construit le nouvel automate
void emonde_rec3 (Automaton a, Automaton r, int *l, int etat)
{
	int i, f;
	int current = compteur;
	a.e[etat].final |= 8; //note que le sommet a été vu
	r.e[current].final = a.e[etat].final & 1;
	l[etat] = current; //correspondance entre les nouveaux et les anciens états
	compteur++;
	for (i=0;i<a.na;i++)
	{
		r.e[current].f[i] = -1; //valeur par défaut
		f = a.e[etat].f[i];
		if (f == -1)
			continue;
		if (!(a.e[f].final & 2) || !(a.e[f].final & 4))
			continue; //le sommet ne doit pas être gardé
		if (!(a.e[f].final & 8))
		{ //le sommet n'a encore jamais été vu dans ce parcours
			//appel récursif
			emonde_rec3(a, r, l, f);
		}
		//ajoute l'arête
		r.e[current].f[i] = l[f];
	}
}
*/

//retire tous les états non accessible ou non co-accessible
//
// fonction pas très éfficace : à revoir !!!!!!!!!!!!!!!!!!!!!!!!!!!!
//
Automaton emonde (Automaton a, bool verb)
{
	int i,j,f;
	
	//détermine les états accessibles et co-accessibles
	int *l = (int *)malloc(sizeof(int)*a.n);
	if (!l)
	{
		printf("Out of memory !\n");
		exit(15);
	}
	int ncc = StronglyConnectedComponents(a, l);
	if (verb)
	{
		printf("%d composantes : [", ncc);
		for (i=0;i<a.n;i++)
		{
			printf(" %d", l[i]);
		}
		printf(" ]\n");
	}
	InvertDict id = NewInvertDict(ncc);
	for (i=0;i<ncc;i++)
	{
		id.d[i] = NewDict(0);
	}
	for (i=0;i<a.n;i++)
	{
		if (a.e[i].final)
			a.e[i].final = 1;
		dictAdd(&id.d[l[i]], i);
	}
	if (verb)
		printInvertDict(id);
	//propage les états finaux aux composantes fortements connexes
	for (i=0;i<a.n;i++)
	{
		if (a.e[i].final & 1)
		{ //l'état i est final et accessible mais non encore noté comme co-accessible
			for (j=0;j<id.d[l[i]].n;j++)
			{
				a.e[id.d[l[i]].e[j]].final |= 4;
				if (verb)
					printf("%d co-acc\n", id.d[l[i]].e[j]);
			}
		}
	}
	//
	if (verb)
		printf("rec...\n");
	if (a.i != -1)
		emonde_rec(a, l, id, a.i);
	
	//compte le nombre de sommets à garder
	int cpt = 0;
	for (i=0;i<a.n;i++)
	{
		if ((a.e[i].final & 2) && (a.e[i].final & 4))
		{ //nouveau sommet à ajouter
			l[i] = cpt;
			cpt++;
		}else
			l[i] = -1;
	}
	//printf("compteur = %d\n", compteur);
	
	if (verb)
	{
		printf("l : [");
		for (i=0;i<a.n;i++)
		{
			printf(" %d(%d)", l[i], a.e[i].final);
		}
		printf(" ]\n");
		
		printf("create the new automaton %d %d...\n", cpt, a.na);
	}
	//créé le nouvel automate
	Automaton r = NewAutomaton(cpt, a.na);
	for (i=0;i<a.n;i++)
	{
		if (l[i] == -1)
		{
			if (verb)
				printf("pass %d\n", i);
			continue;
		}
		for (j=0;j<a.na;j++)
		{
			f = a.e[i].f[j];
			r.e[l[i]].f[j] = -1;
			if (f == -1)
				continue;
			if (l[f] != -1)
			{
				r.e[l[i]].f[j] = l[f];
			}
		}
	}
	
	//remet les états finaux de a
	if (verb)
	{
		printf("Etats supprimés : [");
		fflush(stdout);
	}
	for (i=0;i<a.n;i++)
	{
		if (verb)
		{
			if (l[i] == -1)
			{
				printf(" %d(", i);
				if (!(a.e[i].final & 2))
					printf(" non-acc");
				if (!(a.e[i].final & 4))
					printf(" non-co-acc");
				printf(" )");
			}
		}
		a.e[i].final &= 1;
		if (l[i] != -1)
			r.e[l[i]].final = a.e[i].final;
	}
	if (verb)
		printf(" ]\n");
	
	//état initial
	if (a.i != -1)
		r.i = l[a.i];
	else
		r.i = -1;
	
	FreeInvertDict(id);
	free(l);
	return r;
}

//détermine les sommets accessibles
void emondeI_rec (Automaton a, int etat)
{
	int i, f;
	a.e[etat].final |= 2; //note que le sommet est en cours d'étude
	for (i=0;i<a.na;i++)
	{
		f = a.e[etat].f[i];
		if (f == -1)
			continue;
		if (!(a.e[f].final & 2))
		{ //le sommet n'a pas encore été vu
			emondeI_rec(a, f);
		}
	}
}

//retire tous les états non accessible
Automaton emondeI (Automaton a, bool verb)
{
	int i,j,f;
	//détermine les états accessibles
	if (a.i != -1)
		emondeI_rec (a, a.i);
	
	int *l = (int *)malloc(sizeof(int)*a.n);
	if (!l)
	{
		printf("Out of memory !\n");
		exit(15);
	}
	
	//compte le nombre de sommets à garder
	int cpt = 0;
	for (i=0;i<a.n;i++)
	{
		if (a.e[i].final & 2)
		{ //nouveau sommet à ajouter
			l[i] = cpt;
			cpt++;
		}else
			l[i] = -1;
	}
	//printf("compteur = %d\n", compteur);
	
	//créé le nouvel automate
	Automaton r = NewAutomaton(cpt, a.na);
	for (i=0;i<a.n;i++)
	{
		if (l[i] == -1)
			continue;
		for (j=0;j<a.na;j++)
		{
			f = a.e[i].f[j];
			r.e[l[i]].f[j] = -1;
			if (f == -1)
				continue;
			if (l[f] != -1)
			{
				r.e[l[i]].f[j] = l[f];
			}
		}
	}
	
	//remet les états finaux de a
	if (verb)
		printf("Etats supprimés : [");
	for (i=0;i<a.n;i++)
	{
		if (verb)
		{
			if (l[i] == -1)
			{
				printf(" %d(", i);
				if (!(a.e[i].final & 2))
					printf(" non-acc");
				if (!(a.e[i].final & 4))
					printf(" non-co-acc");
				printf(" )");
			}
		}
		a.e[i].final &= 1;
		r.e[l[i]].final = a.e[i].final;
	}
	if (verb)
		printf(" ]\n");
	
	//état initial
	if (a.i != -1)
		r.i = l[a.i];
	else
		r.i = -1;
	
	free(l);
	return r;
}

Automaton SubAutomaton (Automaton a, Dict d, bool verb)
{
	if (verb)
	{
		printf("dict = ");
		printDict(d);
	}
	Automaton r = NewAutomaton(d.n, a.na);
	int *l = (int *)malloc(sizeof(int)*a.n);
	int i,j;
	for (i=0;i<a.n;i++)
	{
		l[i] = -1;
	}
	for (i=0;i<d.n;i++)
	{
		l[d.e[i]] = i;
	}
	
	if (verb)
	{
		printf("l = [");
		for (i=0;i<a.n;i++)
		{
			printf(" %d", l[i]);
		}
		printf(" ]\n");
	}
	
	for (i=0;i<r.n;i++)
	{
		for (j=0;j<r.na;j++)
		{
			r.e[i].f[j] = -1;
		}
	}
	for (i=0;i<a.n;i++)
	{
		if (l[i] != -1)
		{
			r.e[l[i]].final = a.e[i].final;
			for (j=0;j<a.na;j++)
			{
			
				if (a.e[i].f[j] != -1)
					r.e[l[i]].f[j] = l[a.e[i].f[j]];
				else
					r.e[l[i]].f[j] = -1;
			}
		}
	}
	r.i = -1;
	if (a.i != -1)
	{
		a.i = l[a.i];
	}
	free(l);
	return r;
}

/////////////////////////
// 
//  Tout le code qui suit est à tester !!!!!!!!!!!!!!!!!!!
//
/////////////////////////

//permute les labels des arêtes
//l donne les anciens indices à partir des nouveaux
Automaton Permut (Automaton a, int *l, int na, bool verb)
{
	if (verb)
	{
		int i;
		printf("l = [ ");
		for (i=0;i<na;i++)
		{
			printf("%d ", l[i]);
		}
		printf("]\n");
	}
	Automaton r = NewAutomaton(a.n, na);
	int i,j;
	for (i=0;i<a.n;i++)
	{
		for (j=0;j<na;j++)
		{		
			if (l[j] != -1)
				r.e[i].f[j] = a.e[i].f[l[j]];
			else
				r.e[i].f[j] = -1;
		}
		r.e[i].final = a.e[i].final;
	}
	r.i = a.i;
	return r;
}

//permute les labels des arêtes SUR PLACE
//l donne les anciens indices à partir des nouveaux
void PermutOP (Automaton a, int *l, int na, bool verb)
{
	if (verb)
	{
		int i;
		printf("l = [ ");
		for (i=0;i<na;i++)
		{
			printf("%d ", l[i]);
		}
		printf("]\n");
	}
	int *lf = (int*)malloc(sizeof(int)*a.na);
	int i,j;
	for (i=0;i<a.n;i++)
	{
		//sauvegarde les arêtes
		for (j=0;j<a.na;j++)
		{
			lf[j] = a.e[i].f[j];
			a.e[i].f[j] = -1;
		}
		//met les nouvelles
		for (j=0;j<na;j++)
		{		
			if (l[j] != -1)
				a.e[i].f[j] = lf[l[j]];
		}
	}
	free(lf);
}

/////////////////////// the following is an implementation of Hopcroft's algorithm minimization

typedef int Couple[2];

int *partition; //état --> indice
int *partitioni; //indice --> état
int *class; //classe de chaque état
Couple *class_indices; //intervalle d'indices de la classe
int nclass = 0; //nb de classes
Dict **transitioni; //inverse des transitions de l'automate : état, lettre --> liste d'états
int *L; //liste des classes par rapport auxquelles il faut raffiner
int nL; //nb d'éléments de L
int *pt_visited_class; //premier indice non rencontré dans la classe
int *visited_class; //liste des classes visitées dernièrement (utilisé dans split)
int *etats; //états à parcourir

int global_n = 0;
void print_partition ()
{
	int i;
	printf("partition = [");
	for (i=0;i<global_n+1;i++)
	{
		printf(" %d", partition[i]);
	}
	printf(" ]\n");
	printf("partitioni = [");
	for (i=0;i<global_n+1;i++)
	{
		printf(" %d", partitioni[i]);
	}
	printf(" ]\n");
}

void print_classes ()
{
	//affiche la liste des classes
	int l,h,i,j;
	for (i=0;i<nclass;i++)
	{
		printf("classe %d : ", i);
		l = class_indices[i][0];
		h = class_indices[i][1];
		for (j=l;j<h;j++)
		{
			printf("%d ", partitioni[j]);
		}
		printf("\n");
	}
}

//échange les états i et j
inline void swap (int i, int j)
{
	if (i == j)
		return;
	int k = partition[i];
	partition[i] = partition[j];
	partition[j] = k;
	partitioni[k] = j;
	partitioni[partition[i]] = i;
}

void split (int C, int a, bool verb)
{
	//compute the préimage of C
	int i,j,l,h, e, p, lp, ep, cp;
	int nrc = 0; //nombre de classes rencontrées
	l = class_indices[C][0];
	h = class_indices[C][1];
	//copie la liste des sommets à parcourir (au cas où celle-ci soit modifiée pendant le parcours)
	for (i=l;i<h;i++)
	{ //parcours la classe C
		etats[i] = partitioni[i]; //état d'indice i
	}
	for (i=l;i<h;i++)
	{ //parcours la classe C
		e = etats[i]; //état d'indice i
		for (j=0;j<transitioni[e][a].n;j++)
		{ //parcours l'image inverse de l'état e par la lettre a
			p = transitioni[e][a].e[j]; //parent
			cp = class[p]; //classe de p
			if (!pt_visited_class[cp])
			{ //la classe de p n'a pas encore été vue dans cet appel de split
				if (verb)
					printf("nouvelle classe visitée : %d (%d parent de %d)\n", cp, p, e);
				visited_class[nrc] = cp;
				pt_visited_class[cp] = class_indices[cp][0]; //lowest indice of the class of p
				nrc++;
			}else
			{
				if (verb)
					printf("classe revisitée : %d (%d parent de %d)\n", cp, p, e);
			}
			ep = pt_visited_class[cp]; //indice de l'élément à permuter avec p
			if (ep > partition[p])
			{
				if (verb)
					printf("sommet %d déjà vu\n", p);
				continue; //on a déjà vu l'état p
			}
			ep = partitioni[ep]; //élément à permuter avec p
			swap(ep, p);
			pt_visited_class[cp]++;
			//if (verb)
			//	print_partition();
		}
	}
	
	if (verb)
	{
		//print_partition();
		print_classes();
		printf("%d classes rencontrées\n", nrc);
	}
	
	//create new classes
	for (i=0;i<nrc;i++)
	{
		cp = visited_class[i];
		
		/////only for verification : to be avoided
		if (pt_visited_class[cp] > class_indices[cp][1])
		{
			printf("***********\nError !!!\n***********\n");
		}
		////
		
		l = class_indices[cp][0];
		h = class_indices[cp][1];
		j = pt_visited_class[cp];
		
		if (verb)
			printf("classe %d : l = %d %d %d = h\n", cp, l, j, h);
		
		if (j < h)
		{ //on doit ajouter une nouvelle classe
			//choisi la plus petite classe
			if (h - j > j - l)
			{ //on choisi la partie gauche
				class_indices[cp][0] = j; //l'ancienne classe devient la partie droite
				class_indices[nclass][0] = l;
				class_indices[nclass][1] = j;
			}else
			{ //on choisit la partie droite
				class_indices[cp][1] = j; //l'ancienne classe devient la partie gauche
				class_indices[nclass][0] = j;
				class_indices[nclass][1] = h;
			}
			//met à jour les classes des sommets
			for (j=class_indices[nclass][0];j<class_indices[nclass][1];j++)
			{
				class[partitioni[j]] = nclass;
			}
			L[nL] = nclass; //ajoute la nouvelle classe à L
			nL++;
			nclass++;
		}
		
		pt_visited_class[cp] = 0; //remet à 0
	}
}

//minimisation par l'algo d'Hopcroft
//voir "Around Hopcroft’s Algorithm" de Manuel BACLET and Claire PAGETTI
Automaton Minimise (Automaton a, bool verb)
{
	if (verb)
		global_n = a.n;
	//allocations
	transitioni = (Dict **)malloc(sizeof(Dict *)*(a.n+1)); //inverse des partitions
	partition = (int *)malloc(sizeof(int)*(a.n+1));
	partitioni = (int *)malloc(sizeof(int)*(a.n+1));
	class = (int *)malloc(sizeof(int)*(a.n+1)); //classe d'un état
	nclass = 0;
	class_indices = (Couple *)malloc(sizeof(Couple)*(a.n+1));
	visited_class = (int *)malloc(sizeof(int)*(a.n+1));
	pt_visited_class = (int *)malloc(sizeof(int)*(a.n+1));
	etats = (int *)malloc(sizeof(int)*(a.n+1));
	L = (int *)malloc(sizeof(int)*(a.n+1));	 //liste des classes à partir desquelles raffiner
	nL = 0;
	int i,j,f;
	//initialise
	for (i=0;i<a.n+1;i++)
	{
		partition[i] = i;
		partitioni[i] = i;
		pt_visited_class[i] = 0;
	}
	
	//if (verb)
	//	print_partition();
	
	//initialise l'inverse des transitions
	for (i=0;i<a.n+1;i++)
	{
		transitioni[i] = (Dict *)malloc(sizeof(Dict)*a.na);
		for (j=0;j<a.na;j++)
		{
			transitioni[i][j].e = NULL;
			transitioni[i][j].n = 0;
		}
	}
	for (i=0;i<a.n;i++)
	{
		for (j=0;j<a.na;j++)
		{
			f = a.e[i].f[j];
			if (f != -1)
			{
				dictAdd(&transitioni[f][j], i);
			}else
			{
				dictAdd(&transitioni[a.n][j], i); //état puits
			}
		}
	}
	for (j=0;j<a.na;j++)
	{
		dictAdd(&transitioni[a.n][j], a.n); //transitions de l'état puits
	}
	
	/**/
	if (verb)
	{
		for (i=0;i<a.n+1;i++)
		{
			for (j=0;j<a.na;j++)
			{
				printf("transitioni[%d][%d] = [", i, j);
				for (f=0;f<transitioni[i][j].n;f++)
				{
					printf(" %d", transitioni[i][j].e[f]);
				}
				printf(" ]\n");
			}
		}
	}
	/**/
	
	//commence par séparer états finaux et non-finaux
	f = 0; //compteur du nombre d'états finaux
	for (i=0;i<a.n;i++)
	{
		if (a.e[i].final)
		{
			class[i] = 0;
			//printf("swap %d %d\n", partitioni[f], i);
			swap(partitioni[f], i);
			f++;
			/*
			if (verb)
			{
				printf("%d final\n", i);
				print_partition();
			}
			
			*/
		}else
			class[i] = 1;
	}
	class[a.n] = 1;
	//classe 0 : états finaux, classe 1 : le reste
	class_indices[0][0] = 0;
	class_indices[0][1] = f;
	class_indices[1][0] = f;
	class_indices[1][1] = a.n+1;
	visited_class[0] = 0;
	visited_class[1] = 0;
	nclass = 2;
	
	if (verb)
		print_partition();
	
	if (verb)
	{
		printf("Partition initiale :\n");
		print_classes();
	}
	
	//choisi la classe la plus petite
	if (f <= (a.n+1)/2)
		L[0] = 0;
	else
		L[0] = 1;
	nL = 1;
	
	//algo
	int C; //current class
	while (nL)
	{
		//retire la première classe de la liste L
		nL--;
		C = L[nL];
		//partionne selon cette classe
		for (j=0;j<a.na;j++)
		{
			if (verb)
				printf("split %d %d...\n", C, j);
			split(C, j, verb);
		}
	}
	
	if (verb)
	{
		printf("Partition finale :\n");
		print_classes();
	}
	
	//créé le nouvel automate
	int e;
	Automate r = NewAutomaton(nclass, a.na);
	for (i=0;i<nclass;i++)
	{
		e = partitioni[class_indices[i][0]]; //un état de la classe
		if (e >= a.n)
		{ //état puits
			for (j=0;j<a.na;j++)
				r.e[i].f[j] = -1;
			r.e[i].final = false;
			continue;
		}
		for (j=0;j<a.na;j++)
		{
			if (a.e[e].f[j] != -1)
			{
				f = class[a.e[e].f[j]];
				r.e[i].f[j] = f;
			}else
				r.e[i].f[j] = -1;
		}
		r.e[i].final = a.e[e].final;
	}
	
	if (verb)
	{
		printf("a.i = %d", a.i);
		if (a.i != -1)
		{
			printf(" classe %d", class[a.i]);
		}
		printf("\n");
	}
	
	if (a.i != -1)
		r.i = class[a.i];
	else
		r.i = -1;
	
	//retire l'état puits si pas présent dans l'automate initial
	i = class[a.n];
	if (class_indices[i][1] == class_indices[i][0]+1)
	{ //il faut retirer l'état puits
		if (verb)
			printf("retire l'état puits %d...\n", i);
		DeleteVertexOP(&r, i);
	}
	
	//libère la mémoire
	free(transitioni);
	free(partition);
	free(partitioni);
	free(class);
	free(class_indices);
	free(visited_class);
	free(pt_visited_class);
	free(etats);
	free(L);
	
	return r;
}

//////////////////////////////////////////////////////////////////////////////////////////////

/*
int sign (int a)
{
	if (a > 0)
		return 1;
	if (a < 0)
		return -1;
	return 0;
}

int delta (int a)
{
	if (a)
		return 1;
	return 0;
}
*/

void DeleteVertexOP (Automaton *a, int e)
{
	if (e < 0 || e >= a->n)
		printf("L'état %d n'est pas dans l'automate !\n", e);
	int i,j,f;
	a->n--;
	if (!a->n)
	{
		free(a->e);
		a->e = NULL;
		return;
	}
	for (i=0;i<a->n;i++)
	{
		for (j=0;j<a->na;j++)
		{
			f = a->e[i+(i>=e)].f[j];
			if (f != e)
				a->e[i].f[j] = f-(f>=e);
			else
				a->e[i].f[j] = -1;
		}
		a->e[i].final = a->e[i+(i>=e)].final;
	}
	if (e == a->i)
		a->i = -1;
	else
		a->i = a->i - (a->i>=e);
}

Automaton DeleteVertex (Automaton a, int e)
{
	if (e < 0 || e >= a.n)
		printf("L'état %d n'est pas dans l'automate !\n", e);
	Automaton r = NewAutomaton(a.n-1, a.na);
	int i,j,f;
	for (i=0;i<a.n-1;i++)
	{
		for (j=0;j<a.na;j++)
		{
			f = a.e[i+(i>=e)].f[j];
			if (f != e)
				r.e[i].f[j] = f-(f>=e);
			else
				r.e[i].f[j] = -1;
		}
		r.e[i].final = a.e[i+(i>=e)].final;
	}
	r.i = a.i - (a.i>=e);
	return r;
}

Automaton BiggerAlphabet (Automaton a, Dict d, int nna)
{
	if (d.n != a.na)
	{
		printf("BA Error : the dictionnary must be of the same size as the previous alphabet.\n");
		return NewAutomaton(0,0);
	}
	Automaton r = NewAutomaton(a.n, nna);
	init(&r);
	int i,j;
	for (i=0;i<a.n;i++)
	{
		for (j=0;j<a.na;j++)
		{
			r.e[i].f[d.e[j]] = a.e[i].f[j];
			r.e[i].final = a.e[i].final;
		}
	}
	r.i = a.i;
	return r;
}

void Test ()
{
	printf("sizeof(Automaton)=%d\n", sizeof(Automaton));
}
