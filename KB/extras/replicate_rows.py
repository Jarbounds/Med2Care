import numpy as np
import pandas as pd


# df_dataset = pd.DataFrame(np.array([[0,'CHEBI_15361', 1], [0,'CHEBI_15378', 1], [0,'CHEBI_15362', 1], [17,'CHEBI_15361', 1], [52,'CHEBI_15361', 1], \
#     [67,'CHEBI_15361', 1]]), columns=['user', 'item', 'rating'])

# item1 = 'CHEBI_15361'
# item2 = ['CHEBI_103229', 'CHEBI_150', 'CHEBI_17818', 'CHEBI_24156', \
#     'CHEBI_34386', 'CHEBI_50934', 'CHEBI_51286', 'CHEBI_66106', 'CHEBI_8186', 'CHEBI_88',\
#     'CHEBI_96062'] 

# # find index where item1 exist in dataframe
# idx = df_dataset.index[df_dataset['item']==item1].tolist()
# # replicate for each user the item2 where similarity semantic between items are higher
# pair = [{'user': df_dataset['user'].iloc[i], 'item': c, 'rating':df_dataset['rating'].iloc[i]} for i in idx for c in item2 ]
# # append values from orginal dataframe and sort by user
# df_dataset = df_dataset.append(pair, ignore_index=True).sort_values(by=['user'])  
# print(df_dataset)

dfl = pd.DataFrame(np.random.randn(5, 4),columns=list('ABCD'),index=pd.date_range('20130101', periods=5))  
dfl=dfl[['A','B']]      
print(dfl)