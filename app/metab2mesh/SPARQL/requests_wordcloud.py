prefix = """
    DEFINE input:inference \"schema-inference-rules\"
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
    PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
    PREFIX voc: <http://myorg.com/voc/doc#>
    PREFIX cito: <http://purl.org/spar/cito/>
    PREFIX fabio:	<http://purl.org/spar/fabio/> 
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX chebi: <http://purl.obolibrary.org/obo/CHEBI_>
"""

PubChem = """
    select ?label ?count
    %s
    where
    {
        {
            select ?mesh (count(distinct ?pmid) as ?count) 
            where
            {
                {
                    select ?pmid
                    where{
                        %s cito:isDiscussedBy ?pmid .
                        ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini .
                        ?mesh_ini a meshv:TopicalDescriptor .
                        ?mesh_ini meshv:active 1 .
                        ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber+) ?tn .
                        %s meshv:treeNumber ?tn .
                    }
                }
                ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh .
                ?mesh a meshv:TopicalDescriptor .
                ?mesh meshv:active 1 .
                
            }
            group by ?mesh
        }
        ?mesh rdfs:label ?label .
    }
"""