import os

from utils.utils2database import dump_database
from utils.myconfiguration import MyConfiguration as Config


if __name__ == '__main__':
    config: Config = Config.get_instance()

    database_name = config.database

    dump_path = f'{config.path2dbdump}/{database_name.split("_")[0]}'

    os.makedirs(dump_path, exist_ok=True)

    print('Dumping similarity_chebi table')
    dump_database(
        database_name,
        'similarity_chebi',
        'comp_1,comp_2,sim_resnik,sim_lin,sim_jc',
        dump_path
    )

    print('Dumping similarity_structural_chebi table')
    dump_database(
        database_name,
        'similarity_structural_chebi',
        'comp_1,comp_2,sim_tanimoto,sim_morgan',
        dump_path
    )

    print('Dumping norm_similarity_chebi_sim_jc table')
    dump_database(
        database_name,
        'norm_similarity_chebi_sim_jc',
        'comp_1,comp_2,sim_jc,l2,zscore,`min-max`,tanh,`log-sig`',
        dump_path
    )

    print('Dumping norm_similarity_chebi_sim_lin table')
    dump_database(
        database_name,
        'norm_similarity_chebi_sim_lin',
        'comp_1,comp_2,sim_lin,l2,zscore,`min-max`,tanh,`log-sig`',
        dump_path
    )

    print('Dumping norm_similarity_chebi_sim_resnik table')
    dump_database(
        database_name,
        'norm_similarity_chebi_sim_resnik',
        'comp_1,comp_2,sim_resnik,l2,zscore,`min-max`,tanh,`log-sig`',
        dump_path
    )

    print('Dumping norm_similarity_structural_chebi_sim_morgan table')
    dump_database(
        database_name,
        'norm_similarity_structural_chebi_sim_morgan',
        'comp_1,comp_2,sim_morgan,l2,zscore,`min-max`,tanh,`log-sig`',
        dump_path
    )

    print('Dumping norm_similarity_structural_chebi_sim_tanimoto table')
    dump_database(
        database_name,
        'norm_similarity_structural_chebi_sim_tanimoto',
        'comp_1,comp_2,sim_tanimoto,l2,zscore,`min-max`,tanh,`log-sig`',
        dump_path
    )
