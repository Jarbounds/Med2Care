import os
import shutil
import pandas as pd
import numpy as np
import json
import unidecode

def main():

    # directory where we move unique files
    

    
    # count=0
    # articles_to_garbage = []
    # for filename in os.listdir(dst_dir):
    #     with open(dst_dir + filename, encoding='utf-8') as json_file:
    #         j_file_original = json.load(json_file)
    #         article_id = get_article_id(j_file_original)
    #         list_of_authors = get_authors_names(j_file_original)
    #         if len(list_of_authors)==0:
    #             if (metadata[metadata.sha == article_id].authors.values is np.nan): 
    #                 print(metadata[metadata.sha == article_id].authors.values)
    #                 articles_to_garbage.append(filename)
                             
    #     json_file.close()        
    # print(pd.DataFrame(articles_to_garbage))
    # try:
    #     if not os.path.exists(dst_dir_garbage):
    #         os.makedirs(dst_dir_garbage)
    # except OSError as error:
    #     print(error)

    # for filename in articles_to_garbage:        
    #     shutil.move(os.path.join(dst_dir, filename), \
    #             os.path.join(dst_dir_garbage, filename))

# # Separate

    dst_dir = '../data/comm_use_subset/'
    dst_dir1 = '../data/comm_use_subset1/'
    dst_dir2 = '../data/comm_use_subset2/'
    dst_dir3 = '../data/comm_use_subset3/'
    dst_dir4 = '../data/comm_use_subset4/'
    dst_dir5 = '../data/comm_use_subset5/'
    dst_dir01 = '../data/comm_use_subset_entities/'
    dst_dir11 = '../data/comm_use_subset1_entities/'
    dst_dir21 = '../data/comm_use_subset2_entities/'
    dst_dir31 = '../data/comm_use_subset3_entities/'
    dst_dir41 = '../data/comm_use_subset4_entities/'
    dst_dir51 = '../data/comm_use_subset5_entities/'
    source = '../data/comm_use_subset_nonpmc/'
    source_pmc = '../data/comm_use_subset_pmc/'
    source_entities = '../data/comm_use_subset_nonpmc_entities/'
    source_entities_pmc = '../data/comm_use_subset_pmc_entities/'

    try:
        if not os.path.exists(source):
            os.makedirs(source)
            os.makedirs(source_pmc)
    except OSError as error:
        print(error)   
    
    
    for filename in os.listdir(dst_dir):    
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir, filename), \
                os.path.join(source_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir, filename), \
                os.path.join(source, filename))        

    for filename in os.listdir(dst_dir1):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir1, filename), \
                os.path.join(source_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir1, filename), \
                os.path.join(source, filename)) 

    for filename in os.listdir(dst_dir2):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir2, filename), \
                os.path.join(source_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir2, filename), \
                os.path.join(source, filename))   

    for filename in os.listdir(dst_dir3):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir3, filename), \
                os.path.join(source_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir3, filename), \
                os.path.join(source, filename)) 

    for filename in os.listdir(dst_dir4):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir4, filename), \
                os.path.join(source_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir4, filename), \
                os.path.join(source, filename))    

    for filename in os.listdir(dst_dir5):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir5, filename), \
                os.path.join(source_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir5, filename), \
                os.path.join(source, filename)) 

    try:
        if not os.path.exists(source_entities):
            os.makedirs(source_entities)
            os.makedirs(source_entities_pmc)
    except OSError as error:
        print(error)   

    for filename in os.listdir(dst_dir01):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir01, filename), \
                os.path.join(source_entities_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir01, filename), \
                os.path.join(source_entities, filename))       

    for filename in os.listdir(dst_dir11):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir11, filename), \
                os.path.join(source_entities_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir11, filename), \
                os.path.join(source_entities, filename))      

    for filename in os.listdir(dst_dir21):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir21, filename), \
                os.path.join(source_entities_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir21, filename), \
                os.path.join(source_entities, filename))      

    for filename in os.listdir(dst_dir31):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir31, filename), \
                os.path.join(source_entities_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir31, filename), \
                os.path.join(source_entities, filename))      

    for filename in os.listdir(dst_dir41):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir41, filename), \
                os.path.join(source_entities_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir41, filename), \
                os.path.join(source_entities, filename))        

    for filename in os.listdir(dst_dir51):        
        if filename.startswith('PMC'):    
            shutil.copy2(os.path.join(dst_dir51, filename), \
                os.path.join(source_entities_pmc, filename))
        else:
            shutil.copy2(os.path.join(dst_dir51, filename), \
                os.path.join(source_entities, filename))      

    # count = 0
    # for filename in os.listdir(dst_dir):        
    #     shutil.move(os.path.join(dst_dir, filename), \
    #             os.path.join(dst_dir2, filename))
    #     count+=1
    #     if count > int(len(os.listdir(dst_dir))/3):        
    #         break

    # try:
    #     if not os.path.exists(dst_dir3):
    #         os.makedirs(dst_dir3)
    # except OSError as error:
    #     print(error)   

    # count = 0
    # for filename in os.listdir(dst_dir):        
    #     shutil.move(os.path.join(dst_dir, filename), \
    #             os.path.join(dst_dir3, filename))
    #     count+=1
    #     if count > int(len(os.listdir(dst_dir))/2):        
    #         break

    # try:
    #     if not os.path.exists(dst_dir4):
    #         os.makedirs(dst_dir4)
    # except OSError as error:
    #     print(error)   

    # count = 0
    # for filename in os.listdir(dst_dir):        
    #     shutil.move(os.path.join(dst_dir, filename), \
    #             os.path.join(dst_dir4, filename))
    #     count+=1
    #     if count > 5000:        
    #         break

    
# # Join files

    # for filename in os.listdir(dst_dir1):        
    #     shutil.move(os.path.join(dst_dir1, filename), \
    #             os.path.join(dst_dir, filename))
    # #os.remove(dst_dir1)
    # for filename in os.listdir(dst_dir2):        
    #     shutil.move(os.path.join(dst_dir2, filename), \
    #             os.path.join(dst_dir, filename))
    # #os.remove(dst_dir2)
    # for filename in os.listdir(dst_dir3):        
    #     shutil.move(os.path.join(dst_dir3, filename), \
    #             os.path.join(dst_dir, filename))
    # #os.remove(dst_dir3)

    # print(f'number of files - first: {len(os.listdir(dst_dir))}')
    # print(f'number of files - second: {len(os.listdir(dst_dir1))}')
    # print(f'number of files - third: {len(os.listdir(dst_dir2))}')

## Entities files
    dst_dire = '../data/comm_use_subset_entities/'
    dst_dire1 = '../data/comm_use_subset1_entities/'
    dst_dire2 = '../data/comm_use_subset2_entities/'
    dst_dire3 = '../data/comm_use_subset3_entities/'
    dst_dire4 = '../data/comm_use_subset4_entities/'
    print()
    # for filename in os.listdir(dst_dir1):        
    #     shutil.move(os.path.join(dst_dir1, filename), \
    #             os.path.join(dst_dir, filename))
    # os.remove(dst_dir1)

    # for filename in os.listdir(dst_dir2):        
    #     shutil.move(os.path.join(dst_dir2, filename), \
    #             os.path.join(dst_dir, filename))
    # os.remove(dst_dir2)

    # for filename in os.listdir(dst_dir3):        
    #     shutil.move(os.path.join(dst_dir3, filename), \
    #             os.path.join(dst_dir, filename))
    # os.remove(dst_dir3)

    
    # print(f'number of all files: {len(os.listdir('../data/comm_use_subset/'))}')
    # print(f'number of all files with NER2: {len(os.listdir('../data/comm_use_subset_entities/'))}')

        
    
    # print(f'number of transfered files: {len(os.listdir(dst_dir2))}')
    # print(f'number of  files: {len(os.listdir(dst_dir3))}')

    # print(f'number of files with NER: {len(os.listdir(dst_dir_entities))}')

if __name__ == '__main__':
    main()

