###############################################################################
#                                                                             #
# Licensed under the Apache License, Version 2.0 (the "License"); you may     #
# not use this file except in compliance with the License. You may obtain a   #
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0           #
#                                                                             #
# Unless required by applicable law or agreed to in writing, software         #
# distributed under the License is distributed on an "AS IS" BASIS,           #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
# See the License for the specific language governing permissions and         #
# limitations under the License.                                              #
#                                                                             #
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
import configargparse


class MyConfiguration:
    __instance = None

    def __init__(self, options):

        """
        Virtually private constructor.
        """
        if MyConfiguration.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.dataset = options.path_to_dataset

            self.host = options.host
            self.port = options.port
            self.user = options.user
            self.password = options.password
            self.database = options.database

            self.path_to_owl = options.path_to_owl
            self.path_to_ontology = options.path_to_ontology_db

            self.n_split = options.n_split_dataset
            self.item_prefix = options.items_prefix

        MyConfiguration.__instance = self

    @staticmethod
    def get_instance() -> 'MyConfiguration':
        """ Static access method. """
        if MyConfiguration.__instance is None:
            p = configargparse.ArgParser(default_config_files=['../configurations/configurations.ini'])
            p.add('-mc', '--my-configurations', is_config_file=True, help='alternative configurations file path')

            p.add("-ds", "--path_to_dataset", required=False, help="path to dataset", type=str)
            p.add("-host", "--host", required=False, help="db host", type=str)
            p.add("-port", "--port", required=False, help="db host port", type=str)
            p.add("-user", "--user", required=False, help="db user", type=str)
            p.add("-pwd", "--password", required=False, help="db password", type=str)
            p.add("-db_name", "--database", required=False, help="db name", type=str)
            p.add("-table_name", "--table_name", required=False, help="table name", type=str)

            p.add("-owl", "--path_to_owl", required=False, help="path to owl ontology", type=str)
            p.add("-db_onto", "--path_to_ontology_db", required=False, help="path to ontology db", type=str)

            p.add("-prefix", "--items_prefix", required=False, help="items prefix", type=str)
            p.add("-n_split", "--n_split_dataset", required=False, help="number to split the list of entities",
                  type=int)

            MyConfiguration(p.parse_args())

        return MyConfiguration.__instance


if __name__ == '__main__':
    s = MyConfiguration.get_instance()
    print(s)
    print(MyConfiguration.get_instance().host)
    print(MyConfiguration.get_instance().database)
    print(MyConfiguration.get_instance().user)
    print(MyConfiguration.get_instance().path_to_ontology)
    print(s.database)
