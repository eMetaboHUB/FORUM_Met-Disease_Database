# Compute the score for ranking co-annotated MeSH descriptors

To estimate the importance of each MeSH descriptor supporting a relation, we propose to compute a score, analog to the TF-IDF, using the frequency of the MeSH descriptor in the corpus of articles supporting the relation, adjusted by its frequency in the whole KG.

The TF-IDF is a metric used in text-mining approaches to estimate the importance of a word in a document, regarding a collection of documents. It is related to the frequency of the word in the document (Term-Frequency) and the inverse of the frequency of documents that mention it in the collection (Inverse-Document-Frequency). So, the more a word is frequent in the document and rarely mentioned in the whole collection, the more this word seems important to characterize this document.

For a relation between a chemical and a MeSH descriptor, we apply a similar approach to estimate which co-mentioned descriptors appear to be important to describe this relation. We used the frequency of MeSH annotation in the corpus of articles supporting the relation, regarding the inverse frequency of the MeSH annotation in the whole FORUM KG. This score proposes a ranking of MeSH concepts that seem to be relevant to describe the relation.

We estimate the importance of a MeSH descriptor $`k`$ annotated in publications supporting the relation between a compound $`i`$ and a MeSH descriptor $`j`$:

$`Score=\frac{N^{k}_{i,j}}{N_{i,j}} \times log(\frac{N_{..}}{N_{.k}})`$

- $`N_{i,j}`$ the number of articles supporting the co-occurrence between the compound $`i`$ and the MeSH descriptor $`j`$.
- $`N^{k}_{i,j}`$ the number of articles discussing the MeSH descriptor $`k`$ among those supporting the relation between $`i`$ and $`j`$.
- $`N_{.k}`$ The total number of articles discussing the MeSH descriptor $`k`$ in the KG.
- $`N_{..}`$ The total number of articles in the KG. 


The computation of the score for a given relation between a chemical compound/class and a MeSH descriptor can be done in 2 steps :

### 1)  Determine sur frequency of co-mentioned MeSH descriptors

Use *co_annotated_MeSH.py*

Creates a table of co-mentioned MeSH descriptors for a given relation between a chemical and a MeSH descriptor.

Args: 

- chem: Identifier of the chemical involved in the association
- chemType: Type of the chemical identifier: PubChem, ChEBI or ChemOnt
- MeSH: Identifier of the MeSH involved in the association
- config: Path to the configuration file
- out: Path to output file
- TreeList: List of MeSH category codes to consider, sperated by a |. Ex: C|A|D|G|B|F|I|J"

In config file (you should not have to modify this file): 

- [DEFAULT]
  - request_file: The name of the SPARQL request file containing queries, located in *app/computation/SPARQL* (requests_co_annot)
- [VIRTUOSO]
  - url = url of the Virtuoso SPARQL endpoint
  - graph_from: graph_from: uri of data source graphs, one per line, Ex:
    https://forum.semantic-metabolomics.org/PMID_CID_endpoints/2020
    https://forum.semantic-metabolomics.org/PubChem/reference/2020-12-03
- [NAMESPACES]
  - PubChem: PubChem compound namespace (http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID)
  - ChEBI: ChEBI classes namespace (http://purl.obolibrary.org/obo/)
  - MeSH: MeSH namespace (http://id.nlm.nih.gov/mesh/)
  - ChemOnt classes namespace (http://purl.obolibrary.org/obo/)

```bash
python3 app/computation/co_annotation_score/co_annotated_MeSH.py --chem="IdChemical" --chemType="PubChem/ChEBI/ChemOnt" --MeSH="MeSHID" --config="path/to/config/file" --TreeList="TreeNumbers" --out="path/to/output/co_annotated_MeSH.csv"
```

Example for the relation between Oxyfedrine (PubChem CID 5489013) and Myocardial Ischemia (MeSH D017202):

```bash
python3 app/computation/co_annotation_score/co_annotated_MeSH.py --chem="5489013" --chemType="PubChem" --MeSH="D017202" --config="app/computation/config/co_annotated_MeSH/request_config.ini" --TreeList="C|A|D|G|B|F|I|J" --out="out/path/CID5489013_D017202_co_annotated_MeSH.csv"
```

### 2) Compute the score

Use *score.R*

From the table of co-mentioned MeSH descriptors associated to a particular relation (See co_annotated_MeSH.py), creates the score table and an associated figure displaying the top n most important terms.

Args:

- MeSH_context: Path to file containing the co-annotated MeSH. Should be the output of co_annotated_MeSH.py
- MeSH_corpora: Path to the table containing the corpora sizes of MeSH descriptors, provided in the *co_annotation_score* directory: TOTAL_MESH_PMID.csv)
- cooc: The observed co-occurrence between both entities
- Chem_name: A name for the chemical
- MeSH_name: A name for the MeSH descriptor
- Collection_size: The total number of publications in the collection. For the current release :
  - 8877780 related to PubChem Compounds
  - 7897020 related to ChEBI classes
  - 8826139 related to ChemOnt classes
- Chem_MeSH_ID: If the compound has also a dedicated MeSH descriptor, it is advised to remove it from the analysis to avoid an irrelevant result. Indicate the associated MeSH descriptor using the option or skip it if none.
- n_top: The top 'n' to display in the figure
- path_out: Path to the output directory

To request with ChEBI identifiers, you must add the prefix 'CHEBI_' to the identifier, like "CHEBI_35551" to refer to the class of fluoroalkanoic acid (CHEBI:35551)

To request with ChemOnt identifiers, you must add the prefix 'CHEMONTID_' to the identifier, like "CHEMONTID_0001343" to refer to the class of 1,2-oxazines (C0001343)

```bash
Rscript app/computation/co_annotation_score/score.R --MeSH_context="/path/to/co_annotated_MeSH.csv" --MeSH_corpora="path/to/mesh/corpora" --cooc=COOC --Chem_name="Cpd Name" --MeSH_name="MeSH Name" --Collection_size=N --Chem_MeSH_ID="ChemID" --n_top=20 --path_out="/path/out/dir"
```

Example for the relation between Oxyfedrine (PubChem CID 5489013) and Myocardial Ischemia (MeSH D017202):

```bash
Rscript app/computation/co_annotation_score/score.R --MeSH_context="/path/to/CID5489013_D017202_co_annotated_MeSH.csv" --MeSH_corpora="app/computation/co_annotation_score/TOTAL_MESH_PMID.csv" --cooc=87 --Chem_name="Oxyfedrine" --MeSH_name="Myocardial Ischemia" --Collection_size=8877780 --Chem_MeSH_ID="D010099" --n_top=20 --path_out="/path/out/dir"
```