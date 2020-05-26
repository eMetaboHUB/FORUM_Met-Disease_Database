import glob, requests, subprocess, sys
import rdflib
import os
from rdflib.namespace import XSD, DCTERMS, OWL, VOID
sys.path.insert(1, 'app/')
from Database_ressource_version import Database_ressource_version

def create_update_file_from_ressource(path_out, path_to_graph_dir, file_pattern, target_graph, update_file_name):
    """
    This function is used to load graph which represent a ressource, with one or several .trig files associated to data graph and one ressource_info_**.ttl file describing the ressource
    """
    with open(path_out + update_file_name, "a") as update_f:
        update_f.write("delete from DB.DBA.load_list ;\n")
        update_f.write("ld_dir_all ('./dumps/" + path_to_graph_dir + "', '" + file_pattern + "', '" + target_graph + "');\n")
        update_f.write("rdf_loader_run();\n")
        update_f.write("checkpoint;\n")
        update_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")

def remove_graph(path_out, uris, update_file_name):
    with open(path_out + update_file_name, "a") as remove_f:
        remove_f.write("log_enable(3,1);\n")
        for uri in uris:
            remove_f.write("SPARQL CLEAR GRAPH  \"" + uri + "\"; \n")
        remove_f.write("delete from DB.DBA.load_list ;\n")


def test_if_graph_exists(url, graph_uri, linked_graph_uri, path_out, update_file_name):
    """
    This function is used to test if graph exist and to erase it if needed.
    - url: Virtuoso SPARQL endpoint url
    - graph_uri: the graph uri
    - linked_graph_uri: a list of additionnal graph uri that are linked to this graph (Ex: Intra eq graph)
    - path_out: path to output directory
    """
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html"
    }
    data = {
        "format": "html",
        "query": "ASK WHERE { GRAPH <" + graph_uri + "> { ?s ?p ?o } }"
    }
    r = requests.post(url = url, headers = header, data = data)
    if r.status_code != 200:
        print("Error in request while trying to check if graph " + graph_uri + " exists.\nImpossible to continue, exit.\n")
        print(r.text)
        sys.exit(3)
    if r.text == "true":
        print("SMBL graph " + graph_uri + " and linked graphs " + ",".join(linked_graph_uri) + " already exists.")
        while True:
            t = str(input("Do you want to erase (y/n) :"))
            if t not in ["y", "n"]:
                print("Do you want to erase (y/n) :")
                continue
            else:
                break
        if t == "y":
            l = [graph_uri] + linked_graph_uri
            print(l)
            remove_graph(path_out, l, update_file_name)
            return True
        else:
            return False
    else:
        return True

def request_annotation(url, query, sbml_uri, annot_graph_uri, header, data, out_file):
    """
    This function is ised to send an annotation request
    - g_base_uri: the annotation graph uri base, ex: http://database/annotation_graph/
    - query: a string associated to the query prepared to be filled with additional parameters
    - sbml_uri: the uri of the targeted SBML graph
    - annot_graph_uri: a list of graph used as sources or the annotation process
    - version: the version of the annotation
    - header: a dict containing header paramters for the request
    - data: a dict containing data parameteres for the request
    """
    data["query"] = query %(sbml_uri, "\n".join(["FROM <" + uri + ">" for uri in annot_graph_uri]))
    print(data["query"])
    r = requests.post(url = url, headers = header, data = data)
    if r.status_code != 200:
        print("Error in request while trying to compute annotation query.\nImpossible to continue, exit.\n")
        print(r.text)
        return False
    print("Write results in " + out_file)
    with open(out_file, "w") as f_out:
        f_out.write(r.text)
    return True

def ask_for_graph(url, graph_uri):
    """
    This function is used to test if graph a exist without erase
    - url: Virtuoso SPARQL endpoint url
    - graph_uri: the graph uri to be tested
    """
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html"
    }
    data = {
        "format": "html",
        "query": "ASK WHERE { GRAPH <" + graph_uri + "> { ?s ?p ?o } }"
    }
    r = requests.post(url = url, headers = header, data = data)
    if r.status_code != 200:
        print("Error in request while trying to check if graph " + graph_uri + " exists.\nImpossible to continue, exit.\n")
        print(r.text)
        sys.exit(3)
    if r.text == "true":
        return True
    return False

def create_annotation_graph_ressource_version(path_to_annot_graphs_dir, version, ressource_name, desc, title, sources):
    """
    This function is used to create the ressource_info file associated to the version of the created annotation_graph.
    - path_to_annot_graphs_dir: A path to a directory containing all the associated annotation graph created using Virtuoso as .TriG file (Cf. README)
    - version: the version of the annotations graphs, MUST be the same as the one used in Virtuoso !
    """
    ressource_version = Database_ressource_version(ressource = ressource_name, version = version)
    n_triples = 0
    subjects = set()
    for annot_graph in os.listdir(path_to_annot_graphs_dir):
        if not annot_graph.endswith(".ttl"):
            continue
        if annot_graph.startswith("ressource_info_"):
            continue
        sub_g = rdflib.ConjunctiveGraph()
        sub_g.parse(path_to_annot_graphs_dir + annot_graph, format = 'turtle')
        n_triples += len(sub_g)
        subjects = subjects.union(set([s for s in sub_g.subjects()]))
        ressource_version.add_DataDump(annot_graph)
    for source in sources:
        ressource_version.add_version_attribute(DCTERMS["source"], rdflib.URIRef(source))
    ressource_version.add_version_attribute(DCTERMS["description"], rdflib.Literal(desc))
    ressource_version.add_version_attribute(DCTERMS["title"], rdflib.Literal(title))
    ressource_version.add_version_attribute(VOID["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
    ressource_version.add_version_attribute(VOID["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
    ressource_version.version_graph.serialize(destination=path_to_annot_graphs_dir + "void.ttl", format = 'turtle')