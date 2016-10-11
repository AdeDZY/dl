//
// Created by Zhuyun Dai on 5/14/15.
//
#include "indri/Repository.hpp"
#include "indri/CompressedCollection.hpp"
#include "indri/LocalQueryServer.hpp"
#include "indri/QueryEnvironment.hpp"
#include <iostream>
#include <sstream>
#include <math.h>
#include <cmath>
#include <time.h>

using namespace std;
using namespace indri::api;

int main(int argc, char **argv){
    string repoPath = argv[1];    // path to the index
    string extidFile = argv[2];   // files with document external IDs, like "cluewb09-en0000-0053"
    string outFile = argv[3];     // output file path


    ifstream extidStream;
    extidStream.open(extidFile.c_str());
    
    ofstream outStream;
    outStream.open(outFile.c_str());


    QueryEnvironment IndexEnv;

	stringstream ss;

    IndexEnv.addIndex ( repoPath); // open the index


    vector <string> extids;
    vector <int> intids;

    string extid;
	string prevExtid = "";
    string outLine;
    int indexId = 0;
    int ndoc = 0;
    while(!extidStream.eof()){
		extidStream>>extid;   // read one external doc ID
        extids.clear();
        extids.push_back(extid); // documentIDsFromMetadata only takes vector as input, so put the extid into a vector

     	std::vector< indri::api::ParsedDocument *> documents = IndexEnv.documentsFromMetadata("docno", extids);
    	string documentText = documents[0]->text;
	

		ss.str("");
		ss.clear();
        outStream<<extid<<endl<<documentText<<endl;
        ++ndoc;

    }


    outStream.close();
    extidStream.close();

    IndexEnv.close();

    return 0;
}
