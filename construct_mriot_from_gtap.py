import pickle
import numpy as np
import utils
import pandas as pd
import time
from hyperparas import HyperParas

hyper = HyperParas()


def get_Z_domestic():
    ### get info for domestic Z
    # lowercase_uppercase: code in gtap v7_code in gtap v10
    # purchase: from COMM_SOU in REG to COMM_TAR in REG
    vdfm_VDFB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VDFB.txt', ['COMM_SOU', 'COMM_TAR', 'REG'])
    # construct domestic Z
    Z_domestic = utils.raw_dict_to_matrix(vdfm_VDFB_dict, 'Z', {'REG_SOU_index_in_key': 2,
                                                                'COMM_SOU_index_in_key': 0,
                                                                'REG_TAR_index_in_key': 2,
                                                                'COMM_TAR_index_in_key': 1}, hyper)
    return Z_domestic


def get_F_domestic():
    ## get info for domestic y
    # final domestic household: from COMM in REG to Final in REG
    vdpm_VDPB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VDPB.txt', ['COMM', 'REG'])
    domestic_firm_to_region_final_house = utils.raw_dict_to_matrix(vdpm_VDPB_dict, 'firm_to_region_final',
                                                                   {'COMM_SOU_index_in_key': 0,
                                                                    'REG_SOU_index_in_key': 1,
                                                                    'REG_TAR_index_in_key': 1}, hyper)
    # final domestic gov: from COMM in REG to Final in REG
    vdgm_VDGB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VDGB.txt', ['COMM', 'REG'])
    domestic_firm_to_region_final_gov = utils.raw_dict_to_matrix(vdgm_VDGB_dict, 'firm_to_region_final',
                                                                 {'COMM_SOU_index_in_key': 0,
                                                                  'REG_SOU_index_in_key': 1,
                                                                  'REG_TAR_index_in_key': 1}, hyper)

    # final domestic inv: from COMM in REG to Final in REG
    vdkm_VDIB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VDIB.txt', ['COMM', 'REG'])
    domestic_firm_to_region_final_inv = utils.raw_dict_to_matrix(vdkm_VDIB_dict, 'firm_to_region_final',
                                                                 {'COMM_SOU_index_in_key': 0,
                                                                  'REG_SOU_index_in_key': 1,
                                                                  'REG_TAR_index_in_key': 1}, hyper)
    # final domestic vst: from COMM in REG to Final in REG
    vst_VST_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VST.txt', ['COMM', 'REG'])
    domestic_firm_to_region_final_vst = utils.raw_dict_to_matrix(vst_VST_dict, 'firm_to_region_final',
                                                                 {'COMM_SOU_index_in_key': 0,
                                                                  'REG_SOU_index_in_key': 1,
                                                                  'REG_TAR_index_in_key': 1}, hyper)

    # final domestic all
    F_domestic = domestic_firm_to_region_final_house + domestic_firm_to_region_final_gov + \
                 domestic_firm_to_region_final_inv + domestic_firm_to_region_final_vst
    return F_domestic


def get_international_Z_F():
    ### get info for international Z
    # exports: from COMM in REG_SOU to REG_TAR
    vxmd_VXSB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VXSB.txt', ['COMM', 'REG_SOU', 'REG_TAR'])
    exports_firm_to_region = utils.raw_dict_to_matrix(vxmd_VXSB_dict, 'F', {'REG_SOU_index_in_key': 1,
                                                                            'COMM_SOU_index_in_key': 0,
                                                                            'REG_TAR_index_in_key': 2}, hyper)
    # imports: COMM_SOU to COMM_TAR in REG
    vifm_VMFB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VMFB.txt', ['COMM_SOU', 'COMM_TAR', 'REG'])
    imports_comm_to_firm = utils.raw_dict_to_matrix(vifm_VMFB_dict, 'comm_to_firm', {'COMM_SOU_index_in_key': 0,
                                                                                     'COMM_TAR_index_in_key': 1,
                                                                                     'REG_TAR_index_in_key': 2}, hyper)
    # imports: from COMM in REG_SOU to REG_TAR
    vims_VMSB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VMSB.txt', ['COMM', 'REG_SOU', 'REG_TAR'])
    imports_firms_to_region = utils.raw_dict_to_matrix(vims_VMSB_dict, 'F',
                                                       {'COMM_SOU_index_in_key': 0,
                                                        'REG_SOU_index_in_key': 1,
                                                        'REG_TAR_index_in_key': 2}, hyper)

    # final imports household: COMM to Final in REG
    vipm_VMPB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VMPB.txt', ['COMM', 'REG'])
    imports_comm_to_region_final_house = utils.raw_dict_to_matrix(vipm_VMPB_dict, 'comm_to_region_final',
                                                                  {'COMM_SOU_index_in_key': 0,
                                                                   'REG_TAR_index_in_key': 1}, hyper)
    ## get infor for international y
    # final imports gov: COMM to Final in REG
    vigm_VMGB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VMGB.txt', ['COMM', 'REG'])
    imports_comm_to_region_final_gov = utils.raw_dict_to_matrix(vigm_VMGB_dict, 'comm_to_region_final',
                                                                {'COMM_SOU_index_in_key': 0,
                                                                 'REG_TAR_index_in_key': 1}, hyper)

    # final imports inv: COMM to Final in REG
    vikm_VMIB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/VMIB.txt', ['COMM', 'REG'])
    imports_comm_to_region_final_inv = utils.raw_dict_to_matrix(vikm_VMIB_dict, 'comm_to_region_final',
                                                                {'COMM_SOU_index_in_key': 0,
                                                                 'REG_TAR_index_in_key': 1}, hyper)
    # total imports to final
    imports_comm_to_region_final = \
        imports_comm_to_region_final_house + imports_comm_to_region_final_gov + imports_comm_to_region_final_inv

    # construct international Z & y
    Z_international, F_international = utils.recover_international_Z_F(imports_firms_to_region, imports_comm_to_firm,
                                                                       imports_comm_to_region_final,
                                                                       exports_firm_to_region, hyper)
    return Z_international, F_international


def get_value_add_firm():
    # get info for value added
    vfm_EVFB_dict = utils.txt_to_COMM_REG_dict('raw_gtap_dataset/EVFB.txt', ['FAC', 'COMM', 'REG'])
    factor_purchase_firms_vfm = utils.raw_dict_to_matrix(vfm_EVFB_dict, 'va_all_factors',
                                                         {'COMM_index_in_key': 1,
                                                          'REG_index_in_key': 2}, hyper)
    value_added_firm = factor_purchase_firms_vfm
    return value_added_firm


def get_raw_MRIOT():
    # get info for value-added cal
    print('------------ Constructing domestic Z... --------------')
    b = time.time()
    Z_domestic = get_Z_domestic()
    print('------------ Done ({}s) --------------'.format(time.time()-b))

    print('------------ Constructing domestic F... --------------')
    b = time.time()
    F_domestic = get_F_domestic()
    print('------------ Done ({}s) --------------'.format(time.time()-b))

    print('------------ Constructing international Z and F... --------------')
    b = time.time()
    Z_international, F_international = get_international_Z_F()
    print('------------ Done ({}s) --------------'.format(time.time()-b))

    Z = Z_domestic + Z_international
    F = F_domestic + F_international

    print('------------ Constructing VA... --------------')
    b = time.time()
    VA = get_value_add_firm()
    print('------------ Done ({}s) --------------'.format(time.time()-b))

    print('------------ Saving raw Z, F, VA... --------------')
    b = time.time()
    with open('processed_gtap/Z_init.pkl', 'wb') as f:
        pickle.dump(Z, f)
    with open('processed_gtap/F_init.pkl', 'wb') as f:
        pickle.dump(F, f)
    with open('processed_gtap/VA_init.pkl', 'wb') as f:
        pickle.dump(VA, f)
    print('------------ Done ({}s) --------------'.format(time.time()-b))


#  read raw data
get_raw_MRIOT()

print('------------ Loading raw Z, F, VA... --------------')
b = time.time()
with open('processed_gtap/Z_init.pkl', 'rb') as f:
    Z_init = pickle.load(f)
with open('processed_gtap/F_init.pkl', 'rb') as f:
    F_init = pickle.load(f)
with open('processed_gtap/VA_init.pkl', 'rb') as f:
    VA_init = pickle.load(f)
print('------------ Done ({}s) --------------'.format(time.time()-b))

# balance MRIOT
print('------------ Balancing MRIOT... --------------')
b = time.time()
adjusted_MRIOT_ZF_part = utils.MRIOT_adjust(Z_init, VA_init, F_init, int(len(VA_init) / np.shape(F_init)[1]))
print('------------ Done ({}s) --------------'.format(time.time()-b))

# ---- balance check -------------
Y_without_VA = np.sum(Z_init, axis=0)
VA_by_country = utils.row_sum_n_col(np.reshape(VA_init, (1, -1)), 65).flatten()
Y_init = Y_without_VA + VA_init

mriot_balance_row = np.sum(adjusted_MRIOT_ZF_part, axis=1)
# balance: mriot_balance_row, Y_init

mriot_balance_col = np.sum(adjusted_MRIOT_ZF_part, axis=0)
# balance: mriot_balance_col[:9165] + VA_init, Y_init
# balance: mriot_balance_col[9165:], VA_by_country

# ------- save final MRIOT -------------------------------
print('------------ Saving balanced MRIOT... --------------')
b = time.time()
MRIOT = np.concatenate((adjusted_MRIOT_ZF_part,
                        np.concatenate([np.reshape(VA_init, (1, -1)),
                                        np.ones((1, hyper.num_regions)) * np.nan], axis=1)),
                       axis=0)
df = pd.DataFrame(MRIOT)

indexes = []
for region in hyper.regions_list:
    for act in hyper.activities_list:
        indexes.append(region + '_' + act)
df.set_axis(indexes + ['VA'], axis=0, inplace=True)
df.set_axis(indexes + ['y_' + region for region in hyper.regions_list], axis=1, inplace=True)
with open('processed_gtap/adjusted_MRIOT_df.pkl', 'wb') as f:
    pickle.dump(df, f)
print('------------ Done ({}s) --------------'.format(time.time()-b))
