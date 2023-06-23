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
# 
import pandas as pd


def upload_dataset(csv_path, name_prefix):
    """
    Upload csv dataset which format is not "standard"
    :param csv_path: <user, item, rating, ... > csv file
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    :return: pandas dataframe: <user, item, rating>

    """
    matrix = pd.read_csv(csv_path, header=0, sep=',')
    matrix = matrix[['user', 'item', 'rating']]
    # filter rows for specific ontology
    return matrix[matrix['item'].astype(str).str.startswith(name_prefix)]
