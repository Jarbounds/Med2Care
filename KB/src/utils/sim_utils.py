# To solve SPAQRL query
# https://github.com/RDFLib/rdflib/issues/1702
# Try to downgrade the version of pyparsing to 2.x or
# upgrade to the latest RDFLib, the fix should be included in RDFLib 6.1.1."
# import pkg_resources
# pkg_resources.require("pyparsing==2.4.7")

from rdflib import Graph, Namespace

# Define ChEBI namespace
onto_ns = Namespace("http://purl.obolibrary.org/obo/")


def get_id(entity_uri, onto):
    # Extract the numeric part after "CHEBI_" or "DOID_" from the entity URI
    return entity_uri.split(f"{onto}_")[1]


def get_ancestors(id, onto, onto_graph: Graph):
    entity_uri = onto_ns[f"{onto}_{id}"]
    # List to store the ancestors of the entity
    ancestors = []

    # Recursive function to find the ancestors of the entity
    def find_ancestors(entity_uri):
        query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?parent
            WHERE {{
                <{entity_uri}> rdfs:subClassOf ?parent .
            }}
        """
        results = onto_graph.query(query)
        direct_ancestors = [str(parent) for (parent,) in results if parent.startswith(onto_ns)]

        for ancestor_uri in direct_ancestors:
            if ancestor_uri not in ancestors:
                ancestors.append(ancestor_uri)
                find_ancestors(ancestor_uri)

    # Start the recursive search for ancestors
    find_ancestors(entity_uri)
    ancestors_id = [get_id(a, onto) for a in ancestors]

    return ancestors_id


# Example usage:
def main():
    # Load the ChEBI ontology
    owl_file = "teste.owl"  # Replace with the path to your ChEBI ontology OWL file
    g = Graph()
    g.load(owl_file)

    # Replace '41879' with the actual ChEBI ID you want to query
    chebi_id = "41879"
    ancestors = get_ancestors(chebi_id, "CHEBI", g)

    print(f"Ancestors of ChEBI:{chebi_id}:")
    for parent in ancestors:
        print(f"{chebi_id} - {parent}")


if __name__ == "__main__":
    main()
