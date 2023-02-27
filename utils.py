import pandas as pd
import numpy as np
from hyperparas import HyperParas
import time


def df_to_COMM_REG_dict(df, key_list):
    # transfer df(obtained using txt files in original gtap dataset) to dict
    dict_ = {}
    for i, row in df.iterrows():
        dict_key = tuple([row[key_] for key_ in key_list])
        dict_[dict_key] = row['VALUE']
    return dict_


def txt_to_COMM_REG_dict(txt_path, key_list):
    # transfer txt files in original gtap dataset to dict
    return df_to_COMM_REG_dict(pd.read_table(txt_path, delimiter=','), key_list)


def get_item_index(comm, reg, hyper: HyperParas):
    comm_index, reg_index = hyper.activities_list.index(comm.lower()), hyper.regions_list.index(reg.lower())
    return reg_index * hyper.num_commodities + comm_index


def raw_dict_to_matrix(raw_dict, matrix_type, key_mapping, hyper: HyperParas):
    if matrix_type == 'Z':
        Z = np.zeros((hyper.num_items, hyper.num_items))
        for key_info in raw_dict:
            REG_SOU, COMM_SOU, REG_TAR, COMM_TAR = key_info[key_mapping['REG_SOU_index_in_key']], \
                                                   key_info[key_mapping['COMM_SOU_index_in_key']], \
                                                   key_info[key_mapping['REG_TAR_index_in_key']], \
                                                   key_info[key_mapping['COMM_TAR_index_in_key']]
            loc_row, loc_col = get_item_index(COMM_SOU, REG_SOU, hyper), \
                               get_item_index(COMM_TAR, REG_TAR, hyper)
            Z[loc_row, loc_col] = raw_dict[key_info]
        return Z
    elif matrix_type == 'F':
        F = np.zeros((hyper.num_items, hyper.num_regions))
        for key_info in raw_dict:
            REG_SOU, COMM_SOU, REG_TAR = key_info[key_mapping['REG_SOU_index_in_key']], \
                                         key_info[key_mapping['COMM_SOU_index_in_key']], \
                                         key_info[key_mapping['REG_TAR_index_in_key']]
            loc_row, loc_col = get_item_index(COMM_SOU, REG_SOU, hyper), \
                               hyper.regions_list.index(REG_TAR)
            F[loc_row, loc_col] = raw_dict[key_info]
        return F
    elif matrix_type == 'comm_to_firm':
        comm_to_firm = np.zeros((hyper.num_commodities, hyper.num_items))
        for key_info in raw_dict:
            COMM_SOU, REG_TAR, COMM_TAR = key_info[key_mapping['COMM_SOU_index_in_key']], \
                                          key_info[key_mapping['REG_TAR_index_in_key']], \
                                          key_info[key_mapping['COMM_TAR_index_in_key']]
            loc_row, loc_col = hyper.activities_list.index(COMM_SOU), get_item_index(COMM_TAR, REG_TAR, hyper)
            comm_to_firm[loc_row, loc_col] = raw_dict[key_info]
        return comm_to_firm
    elif matrix_type == 'comm_to_region_final':
        comm_to_region_final = np.zeros((hyper.num_commodities, hyper.num_regions))
        for key_info in raw_dict:
            COMM_SOU, REG_TAR = key_info[key_mapping['COMM_SOU_index_in_key']], \
                                key_info[key_mapping['REG_TAR_index_in_key']]
            loc_row, loc_col = hyper.activities_list.index(COMM_SOU), hyper.regions_list.index(REG_TAR)
            comm_to_region_final[loc_row, loc_col] = raw_dict[key_info]
        return comm_to_region_final
    elif matrix_type == 'firm_to_region_final':
        firm_to_region_final = np.zeros((hyper.num_items, hyper.num_regions))
        for key_info in raw_dict:
            COMM_SOU, REG_SOU, REG_TAR = key_info[key_mapping['COMM_SOU_index_in_key']], \
                                         key_info[key_mapping['REG_SOU_index_in_key']], \
                                         key_info[key_mapping['REG_TAR_index_in_key']]
            loc_row, loc_col = get_item_index(COMM_SOU, REG_SOU, hyper), hyper.regions_list.index(REG_TAR)
            firm_to_region_final[loc_row, loc_col] = raw_dict[key_info]
        return firm_to_region_final
    elif matrix_type == 'va_all_factors':
        va_all_factors = np.zeros(hyper.num_items)
        for key_info in raw_dict:
            COMM, REG = key_info[key_mapping['COMM_index_in_key']], \
                        key_info[key_mapping['REG_index_in_key']]
            loc = get_item_index(COMM, REG, hyper)
            va_all_factors[loc] += raw_dict[key_info]
        return va_all_factors


def row_sum_n_col(array_, n_col):
    # row sum: for each row, [sum of columns: 0~n_col-1, sum of columns: n_col~2*n_col-1, ...]
    return np.sum(np.reshape(array_, (-1, int(np.shape(array_)[1] / n_col), n_col)), axis=2)


def col_sum_each_n_row(array_, n_row):
    # col sum: for each column, [sum of rows: 0,n_row, 2*n_row...;
    #                            sum of rows: 1,n_row+1, 2*n_row+1...;
    #                            ...]
    return np.sum(np.reshape(array_, (-1, n_row, int(np.shape(array_)[1]))), axis=0)


def recover_international_Z_F(imports_firms_to_region, imports_comm_to_firm, imports_comm_to_region_final,
                              exports_firm_to_region, hyper):
    imports_comm_to_region = col_sum_each_n_row(imports_firms_to_region,
                                                hyper.num_commodities)
    product_distribution_firm = imports_comm_to_firm / np.repeat(imports_comm_to_region, hyper.num_commodities, axis=1)
    product_distribution_final = imports_comm_to_region_final / imports_comm_to_region

    return np.repeat(exports_firm_to_region, hyper.num_commodities, axis=1) * np.tile(product_distribution_firm,
                                                                                      (hyper.num_regions, 1)), \
           exports_firm_to_region * np.tile(product_distribution_final, (hyper.num_regions, 1))


def RAS_matrix_balancing(A, u, v):
    """
    balance matrix based on the RAS approach
    :param A: original matrix
    :param u: targeted row sum
    :param v: targeted col sum
    :return: X: balanced matrix
    """
    X = A.copy()
    print('------balancing.....------')
    for i in range(500):
        b = time.time()
        R = u / np.sum(X, axis=1)
        X = X * R[:, None]
        S = v / np.sum(X, axis=0)
        X = X * S[None, :]
        print(i, time.time() - b)
    return X


def MRIOT_adjust(Z_, VA_, F_, num_comm_):
    """
    :param Z_: shape: num_item, num_item
    :param VA_: shape: num_item
    :param F_: shape: num_item, num_reg
    :param num_reg_:
    :param num_comm_:
    :return:
    """
    # keep constant
    Y_without_VA = np.sum(Z_, axis=0)
    VA_by_country = row_sum_n_col(np.reshape(VA_, (1, -1)), num_comm_).flatten()

    # targeted row sum
    U = Y_without_VA + VA_
    # targeted col sum
    V = np.concatenate((Y_without_VA, VA_by_country))
    # Z_F_MRIOT: not including VA in balancing
    Z_F_MRIOT = np.concatenate((Z_, F_), axis=1)

    Z_F_MRIOT_adjusted = RAS_matrix_balancing(Z_F_MRIOT, U, V)
    return Z_F_MRIOT_adjusted


if __name__ == '__main__':
    # sample check
    num_regions, num_commodities = 3, 4
    num_items = num_regions * num_commodities
    Z = np.random.randint(1, 4, (num_items, num_items))
    VA = np.random.randint(1, 4, num_items)
    F = np.random.randint(1, 4, (num_items, num_regions))
    mriot = MRIOT_adjust(Z, VA, F, num_commodities)

    # condition check
    Y_without_VA = np.sum(Z, axis=0)
    VA_by_country = row_sum_n_col(np.reshape(VA, (1, -1)), num_commodities).flatten()
    Y_init = Y_without_VA + VA

    print('----- init ----------------')
    mriot_init = np.concatenate((Z, F), axis=1)
    mriot_row = np.sum(mriot_init, axis=1)
    print(mriot_row, Y_init)

    mriot_col = np.sum(mriot_init, axis=0)
    print(mriot_col[:num_items], Y_init)
    print(mriot_col[num_items:], VA_by_country)

    print('----- balanced ----------------')
    mriot_balance_row = np.sum(mriot, axis=1)
    print(mriot_balance_row, Y_init)

    mriot_balance_col = np.sum(mriot, axis=0)
    print(mriot_balance_col[:num_items], Y_init)
    print(mriot_balance_col[num_items:], VA_by_country)
