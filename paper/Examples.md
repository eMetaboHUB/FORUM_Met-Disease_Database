# Exemples

- Comparaison des résultats avec metab2mesh (liens simples)
  - CID - MESH test case Cyclic AMP
  - MESH - CID test cas Phenylketonurias 
- Exemple avec Propagation:
  - Résultat associations gagnées : 
    - Test case Oxyfedrine
    - Test case ChEBI + Phenylketonuria
  - Résultats associatiosn perdues :
    - Test Case Eau + Eukaryote
  - Résultat Analyse globale :
    - Imidocarb dipropionate


# Examples

Metab2MeSh [1] was a web server dedicated to the annotation of compounds with biomedical concepts defined in the MeSH Thesaurus, largely appreciated and used in the community [2-6]. Unfortunately, this tool is no longer available since 2019, impacting tools using it as a data provider or to corroborate other results or hypotheses. Metab2MeSHBis was created to fill this gap, but, using linked data, it improve several aspects of the original tool, mainly on provided annotations, data accessibility and manipulation. In order to validate our approache, it is critical to ensure that association made by metab2mesh are also conserved in our tool. We used the same test cases as in the Metab2MeSH article: diseases related to Cyclic AMP and compouds related to Phenylketonuria by literature evidences (data were respectively retrieve from the supplementary Figures 2 and 3).

## Diseases related to Cyclic AMP

Table X compares results from Metab2MeSH and our tool for diseases associated to Cyclic AMP, using an identical approache (without propagation) or using the propagation through the MeSH thesaurus. Using an identical approache, all diseases associations are conserved, with similar statistics of p-value, Fold-Change and Chisq-Stat, but as the corpus of each assoication grow each year, they relies today on more articles.

When propaging associations to MeSH ancestors through the Thesaurus, corpus of MeSH which are not leaf can increase if some of their child terms are also associated to the compound. In Table X, corpus of *Neuroblastoma* does not change even if it has two child-terms (*Esthesioneuroblastoma* and *Ganglioneuroblastoma*), because they are never associated to Cyclic AMP in our Knowledge base. *Glioma* has 10 child-terms and his corpus size increase by more than 44% using the propagation, as his child-terms are also associated to Cyclic AMP in our Knowledge base. *Cystic Fibrosis* being a leaf in the MeSH Thesaurus, his corpus is not affected by the propagation.












[1] Sartor, M.A., Ade, A., Wright, Z., States, D., Omenn, G.S., Athey, B., Karnovsky, A., 2012. Metab2MeSH: annotating compounds with medical subject headings. Bioinformatics 28, 1408–1410. https://doi.org/10.1093/bioinformatics/bts156
[2] Fukushima, A., Kusano, M., 2013. Recent Progress in the Development of Metabolome Databases for Plant Systems Biology. Front. Plant Sci. 4. https://doi.org/10.3389/fpls.2013.00073
[3] Guney, E., Menche, J., Vidal, M., Barábasi, A.-L., 2016. Network-based in silico drug efficacy screening. Nat Commun 7, 10331. https://doi.org/10.1038/ncomms10331
[4] Sas, K.M., Karnovsky, A., Michailidis, G., Pennathur, S., 2015. Metabolomics and Diabetes: Analytical and Computational Approaches. Diabetes 64, 718–732. https://doi.org/10.2337/db14-0509
[5] Cavalcante, R.G., Patil, S., Weymouth, T.E., Bendinskas, K.G., Karnovsky, A., Sartor, M.A., 2016. ConceptMetab: exploring relationships among metabolite sets to identify links among biomedical concepts. Bioinformatics 32, 1536–1543. https://doi.org/10.1093/bioinformatics/btw016
[6] Duren, W., Weymouth, T., Hull, T., Omenn, G.S., Athey, B., Burant, C., Karnovsky, A., 2014. MetDisease—connecting metabolites to diseases via literature. Bioinformatics 30, 2239–2241. https://doi.org/10.1093/bioinformatics/btu179