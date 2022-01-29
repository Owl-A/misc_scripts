#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "Matching.h"
#include <fstream>
#include "Graph.h"
#include <cstdlib>
#include <iostream>
#include <string>
#include <sstream>
using namespace std;

static pair< Graph, vector<double> > *ReadWeightedGraph(int mentees, int mentors, PyObject* args)
{
	//Please see Graph.h for a description of the interface

	// mentees and mentors are already equal (after the latest change) but meh, whatever.
	int multi = mentors*((mentees/mentors) + ((mentees % mentors) ? 1 : 0));
	int n = multi + mentees;
	int m = mentees * multi;
	PyObject *plist, *pitem;
	/*
	if(!PyArg_ParseTuple(args, "O!", &PyList_Type, &plist)){
	  PyErr_SetString(PyExc_TypeError, "The cost list (3rd argument) should be a list of floats");
	  return NULL;
	}
	*/
	plist = PyTuple_GetItem(args, 2);

	Graph G(n);
	vector<double> cost(m);
	for(int i=0; i < mentees; i++){
	  for(int j=0; j < mentors; j++){
	    pitem = PyList_GetItem(plist, i*mentors + j);
	    if(!PyFloat_Check(pitem)) {
	      PyErr_SetString(PyExc_TypeError, "Found a non-float in cost list (3rd argument)");
	      return NULL;
	    }
	    double c = PyFloat_AsDouble(pitem);
	    cerr << "Cost: " << c << ", Mentee: "<< i << ", Mentor: "<< j << endl;
	    for(int k = 0; k < multi; k += mentors){
	      G.AddEdge(i, mentees + j + k);
              cost[G.GetEdgeIndex(i, mentees + j + k)] = c;
	    }
	  }
	}
	pair< Graph, vector<double> > *p = new pair< Graph, vector<double> >();
	p->first = G;
	p->second = cost;
	return p;
}

static PyObject*
MinimumCostPerfectMatchingExample(PyObject *self, PyObject *args)
{
	Graph G;
	vector<double> cost;
	
	int mentees, mentors;
	/*
	if(!PyArg_ParseTuple(args, "i", &mentees)){
	  PyErr_SetString(PyExc_TypeError, "The mentee number (1st argument) should be a number");
	  return NULL;
	}
	if(!PyArg_ParseTuple(args, "i", &mentors)){
	  PyErr_SetString(PyExc_TypeError, "The mentor number (2nd argument) should be a number");
	  return NULL;
	}
	*/

	mentees = PyLong_AsLong(PyTuple_GetItem(args, 0));
	mentors = PyLong_AsLong(PyTuple_GetItem(args, 1));

	//Read the graph
	pair< Graph, vector<double> > *p = ReadWeightedGraph(mentees, mentors, args);
	//pair< Graph, vector<double> > p = CreateRandomGraph();
	if(!p){
	  PyObject *fail = PyList_New(0);
	  return fail;
	}
	G = p->first;
	cost = p->second;

	//Create a Matching instance passing the graph
	Matching M(G);

	//Pass the costs to solve the problem
	pair< list<int>, double > solution = M.SolveMinimumCostPerfectMatching(cost);

	list<int> matching = solution.first;

	PyObject *ret = PyList_New(mentees), *pitem;
	for(list<int>::iterator it = matching.begin(); it != matching.end(); it++)
	{
		pair<int, int> e = G.GetEdge( *it );

		pitem = PyLong_FromLong((e.second - mentees) % mentors);
		PyList_SetItem(ret, e.first, pitem);
	}
	
	return ret;
}


static PyMethodDef Methods[] = {
  {"match", MinimumCostPerfectMatchingExample, METH_VARARGS,
   "Does the min cost perfect matching of the bipartite graph"},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
  PyModuleDef_HEAD_INIT,
  "matcher",
  NULL,
  -1,
  Methods
};

PyMODINIT_FUNC
PyInit_matcher(void) {
  return PyModule_Create(&module);
}

int main(int argc, char* argv[])
{
	wchar_t *program = Py_DecodeLocale(argv[0], NULL);
	if(program == NULL){
	  cerr << "Fatal error: cannot decode argv[0]\n";
	  exit(1);
	}

	if(PyImport_AppendInittab("matcher", PyInit_matcher) == -1){
	  cerr << "Error: cannot extend in-built modules table\n";
	  exit(1);
	}

	Py_SetProgramName(program);

	Py_Initialize();

	PyObject *pmodule = PyImport_ImportModule("matcher");
	if(!pmodule) {
	  PyErr_Print();
	  cerr << "Error: could not import module 'matcher'\n";
	}

	PyMem_RawFree(program);
	return 0;

	/*string filename = "";
	string algorithm = "";

	int i = 1;
	while(i < argc)
	{
		string a(argv[i]);
		if(a == "-f")
			filename = argv[++i];
		else if(a == "--minweight")
			algorithm = "minweight";
		else if(a == "--max")
			algorithm = "max";
		i++;
	}

	if(filename == "" || algorithm == "")
	{
		cout << "usage: ./example -f <filename> <--minweight | --max>" << endl;
		cout << "--minweight for minimum weight perfect matching" << endl;
		cout << "--max for maximum cardinality matching" << endl;
		cout << "file format:" << endl;
		cout << "the first two lines give n (number of vertices) and m (number of edges)," << endl;
		cout << "followed by m lines, each with a tuple (u, v [, c]) representing the edges," << endl;
	   	cout << "where u and v are the endpoints (0-based indexing) of the edge and c is its cost" << endl;	
		cout << "the cost is optional if --max is specified" << endl;
		return 1;
	}

	try
	{
		if(algorithm == "minweight")
			MinimumCostPerfectMatchingExample(filename);
		else
			MaximumMatchingExample(filename);
	}
	catch(const char * msg)
	{
		cout << msg << endl;
		return 1;
	}

	return 0;
	*/
}



