from utils.utils2database import dump_database


if __name__ == '__main__':
    dump_database(
        'entities_sim_med2care_rs',
        'similarity_chebi',
        'comp_1,comp_2,sim_resnik,sim_lin,sim_jc'
    )
    dump_database(
        'entities_sim_med2care_rs',
        'similarity_structural_chebi',
        'comp_1,comp_2,sim_tanimoto,sim_morgan'
    )

    dump_database(
        'entities_sim_med2care_rs',
        'norm_similarity_chebi_sim_jc',
        'comp_1,comp_2,sim_jc,l2,zscore,min-max,tanh,log-sig'
    )
    dump_database(
        'entities_sim_med2care_rs',
        'norm_similarity_chebi_sim_lin',
        'comp_1,comp_2,sim_lin,l2,zscore,min-max,tanh,log-sig'
    )
    dump_database(
        'entities_sim_med2care_rs',
        'norm_similarity_chebi_sim_resnik',
        'comp_1,comp_2,sim_resnik,l2,zscore,min-max,tanh,log-sig'
    )
    dump_database(
        'entities_sim_med2care_rs',
        'norm_similarity_structural_chebi_sim_morgan',
        'comp_1,comp_2,sim_morgan,l2,zscore,min-max,tanh,log-sig'
    )
    dump_database(
        'entities_sim_med2care_rs',
        'norm_similarity_structural_chebi_sim_tanimoto',
        'comp_1,comp_2,sim_tanimoto,l2,zscore,min-max,tanh,log-sig'
    )
