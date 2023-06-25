###############################################################################
#                                                                             #  
# @author Matilde Pato                                                        #  
# @email: matilde.pato@isel.pt                                                #
# @date: February, 12th 2021                                                  #
# @version: 1.0                                                               #  
# @last update:                                                               #   
#                                                                             #  
#                                                                             #  
###############################################################################
# 
import configargparse


class MyConfiguration:
    __instance = None

    @staticmethod
    def get_instance() -> "MyConfiguration":
        """ Static access method. """
        if MyConfiguration.__instance is None:
            p = configargparse.ArgParser(default_config_files=['../configurations/configurations.ini'])

            p.add('-mc', '--my-configurations', is_config_file=True, help='alternative configurations file path')

            p.add("-ds", "--path2ds", required=False, help="path to dataset", type=str)
            p.add("-ds_kb", "--path2kb", required=False, help="path to kb dataset", type=str)

            p.add("-db_dump", "--path2dbdump", required=False, help="path to database table dumps", type=str)

            p.add("-info", "--path2info", required=False, help="info about process", type=str)

            p.add("-n", "--n", required=False, help="n most similar items", type=float)
            p.add("-normalized", "--normalized", required=False, help="normalized values", type=int)

            p.add("-host", "--host", required=False, help="db host", type=str)
            p.add("-port", "--port", required=False, help="db host port", type=str)
            p.add("-user", "--user", required=False, help="db user", type=str)
            p.add("-pwd", "--password", required=False, help="db password", type=str)
            p.add("-db_name", "--database", required=False, help="db name", type=str)
            p.add("-tablename", "--tablename", required=False, help="table name", type=str)

            p.add("-pathchebi", "--path_owl_chebi", required=False, help="path to chebi ontology", type=str)
            p.add("-pathdoid", "--path_owl_doid", required=False, help="path to do ontology", type=str)
            p.add("-pathgo", "--path_owl_go", required=False, help="path to go ontology", type=str)
            p.add("-pathhp", "--path_owl_hp", required=False, help="path to hp ontology", type=str)

            p.add("-pathdbchebi", "--path_db_chebi", required=False, help="path to chebi ontology", type=str)
            p.add("-pathdbdoid", "--path_db_doid", required=False, help="path to do ontology", type=str)
            p.add("-pathdbgo", "--path_db_go", required=False, help="path to go ontology", type=str)
            p.add("-pathdbhp", "--path_db_hp", required=False, help="path to hp ontology", type=str)

            p.add("-item", "--item_prefix", required=False, help="1st item prefix to load", type=str)

            MyConfiguration(p.parse_args())

        return MyConfiguration.__instance

    def __init__(self, options):

        """
        Virtually private constructor.
        """
        if MyConfiguration.__instance is not None:
            raise Exception("This class is a singleton!")
        else:

            self.n = options.n
            self.normalized = options.normalized

            self.host = options.host
            self.port = options.port
            self.user = options.user
            self.password = options.password
            self.database = options.database
            self.tablename = options.tablename

            self.path_owl_chebi = options.path_owl_chebi
            self.path_owl_doid = options.path_owl_doid
            self.path_owl_go = options.path_owl_go
            self.path_owl_hp = options.path_owl_hp

            self.path_db_chebi = options.path_db_chebi
            self.path_db_doid = options.path_db_doid
            self.path_db_go = options.path_db_go
            self.path_db_hp = options.path_db_hp

            self.item_prefix = options.item_prefix

            self.path2ds = options.path2ds
            self.path2kb = options.path2kb

            self.path2dbdump = options.path2dbdump

            self.path2info = options.path2info

        MyConfiguration.__instance = self
