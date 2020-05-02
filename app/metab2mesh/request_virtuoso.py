import requests
import os
import multiprocessing as mp
import pandas as pd

header = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/csv"
}
data = {
    "format": "csv",
}

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
"""

distinct_pmid_by_CID = """
select ?CID ?count
where
{
    {
        select ?CID ?count
        where
        {
            {
                select (strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\") as ?CID) (count(distinct ?pmid) as ?count) 
                where 
                {
                    {
                        select ?cid where {
                            {
                                select distinct ?cid where
                                {
                                    ?cid cito:isDiscussedBy ?pmid .
                                }
                                order by ?cid
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:treeNumber ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                }
                group by ?cid
            }
        }
        order by ?CID
    }
}
limit %d
offset %d
"""
distinct_pmid_by_MeSH = """
select ?MESH ?count
where
{
    {
        select ?MESH ?count
        where
        {
            {
                select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) 
                where 
                {
                    {
                        select ?mesh
                        where
                        {
                            {
                                select distinct ?mesh
                                where
                                {
                                    ?mesh a meshv:TopicalDescriptor .
                                    ?mesh meshv:treeNumber ?tn .
                                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                                }
                                order by ?mesh
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                }
                group by ?mesh
            }
        }
        order by ?MESH
    }
}
limit %d
offset %d
"""

distinct_all_pmids = """
    select (count(distinct ?pmid) as ?count) where {
        ?cid cito:isDiscussedBy ?pmid .
        ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
        ?mesh a meshv:TopicalDescriptor .
        ?mesh meshv:treeNumber ?tn .
        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
    }
"""

distinct_pmid_by_CID_MeSH = """
select ?CID ?MESH ?count
where
{
    {
        select ?CID ?MESH ?count
        where 
        {
                {
                    select (strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\") as ?CID) (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) 
                    where {
                        {
                            select ?cid where {
                                {
                                    select distinct ?cid where {
                                        ?cid cito:isDiscussedBy ?pmid .
                                    }
                                    order by ?cid
                                }
                            }
                            limit %d
                            offset %d
                        }
                        ?cid cito:isDiscussedBy ?pmid .
                        ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                        ?mesh a meshv:TopicalDescriptor .
                        ?mesh meshv:treeNumber ?tn .
                        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                    }
                    group by ?cid ?mesh
                } 
            bind(uri(concat(\"http://database/ressources/metab2mesh/\", ?CID, \"_\", ?MESH)) as ?id)
        }
        order by ?id
    }
}
limit %d
offset %d
"""


list_of_distinct_pmid_by_CID_MeSH = """
select ?id (group_concat(distinct ?str_pmid;separator=\";\") as ?list_pmid)
where
{
    {
        select ?id ?str_pmid
        where
        {
            {
                select (concat(strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\"), \"_\", strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\")) as ?id) (strafter(str(?pmid), \"http://rdf.ncbi.nlm.nih.gov/pubchem/reference/PMID\") as ?str_pmid)
                where {
                    {
                        select ?cid where {
                            {
                                select distinct ?cid where {
                                    ?cid cito:isDiscussedBy ?pmid .
                                }
                                order by ?cid
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:treeNumber ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                }
                group by ?cid ?mesh
            }
        }
        order by ?id
    } 
}
limit %d
offset %d
"""


MESH_name = """
select ?MESH str(?str_f_label)
where
{
    {
        select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) MIN(str(?label)) as ?str_f_label
        where
        {
            {
                select ?mesh
                where
                {
                    {
                        select distinct ?mesh
                        where
                        {
                            ?mesh a meshv:TopicalDescriptor .
                            ?mesh meshv:treeNumber ?tn .
                            FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                        }
                        order by ?mesh
                    }
                }
                limit %d
                offset %d
            }
        ?mesh rdfs:label ?label
        }
        group by ?mesh
        order by ?mesh
    }
}
limit %d
offset %d
"""

url = "http://localhost:9980/sparql/"


def parallelize_query_by_offset(count_id, query, prefix, header, data, url, limit_pack_ids, limit_selected_ids, out_path, n_processes):
    # Initialyze the pool
    pool = mp.Pool(processes=n_processes, maxtasksperchild=20)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    # First step is to get the total number of cid: 
    # Getting the number of CID, we can prepare the pack of cids respecting limit_size
    n_offset = count_id // limit_pack_ids
    offset_list = [i * limit_pack_ids for i in range(0, n_offset + 1)]
    # Apply send_query_by_offset in parallel respecting the number of processes fixed
    results = [pool.apply_async(send_query_by_offset, args=(query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, 0, out_path)) for offset_pack_ids in offset_list]
    output = [p.get() for p in results]
    # Ended
    pool.close()
    pool.join()
    # Merge files
    os.system("cat " + out_path + "* >> " + out_path + "res_full.csv")


def write_request(lines, out_name):
    if len(lines) > 0:
        # Remove the header 
        lines.pop(0)
        with open(out_name, "w") as out:
            for l in lines:
                out.write(l + "\n")

def send_query(query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids):
    # Fill the query string with the associated parameters
    formated_query = prefix + query % (limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids)
    data["query"] = formated_query
    r = requests.post(url = url, headers = header, data = data)
    return r

def send_query_by_offset(query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids, out_path):
    """
    In this function limit_pack_ids, offset_pack_ids are fixed and only offset_selected_ids is increased if needed
    """
    n_f = 1
    out_name = out_path + "res_offset_%d_f_%d.csv" %(offset_pack_ids, n_f)
    # Send the query at defined pack_id offset, and with intial selected_id offset, 0.
    r = send_query(query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids)
    # Test if request successed
    if r.status_code != 200:
        with open(out_path + "fail.log", "a") as log_fail:
            log_fail.write("%d_%d" % (offset_pack_ids, offset_selected_ids))
        # If the first request fail, we fake it succed so the will still check the superior offset
        test = True
    else:
        print("Request succed !")
        # Parse and write lines
        lines = r.text.splitlines()
        # After parsing, r is clean
        r = None
        write_request(lines, out_name)
        # When writing, the header is remove so the number of lines to check is exactly limit_selected_ids
        test = (len(lines) == limit_selected_ids)
        # After testing, lines are clean:
        lines = None
    while test:
        # If the number of lines equals the setted limit, it may reveals that there are remaining lines, increase offset by limit to get them.
        print("Limit reach, trying next offset ... ")
        offset_selected_ids += limit_selected_ids
        n_f += 1
        out_name = out_path + "res_offset_%d_f_%d.csv" %(offset_pack_ids, n_f)
        # Send request
        r = send_query(query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids)
        if r.status_code != 200:
            with open(out_path + "fail.log", "a") as log_fail:
                log_fail.write("%d_%d" % (offset_pack_ids, offset_selected_ids))
            # If the first request fail, we fake it succed so the will still check the superior offset
            test = True
            continue
        lines = r.text.splitlines()
        # After testing, lines are clean:
        r = None
        # Export files
        write_request(lines, out_name)
        # Test if it was the last
        test = (len(lines) == limit_selected_ids)
        # After testing, lines are clean:
        lines = None
    return True

def prepare_data_frame(path_to_CID_MESH, path_to_CID_PMID, path_to_MESH_PMID, nbTotal_PMID, out_path, file_size):
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    cid_mesh = pd.read_csv(path_to_CID_MESH, sep = ",", names=["CID", "MESH", "COOC"])
    cid_pmid = pd.read_csv(path_to_CID_PMID, sep = ",", names=["CID", "TOTAL_PMID_CID"])
    mesh_pmid = pd.read_csv(path_to_MESH_PMID, sep = ",", names=["MESH", "TOTAL_PMID_MESH"])
    # Step 1: merging total CID counts :
    data = cid_mesh.merge(cid_pmid, on = "CID", how = "left")
    # Step 2: merging total MESH counts :
    data = data.merge(mesh_pmid, on = "MESH", how = "left")
    # Step 3: Add total number of PMID
    data["TOTAL_PMID"] = nbTotal_PMID
    df_size=len(data)
    for i, start in enumerate(range(0, df_size, file_size)):
        data[start:start+file_size].to_csv(out_path + 'metab2mesh_{}.csv'.format(i), index = False)
    return data


# Get By CID: 
count_cid_query = prefix + """
    select (count(distinct ?cid) as ?count_CID)
    where 
    {
        ?cid cito:isDiscussedBy ?pmid .
    }
"""

# Get By MeSH
count_mesh_query = prefix + """
    select (count(distinct ?mesh) as ?count_MESH) 
    where 
    {
        ?mesh a meshv:TopicalDescriptor .
        ?mesh meshv:treeNumber ?tn .
        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
    }
"""

# For CID - distinct PMID, when request by pack, some CID may not have linked publication for which there is a mesh from the selected fields. So the number of returned CID may be less than the pack size
# For MeSH - distinct PMID, when request by pack, some MeSH selected from their fields (in the total MESH thesaurus) may not have linked publication for which there is CID. So the number of returned MeSH may be less than the pack size.

# Count distinct CID
data["query"] = count_cid_query
count_cid_res = requests.post(url = url, headers = header, data = data)
count_cid = int(count_cid_res.text.splitlines().pop(1))

# Get CID - MeSH coocurences :
parallelize_query_by_offset(count_cid, distinct_pmid_by_CID_MeSH, prefix, header, data, url, 1000, 1000000, "data/metab2mesh/CID_MESH/", 8)
# Get CID distinct PMID :
parallelize_query_by_offset(count_cid, distinct_pmid_by_CID, prefix, header, data, url, 10000, 10000, "data/metab2mesh/CID_PMID/", 8)

# Count distinct MESH
data["query"] = count_mesh_query
count_mesh_res = requests.post(url = url, headers = header, data = data)
count_mesh = int(count_mesh_res.text.splitlines().pop(1))
# Get MeSH distinct PMID :
parallelize_query_by_offset(count_mesh, distinct_pmid_by_MeSH, prefix, header, data, url, 3000, 3000, "data/metab2mesh/MESH_PMID/", 8)

# On compte le nombre total de distinct pmids qui ont un CID et un MeSH
data["query"] = prefix + distinct_all_pmids
count_pmids_res = requests.post(url = url, headers = header, data = data)
count_pmids = int(count_pmids_res.text.splitlines().pop(1))
# Nb. total pmids = 8754160

# Extract MeSH Names
parallelize_query_by_offset(count_mesh, MESH_name, prefix, header, data, url, 3000, 30000, "data/metab2mesh/MESH_LABEL/", 8)
# To Extract CID Names, please use the PubChem translation service at https://pubchem.ncbi.nlm.nih.gov/idexchange/idexchange.cgi using a list of all cids (ex: all_linked_ids)
# The same thing was done for CID

# Extract list of pmids associated to a CID - MeSH co-occurence, separated by ";". WARNING: In the request, the group concat term must be in the last select because of large string can't be handeling by sub-queries ans link to a superior select. 
# However, to handle offset with large "order by", the order by term must be placed in a sub query, before output all results, but the group_concat muste be in the firs select so ... problem !
# So the order provided in this query is the same as in the others

parallelize_query_by_offset(count_cid, list_of_distinct_pmid_by_CID_MeSH, prefix, header, data, url, 100, 1000000, "data/metab2mesh/CID_MESH_PMID_LIST/", 6)


df_metab2mesh = prepare_data_frame("data/metab2mesh/CID_MESH/res_full.csv", "data/metab2mesh/CID_PMID/res_full.csv", "data/metab2mesh/MESH_PMID/res_full.csv", count_pmids, "data/metab2mesh/res2/", 30000)