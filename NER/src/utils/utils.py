###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 29 Apr 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 01 Oct 2021 - News functions were used (after line 100)      #      
#   (author: matilde.pato@gmail.com  )                                        # 
#                                                                             #   
#                                                                             #  
###############################################################################

import os
import shutil


def new_folder(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError as error:
        print(error)


def new_file(file):
    try:
        if not os.path.isfile(file):
            f = open(file, 'w')
            f.close()
    except OSError as error:
        print(error)


def set_blacklist(file, line):
    """
    This function receives the article to and saves them in the
    blacklist file. The blacklist contains all invalid articles, such
    as non-authors, non-entities, and others
    :param  file: name of txt file
    :param  line: all content
    :return none
    """

    new_file(file)
    with open(file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n')
        f.write(content)
        f.close()


def save_metadata(file, metadata):
    """
    This function will save all metadata about the process in txt file
    :param  file: name of txt file
    :param metadata: the contents to write
    :return None
    """

    new_file(file)
    with open(file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(metadata.rstrip('\r\n') + '\n')
        f.write('------------------------------------------------------' + '\n' + content)


def create_output_folder(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def create_entities_folder(src):
    # Change the current working directory to path
    os.chdir(src)
    # input_dir is new
    input_dir = os.path.basename(os.getcwd())
    # Return one folder back  
    os.chdir('..')

    # Create a new directory if not exists
    if not os.path.exists(input_dir.rstrip("/") + "_entities/"):
        os.makedirs(input_dir.rstrip("/") + "_entities/")

    output_dir = input_dir.rstrip("/") + "_entities/"
    return input_dir, output_dir


def input_parameters(args):
    if len(args) == 2:
        return ["chebi", "do", "go", "hpo", "taxon", "cido"]
    # if entities is defined by user then saved it in a list
    lexicons = []
    for i in args[2:]:
        lexicons.append(i)
    print(f'Entities to be found: {lexicons}')
    # else all entities are listed    

    return lexicons


def transfer_file(lst_files: list, src: str, dst: str, flag: str) -> None:
    """
    Copy or move files from one folder to another, based on list of files.

    :param  lst_files: list of file names to copy or move
    :param  src: path of source
    :param  dst: path of destination
    :param  flag: constant value 'copy' or 'move'
    :return None

    E.g.
    File copied successfully.
    ../data/document_parses/pdf_json/3e7204f7030a9956a95b58d84d283d85229cc117.json
    """

    new_folder(dst)

    print(f'{flag} files!')
    for file in lst_files:
        if os.path.isfile(os.path.join(src, file)):
            try:
                if flag == 'copy':
                    shutil.copy(os.path.join(src, file), os.path.join(dst, file))
                elif flag == 'move':
                    shutil.move(os.path.join(src, file), os.path.join(dst, file))
            # For other errors
            except:
                print(f"Error occurred while {flag} file.")
        else:
            print("file does not exist: file")
    print(f'End of {flag} successfully.')