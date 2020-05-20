import os, time, rdflib, sys, subprocess
from rdflib.namespace import XSD, DCTERMS, VOID
sys.path.insert(1, 'app/')
from Database_ressource_version import Database_ressource_version

def download_pubChem(dir, request_ressource, out_path):
    """
    This function is used to download PubChem rdf files from the ftp server and create a new version of the associated ressource.
    - dir: the path to the directory/file to fetch in the ftp server from ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/
    - request_ressource: the name of the ressource as indicated in the void.ttl file.
    - out_path: a path to a directory to write output files
    The function return the version created
    """
    # Intialyze .log files
    with open("dl_pubchem_" + request_ressource + ".log", "wb") as f_log:
        pass
    # On télécharge le fichier void et les données
    print("Trying to dowload PubChem void.ttl file ...", end = '')
    try:
        subprocess.run("wget ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/void.ttl", shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to download PubChem void.ttl file, check dl_pubchem_" + request_ressource + ".log")
        print(e)
        with open("dl_pubchem_" + request_ressource + ".log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nTrying to read Pubchem void.ttl file ...", end = '')
    # On parse le fichier des metadatas
    g_metadata = rdflib.Graph()
    g_metadata.parse("void.ttl", format='turtle')
    print("Ok\nGet version from void.ttl file ...", end = '')
    global_modif_date = g_metadata.value(subject=rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/void.ttl#PubChemRDF"), predicate=rdflib.URIRef("http://purl.org/dc/terms/modified"), object=None)
    # On crée un repertoire correspondant au subset PubChem récupéré et à la date de récupération
    version_path = out_path + request_ressource + "/" + str(global_modif_date) + "/"
    if not os.path.exists(version_path):
        os.makedirs(version_path)
    try:
        subprocess.run("mv void.ttl " + out_path, shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to move PubChem void.ttl file, check dl_pubchem_" + request_ressource + ".log")
        print(e)
        with open("dl_pubchem_" + request_ressource + ".log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nTrying to dowload Pubchem " + dir + " directory ...", end = '')
    # On récupère les données que l'on enregistre dans le directory créée
    try:
        subprocess.run("wget -r -A ttl.gz -nH" + " -P " + version_path + " --cut-dirs=5 " + "ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/" + dir, shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to dowload PubChem " + dir + " directory, check dl_pubchem_" + request_ressource + ".log")
        print(e)
        with open("dl_pubchem_" + request_ressource + ".log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nTrying to build Pubchem " + request_ressource + " new ressource version ...", end = '')
    # On récupère la description en metadata du répertoire téléchargé  pour créer le graph qui sera associé à la ressource
    ressource_version = Database_ressource_version(ressource = "PubChem/" + request_ressource, version = str(global_modif_date))
    ressource_version.version_graph.namespace_manager = g_metadata.namespace_manager
    # On annote la nouvelle version avec les informations du fichier void
    for s,p,o in g_metadata.triples((rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/void.ttl#" + request_ressource), None, None)):
        if p == VOID['dataDump'] and not str(o).startswith("ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/" + dir):
            continue
        ressource_version.add_version_attribute(predicate = p, object = o)
    # On écrit le graph le fichier
    ressource_version.version_graph.serialize(version_path + "ressource_info_" + request_ressource + "_" + str(global_modif_date) + ".ttl", format = 'turtle')
    print("Ok\nEnd !")
    return ressource_version.version, str(ressource_version.uri_version)

def download_MeSH(out_dir, namespaces_dict):
    """
    This function is used to download the last version of the MeSH RDF from NIH ftp server, the void.ttl file is also use to bring metadata information about the dowloaded version.
    But contrary to PubChem the modification date is not include in the void.ttl file, so version should be added by the user.
    Ressource is named 'MeSHRDF' as indicate in the void.ttl
    - out_dir: a path to an directory to write output files
    - namespace_list: a list of the namespaces that should be associated to the graph
    The function return the version
    """
    # Intialyze .log files
    with open("dl_mesh.log", "wb") as f_log:
        pass
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    print("Trying to dowload MeSH void.ttl file ...", end = '')
    # On télécharge le fichier void et les données
    try:
        subprocess.run("wget -P " + out_dir + " ftp://ftp.nlm.nih.gov/online/mesh/rdf/void_1.0.0.ttl", shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to download MeSH void.ttl file, check dl_mesh.log")
        print(e)
        with open("dl_mesh.log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nTrying to read MeSH void.ttl file ...", end = '')
    g_metadata = rdflib.Graph()
    g_metadata.parse(out_dir + "void_1.0.0.ttl", format = 'turtle')
    print("Ok\nTrying to dowload MeSH RDF file ...", end = '')
    # téléchargement du MeSH RDF
    try:
        subprocess.run("wget -P " + out_dir + " ftp://ftp.nlm.nih.gov/online/mesh/rdf/mesh.nt", shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to download MeSH mesh.nt file, check dl_mesh.log")
        print(e)
        with open("dl_mesh.log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nGet version from void.ttl file ...", end = '')
    # On récupère la date de modification
    version = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(out_dir + "mesh.nt")))
    out_path = out_dir + version + "/"
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    # On déplace les fichiers aux endroits correspondant à la version
    print("Ok\nMove files ...", end = '')
    try:
        subprocess.run("rm " + out_dir + "void_1.0.0.ttl ", shell = True, check=True, stderr = subprocess.PIPE)
        subprocess.run("mv " + out_dir + "mesh.nt " + out_path + "mesh.nt", shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to move files, check dl_mesh.log")
        print(e)
        with open("dl_mesh.log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nTrying to parse MeSH original metadata ...", end = '')
    # On crée la nouvelle ressource MeSH
    ressource_version = Database_ressource_version(ressource = "MeSHRDF", version = version)
    ressource_version.version_graph.namespace_manager = g_metadata.namespace_manager
    for s,p,o in g_metadata.triples((rdflib.URIRef("http://id.nlm.nih.gov/mesh/void#MeSHRDF"), None, None)):
        # L'attribut creation dans le void correspond à la date de création originale du fichier soir courant 2014, noous souhaitant que la date de création de notre ressource correspondent à la date de modification du fichier
        if p != DCTERMS["created"]:
            ressource_version.add_version_attribute(predicate = p, object = o)
    # On crée le graph de données : 
    print("Ok\nTrying to create MeSH new ressource version ...", end = '')
    mesh_graph = ressource_version.create_data_graph([], None)
    mesh_graph.bind("mesh", rdflib.Namespace("http://id.nlm.nih.gov/mesh/"))
    mesh_graph.parse(out_path + "mesh.nt", format = "nt")
    mesh_graph.serialize(destination = out_path + "mesh.trig", format='trig')
    ressource_version.add_version_attribute(namespaces_dict["void"]["triples"], rdflib.Literal( len(mesh_graph), datatype=XSD.long ))
    ressource_version.add_version_attribute(namespaces_dict["void"]["distinctSubjects"], rdflib.Literal( len(set([str(s) for s in mesh_graph.subjects()])), datatype=XSD.long ))
    # On écrit le graph de la ressource 
    ressource_version.version_graph.serialize(out_path + "ressource_info_MeSHRDF" + "_" + version + ".ttl", format = 'turtle')
    # On supprime le fichier initial au format .nt
    try:
        subprocess.run("rm " + out_path + "mesh.nt", shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to move files, check dl_mesh.log")
        print(e)
        with open("dl_mesh.log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nEnd")
    return ressource_version.version, str(ressource_version.uri_version)