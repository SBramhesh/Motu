from io import StringIO
from io import BytesIO
import streamlit as st
import xlsxwriter
import pandas as pd
import re
import copy
import numpy as np
from functools import partial, reduce
pd.options.display.precision = 2


def get_first_table(string_data):
    print(string_data.split(r'EARFCNDL')
          [1].split(r'GLOBALCELLID')[0])
    textt = string_data.split(r'EARFCNDL')[
        1].split(r'GLOBALCELLID')[0]
    ddfn = pd.read_csv(StringIO(textt.strip()),
                       sep='|', skiprows=2, header=None)
    return textt


def get_lte_car_df(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ru-|Sector.*[^,]= (ad|op).*State|isSharedWithExternalMe|prod|(main|oper).*indicator|con.*power|noOf.xAntennas|sectorFunctionRef|availableHwOutputPower|reservedBy') > -1:
            table_list = entry.split('MO')[2:-2]
    lte_list = "\nMO " + "".join(table_list)
    df_car = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    return df_car.dropna()


def get_pre_cell_df1(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)

    split_str = "MO                                               ;sleepState"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc CellSleepFunction= sleepState') > -1:
            table_list = entry.split(split_str)[1].split('----------------')[0]
    lte_list = split_str + "".join(table_list)
    # lte_list = split_str + map1['PRE_CELL']
    df_pre1 = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_pre1.columns = [x.strip() for x in df_pre1.columns.to_list()]
    return df_pre1.iloc[:, :]


def get_post_cell_df1(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)

    split_str = "MO                                               ;sleepState"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc CellSleepFunction= sleepState') > -1:
            table_list = entry.split(split_str)[1].split('----------------')[0]
    lte_list = split_str + "".join(table_list)
    # lte_list = split_str + map1['PRE_CELL']
    df_pre1 = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_pre1.columns = [x.strip() for x in df_pre1.columns.to_list()]
    return df_pre1.iloc[:, :]


def get_pre_cell_df2(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    map = {}
    map1 = {}
    split_str = "MO                           ;additionalPlmnReservedList "
    for index, entry in enumerate(entries):
        if entry.find('hgetc ^EutranCell.DD= additionalPlmnReservedList|administrativeState|cellBarred|operationalState|primaryPlmnReserved') > -1:
            # st.sidebar.write(entry)
            map[index] = entry.split(split_str)[1].split('----------------')[0]
    # map.keys = ['pre_cell', 'post_cell']
    for indx, k in enumerate(list(map.keys())):
        if indx == 0:
            map1['PRE_CELL'] = map[k]
        else:
            map1['POST_CELL'] = map[k]
    # st.sidebar.write(map1)

    split_str = "MO                           ;additionalPlmnReservedList "
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ^EutranCell.DD= additionalPlmnReservedList|administrativeState|cellBarred|operationalState|primaryPlmnReserved') > -1:
            table_list = entry.split(split_str)[1].split('----------------')[0]
    lte_list = split_str + "".join(table_list)
    lte_list = split_str + map1['PRE_CELL']
    df_pre2 = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_pre2.columns = [x.strip() for x in df_pre2.columns.to_list()]
    return df_pre2.iloc[:, :]


def get_post_cell_df2(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    map = {}
    map1 = {}
    split_str = "MO                           ;additionalPlmnReservedList "
    for index, entry in enumerate(entries):
        if entry.find('hgetc ^EutranCell.DD= additionalPlmnReservedList|administrativeState|cellBarred|operationalState|primaryPlmnReserved') > -1:
            # st.sidebar.write(entry)
            map[index] = entry.split(split_str)[1].split('----------------')[0]
    # map.keys = ['pre_cell', 'post_cell']
    for indx, k in enumerate(list(map.keys())):
        if indx == 0:
            map1['PRE_CELL'] = map[k]
        else:
            map1['POST_CELL'] = map[k]
    # st.sidebar.write(map1)

    split_str = "MO                           ;additionalPlmnReservedList "
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ^EutranCell.DD= additionalPlmnReservedList|administrativeState|cellBarred|operationalState|primaryPlmnReserved') > -1:
            table_list = entry.split(split_str)[1].split('----------------')[0]
    lte_list = split_str + "".join(table_list)
    lte_list = split_str + map1['POST_CELL']
    df_pre2 = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_pre2.columns = [x.strip() for x in df_pre2.columns.to_list()]
    return df_pre2.iloc[:, :]


def get_pre_cell_df(string_data, node_name):
    pre_cell_df1 = get_pre_cell_df1(string_data, node_name)
    pre_cell_df2 = get_pre_cell_df2(string_data, node_name)
    sleep_list = pre_cell_df1['sleepState'].to_list()
    pre_cell_df2['sleepState'] = sleep_list
    df_final = pre_cell_df2
    df_final = mod_col(['administrativeState', 'cellBarred',
                       'operationalState', 'sleepState'], df_final)
    df_final = mod_col_equal(['additionalPlmnReservedList'], df_final)
    # st.sidebar.write(pre_cell_df1)
    # st.sidebar.write(pre_cell_df2)
    # st.sidebar.write(df_final)
    return df_final


def get_post_cell_df(string_data, node_name):
    pre_cell_df1 = get_post_cell_df1(string_data, node_name)
    pre_cell_df2 = get_post_cell_df2(string_data, node_name)
    sleep_list = pre_cell_df1['sleepState'].to_list()
    pre_cell_df2['sleepState'] = sleep_list
    df_final = pre_cell_df2
    df_final = mod_col(['administrativeState', 'cellBarred',
                       'operationalState', 'sleepState'], df_final)
    df_final = mod_col_equal(['additionalPlmnReservedList'], df_final)
    # st.sidebar.write(pre_cell_df1)
    # st.sidebar.write(pre_cell_df2)
    # st.sidebar.write(df_final)
    return df_final


def get_pre_cell_df_nr(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    mapp = {}
    map2 = {}
    split_str = "MO                         ;administrativeState;bandList  "
    for index, entry in enumerate(entries):
        #     print(entry)
        if entry.find('hgetc NRCellDU= (ad|op).*State|cell(Barred|LocalId|Range|ReservedForOperator|State)|nRCellDUId|nRPCI|nRTAC|^bandList$|^rachRootSequence$') > -1:
            print('yes')
            mapp[index] = entry.split(
                split_str)[1].split('----------------')[0]
    # map.keys = ['pre_cell', 'post_cell']
    for indx, k in enumerate(list(mapp.keys())):
        if indx == 0:
            map2['PRE_CELL'] = mapp[k]
        else:
            map2['POST_CELL'] = mapp[k]
    split_str = "MO                         ;administrativeState;bandList  "
    table_list = ""
    for entry in entries:
        if entry.find('hgetc NRCellDU= (ad|op).*State|cell(Barred|LocalId|Range|ReservedForOperator|State)|nRCellDUId|nRPCI|nRTAC|^bandList$|^rachRootSequence$') > -1:
            table_list = entry.split(split_str)[1].split('----------------')[0]
    lte_list = split_str + "".join(table_list)
    lte_list = split_str + map2['PRE_CELL']
    df_pre_nr = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_pre_nr.columns = [x.strip() for x in df_pre_nr.columns.to_list()]
    df_pre_nr = mod_col(['administrativeState', 'cellBarred', 'cellState',
                         'operationalState', 'cellReservedForOperator'], df_pre_nr)
    df_pre_nr = mod_col_equal(['bandList'], df_pre_nr)
    return df_pre_nr


def get_post_cell_df_nr(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    mapp = {}
    map2 = {}
    split_str = "MO                         ;administrativeState;bandList  "
    for index, entry in enumerate(entries):
        #     print(entry)
        if entry.find('hgetc NRCellDU= (ad|op).*State|cell(Barred|LocalId|Range|ReservedForOperator|State)|nRCellDUId|nRPCI|nRTAC|^bandList$|^rachRootSequence$') > -1:
            print('yes')
            mapp[index] = entry.split(
                split_str)[1].split('----------------')[0]
    # map.keys = ['pre_cell', 'post_cell']
    for indx, k in enumerate(list(mapp.keys())):
        if indx == 0:
            map2['PRE_CELL'] = mapp[k]
        else:
            map2['POST_CELL'] = mapp[k]
    split_str = "MO                         ;administrativeState;bandList  "
    table_list = ""
    for entry in entries:
        if entry.find('hgetc NRCellDU= (ad|op).*State|cell(Barred|LocalId|Range|ReservedForOperator|State)|nRCellDUId|nRPCI|nRTAC|^bandList$|^rachRootSequence$') > -1:
            table_list = entry.split(split_str)[1].split('----------------')[0]
    lte_list = split_str + "".join(table_list)
    lte_list = split_str + map2['POST_CELL']
    df_pre_nr = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_pre_nr.columns = [x.strip() for x in df_pre_nr.columns.to_list()]
    df_pre_nr = mod_col(['administrativeState', 'cellBarred', 'cellState',
                         'operationalState', 'cellReservedForOperator'], df_pre_nr)
    df_pre_nr = mod_col_equal(['bandList'], df_pre_nr)
    return df_pre_nr


def get_cell_state_df_lte(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    table_list = ""
    for entry in entries:
        if entry.find('hgetc (^Eu|^nb).*cel.*[^,]= cellBarred') > -1:
            table_list = entry.split('MO')[2:]
    lte_list = "\nMO " + "".join(table_list)
    df_cs = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_cs.columns = [x.strip() for x in df_cs.columns.to_list()]
    # st.sidebar.write(df_cs.dropna())
    df_cs = mod_col(['administrativeState', 'cellBarred',
                     'operationalState'], df_cs.dropna())
    df_cs = mod_col_equal(['additionalPlmnReservedList'], df_cs)
    return df_cs


def get_cell_state_df_nr(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    nr_list = ""
    for entry in entries:
        if entry.find('hgetc NRCellDU= (ad|op).*State|cell(Barred') > -1:
            nr_list = entry.split('MO')[2:]
    nrr_list = "\nMO " + "".join(nr_list)
    nr_cs = pd.read_csv(StringIO(nrr_list.strip()),   sep=';', header=0)
    nr_cs.columns = [x.strip() for x in nr_cs.columns.to_list()]
    nr_cs = mod_col(['administrativeState', 'cellBarred',
                     'cellReservedForOperator', 'operationalState', 'cellState'], nr_cs.dropna())
    nr_cs = mod_col_equal(['bandList'], nr_cs)
    return nr_cs


def get_mmbb_invx_cell_df(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    split_str = "FRU   ;LNH      ;BOARD      ;RF  ;BP  ;TX (W/dBm)  ;VSWR (RL)   ;RX (dBm) ;UEs/gUEs  ;Sector/AntennaGroup/Cells (State:CellIds:PCIs)"
    # split_str ="FRU    ;LNH      ;BOARD         ;RF  ;BP  ;TX (W/dBm)  ;VSWR (RL)   ;RX (dBm) ;UEs/gUEs"
    table_list = ""
    for entry in entries:
        if entry.find(' invxrbc') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[1].split('----------------')[0]
    lte_list = split_str + "".join(table_list)
    df_invxm = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_invxm.dropna(inplace=True)
    df_invxm.columns = [x.strip() for x in df_invxm.columns.to_list()]
    df_invx_f = df_invxm[['FRU', 'BOARD', 'LNH', 'RF', 'VSWR (RL)']]
    cellids = df_invxm.iloc[:, -1].to_list()
    cell_id = list(map(lambda x: x.split(' ')[2], cellids))
    tup_list = tuple(map(lambda x: x.split('='), cell_id))
    tech, fdd = map(list, zip(*tup_list))
    tech_list = list(map(lambda x: 'LTE' if x ==
                     'FDD' or x == 'LDD' else 'NR', tech))
    fdd_list = list(map(lambda x: (node_name + "_" + x)
                    if x.find('UNEN') == -1 else x, fdd))
    eq_list = ['=' for items in fdd_list]
    tf_list = list(reduce(partial(map, str.__add__),
                   (tech, eq_list, fdd_list)))
    tff_list = []
    for i in range(len(fdd_list)):
        tff_list.append(tech[i] + "=" + fdd_list[i])
    df_invx_f['TECH'] = tech_list
    df_invx_f['FDD'] = tf_list
    # df_invx_f[['TECH', 'FDD', 'FRU','BOARD','LNH', 'RF', 'VSWR (RL)']]
    vswr_list = df_invx_f['VSWR (RL)']
    v_list = list(map(lambda x: x.split('(')[1].split(')')[0], vswr_list))
    df_invx_f['VSWR (RL)'] = v_list
    return df_invx_f[['TECH', 'FDD', 'FRU', 'BOARD', 'LNH', 'RF', 'VSWR (RL)']]


def get_mmbb_lte_traffic(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    split_str = "Time  Object                        pmErabEstabAttInit pmErabEstabSuccInit pmRrcConnEstabAtt pmRrcConnEstabSucc"
    table_list = ""
    for entry in entries:
        if entry.find('pmxh . pmErabEstabAttInit$|pmErabEstabSuccInit$|pmRrcConnEstabAtt$|pmRrcConnEstabSucc$') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[1]
    lte_list = split_str + "".join(table_list)
    ltte_list = lte_list.split('\n')

    fin_list = []
    print(f'===>>>{len(ltte_list)}')
    for i in range(len(ltte_list)):
        te_list = ltte_list[i].split(' ')
        tee_list = [x for x in te_list if len(x) > 0]
        fin_list.append(tee_list)
    df_mtraff = pd.DataFrame(fin_list)
    df_mtraff.columns = fin_list[0]
    df_mtraf = df_mtraff.iloc[1:-6, :]

    split_str = "coli>/fruacc/lhsh 000100 /lrat/ue print"
    table_list = ""
    for entry in entries:
        if entry.find('lh mp ue print -admitted') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[1].split('================')[0]
    llte_list = "".join(table_list)
    lttee_list = llte_list.split('\n')
    map_list = [item[5:].strip() for item in lttee_list[1: -1]]
    mapp_list = []
    for i in range(len(map_list)):
        mapp_list.append(
            [item for item in map_list[i].split(' ') if len(item) > 0])
    df_map = pd.DataFrame(mapp_list)
    df_map.columns = mapp_list[0]
    df_mapp = df_map.iloc[1:, :]
    split_str = "MO                           ;cellId;crsGain;dlChannelBandwidth;dlInternalChannelBandwidth;earfcndl;earfcnul;isDlOnly;rachRootSequence;sectorCarrierRef     ;tac ;ulChannelBandwidth;ulInternalChannelBandwidth"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ^EutranCell.DD= ^cellid$|^tac$|^earfcn.l$|lchannelbandwidth|rachRootSequence|isdlonly|crsgain|sectorcarrierref') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[1]
    ltee_list = split_str + "".join(table_list)
    lttea_list = ltee_list.split('\n')

    df_mapy = pd.read_csv(StringIO(ltee_list.strip()),   sep=';', header=0)
    # df_mapy.dropna
    df_mapyy = df_mapy.iloc[:, :2]
    df_mapyy.columns = ['Object', 'CellId']

    mtraf_obj = df_mtraf['Object']

    c_list = []
    for index, i in enumerate(mtraf_obj):
        if index < len(df_mapyy['Object']):
            if df_mapyy['Object'][index].find(i) > -1:
                #             print("yes")
                c_list.append(df_mapyy['CellId'][index])
            else:
                c_list.append(" ")
        else:
            c_list.append(0)
    df_mtraf['CellId'] = c_list

    ue_list = []
    bear_list = []

    ue_dict = {}
    # ue_dict.keys = df_mapp['CellId']
    # dir(ue_dict)

    for index, item in enumerate(df_mapp['CellId']):
        ue_dict[int(item)] = [df_mapp['#UE:s'][index+1],
                              df_mapp['#Bearers'][index+1]]
    ue_dict.keys()

    for i in list(df_mtraf['CellId']):
        if i in ue_dict:
            ue_list.append(str(ue_dict[i][0]))
            bear_list.append(str(ue_dict[i][1]))
        else:
            ue_list.append('0')
            bear_list.append('0')

    # st.sidebar.write(df_mtraf)
    # st.sidebar.write(ue_list)
    # st.sidebar.write(bear_list)
    df_mtraf['ue'] = ue_list
    df_mtraf['bear'] = bear_list

    return df_mtraf


def get_mmbb_ext_alarm(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    split_str = "MO                                    ;administrativeState;alarmSlogan              ;normallyOpen;operationalState;perceivedSeverity"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ,alarmport slogan|administrativeState|normallyOpen|operationalState|perceivedSeverity . ^[A-Z0-9]') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[1]
    lte_list = split_str + "".join(table_list)
    df_alport = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_alport.columns = [x.strip() for x in df_alport.columns.to_list()]
    rbs_list = [item.split(' ')[0]
                for item in df_alport['alarmSlogan'].to_list()]
    df_alport['RBS'] = rbs_list
    df_alport['alarmSlogan'] = [
        " ".join(item.split(' ')[1:]) for item in df_alport['alarmSlogan'].to_list()]
    df_alport['MO'] = [item.split(',')[1]
                       for item in df_alport['MO'].to_list()]
    df_alportt = mod_col(
        ['administrativeState', 'operationalState', 'perceivedSeverity'], df_alport)
    return df_alportt[['MO', 'administrativeState', 'RBS', 'alarmSlogan', 'normallyOpen', 'operationalState', 'perceivedSeverity']]


def get_mmbb_rsu(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    split_str = "MO                                               ;electricalAntennaTilt;iuantAntennaModelNumber;iuantAntennaSerialNumber;iuantBaseStationId;iuantSectorId;maxTilt;minTilt;operationalState;userLabel"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc AntennaNearUnit=|RetSubUnit= (admin|oper).*State|iuantDeviceType|UniqueId|productNumber|rfportref|tilt$|antenna[ms]|sectorid|stationid|userlabel') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[1]
    lte_list = split_str + "".join(table_list)
    ltte_list = lte_list.split('\n')

    fin_list = []
    print(f'===>>>{len(ltte_list)}')
    for i in range(len(ltte_list)):
        te_list = ltte_list[i].split(';')
        tee_list = [x for x in te_list if len(x) > 0]
        fin_list.append(tee_list)

    head_list = list(map(lambda x: x.split(';'), fin_list[0]))
    headd_list = []
    for l in head_list:
        for item in l:
            headd_list.append(item)
    headr_list = [x for x in headd_list if len(x) > 0]
    df_mrsu = pd.DataFrame(fin_list)
    # df_mrsu.columns = headr_list
    df_mrsu.dropna(how='all', axis=0)
    suff_list = list(map(lambda x: '' if not x else x,
                     df_mrsu.iloc[:, -1].to_list()))
    pref_list = df_mrsu.iloc[:, -2].to_list()
    llist = []
    for i in range(len(pref_list)):
        llist.append(str(pref_list[i]).strip() + str(suff_list[i]).strip())

    df_mrsu['UserLabel'] = llist
    dff_mrsu = df_mrsu.iloc[:, :-3]
    dff_mrsu['UserLabel'] = df_mrsu.iloc[:, -1].to_list()
    dff_mrsu.columns = headr_list
    # st.sidebar.write(dff_mrsu)
    dff_mrsu.columns = [x.strip() for x in dff_mrsu.columns.to_list()]
    dff_mrsu = mod_col(['operationalState'], dff_mrsu.iloc[1:-2, :])
    return dff_mrsu


def get_inv_prod_df(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    split_str = "ID ;LINK ;RiL ;VENDOR1      ;VENDORPROD1"
    table_list = ""
    for entry in entries:
        if entry.find(' invxrbc') > -1:
            table_list = entry.split(split_str)[1].split('----------------')[0]
    lte_list = split_str + "".join(table_list)
    df_invx_prod = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    return df_invx_prod.iloc[1:, :]


def get_attn_df(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    split_str = ";auPortRef"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc rfbranch= Attenuation$|Delay$|^auPortRef$|^rfPortRef$') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[1]
    lte_list = 'MO ' + split_str + "".join(table_list)
    df_attn = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_attn.columns = [x.strip() for x in df_attn.columns.to_list()]
    df_attn['auPortRef'] = ["".join(x.split('=')[1:])
                            for x in df_attn['auPortRef']]
    df_attn['ulAttenuation'] = [
        "".join(x.split('=')[1:]) for x in df_attn['ulAttenuation']]
    df_attn['ulTrafficDelay'] = [
        "".join(x.split('=')[1:]) for x in df_attn['ulTrafficDelay']]
    df_attn['dlAttenuation'] = [
        "".join(x.split('=')[1:]) for x in df_attn['dlAttenuation']]
    df_attn['dlTrafficDelay'] = [
        "".join(x.split('=')[1:]) for x in df_attn['dlTrafficDelay']]

    return df_attn


def get_asm_df(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    split_str = "Tx/Rx Tot       Median  Highest  20perc  80perc"
    table_list = ""
    for entry in entries:
        if entry.find('! $perl $scripts/WPsinr.pl $tempdir/$asmvarfn.dummySinr  $pvar $ovar $2txvar $4txvar') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[1].split(
                'Percentiles 20 and 80')[0]
    lte_list = 'UNL05524 Branch' + split_str + "".join(table_list)
    ltte_list = lte_list.split('\n')
    tte_list = [x for x in ltte_list if len(x) > 0]
    f_list = []
    for row in tte_list:
        f_list.append([x for x in row.split(' ')if len(x) > 0])
    df_asm = pd.DataFrame(f_list)

    df_asm.columns = f_list[0]
    df_asmm = df_asm.iloc[1:, : -2]
    b_list = df_asmm['BranchTx/Rx']
    bb_list = []
    for x in b_list:
        bb_list.append(x.replace('/', 'X'))
    df_asmm['BranchTx/Rx'] = bb_list
    c_list = df_asmm.columns.to_list()
    c_list[0] = 'Branch'
    c_list[1] = 'Tx/Rx'
    df_asmm.columns = [c_list]
    return df_asmm


def get_mmbb_sdi(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    split_str = "Node;MomVersion;SW;Date;ID ;RiL ;Type ;Res ;MO1-MO2        ;BOARD1-BOARD2"
    table_list = ""
    for entry in entries:
        if entry.find('sdijrc') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[1]
    lte_list = split_str + "".join(table_list)
    df_sdi = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_sdi.columns = [x.strip() for x in df_sdi.columns.to_list()]
    return df_sdi[['Node', 'MomVersion', 'MO1-MO2', 'BOARD1-BOARD2']]


def mod_col(cols, df_mxru):
    for col in cols:
        ad_list = df_mxru[col]
        df_mxru[col] = [item.split('(')[1].split(')')[0] for item in ad_list]
    return df_mxru


def mod_col_equal(cols, df_mxru):
    for col in cols:
        ad_list = df_mxru[col]
        df_mxru[col] = [item.split('=')[1] for item in ad_list]
    return df_mxru


def get_mmbb_ru_df(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    split_str = "MO                        ;administrativeState;isSharedWithExternalMe;maintenanceIndicator;operationalIndicator;operationalState;productName   ;productNumber;productRevision;productionDate;reservedBy;serialNumber"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ru-|Sector.*[^,]= (ad|op).*State|isSharedWithExternalMe|prod|(main|oper).*indicator|con.*power|noOf.xAntennas|sectorFunctionRef|availableHwOutputPower|reservedBy|arfcndl|bSChannelBwDL') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[1].split('.....')[0]
    lte_list = split_str + "".join(table_list)
    ltte_list = lte_list.split('\n')

    fin_list = []
    print(f'===>>>{len(ltte_list)}')
    for i in range(len(ltte_list)):
        te_list = ltte_list[i].split(';')
        tee_list = [x for x in te_list if len(x) > 0]
        fin_list.append(tee_list)

    head_list = list(map(lambda x: x.split(';'), fin_list[0]))
    headd_list = []
    for l in head_list:
        for item in l:
            headd_list.append(item)
    headr_list = [x for x in headd_list if len(x) > 0]
    df_mru = pd.DataFrame(fin_list)
    df_mru.columns = headr_list
    rsv_list = ['' for item in df_mru['reservedBy']]
    df_mru['reservedBy'] = rsv_list
    df_mmru = df_mru.iloc[1:-1, :]
    df_mmru = mod_col(['administrativeState', 'operationalIndicator',
                       'operationalState', 'maintenanceIndicator'], df_mmru)
    # st.sidebar.write(df_mmru)
    return df_mmru


def get_mmbb_configuration_df(string_data, node_name):
    node_search = node_name + ">"
    entries = re.split(node_search, string_data)
    df_conf2_nr = get_df_conf2_nr(entries)
    df_conf1_lte = get_df_conf1_lte(entries)
    df_conf3_lte = get_df_conf3_lte(entries)
    df_conf4_lte = get_df_conf4_lte(entries)
    df_conf6_nr = get_df_conf6_nr(entries)
    df_conf5_lte_nr = get_df_conf5_lte_nr(entries)
    enb_id = get_enb_id(entries)
    enb_list = [enb_id for i in range(len(df_conf1_lte))]
    lte_tech_list = ['LTE' for i in range(len(df_conf1_lte))]
    node_list = [node_name for i in range(len(df_conf1_lte))]
    rach_list = df_conf1_lte['rachRootSequence'].to_list()
    gain_list = [str(x) for x in df_conf1_lte['crsGain'].to_list()]
    cell_id_list = df_conf1_lte['cellId'].to_list()
    power_list = [
        str(int(z)) + '_' for z in df_conf3_lte['configuredMaxTxPower'].to_list()]
    a_list = df_conf5_lte_nr['availableHwOutputPower'].to_list()[:-3]
    cp_ap_list = []
    for index, i in enumerate(power_list):
        cp_ap_list.append(str(i) + str(a_list[index]))
    # st.sidebar.write(a_list)
    # st.sidebar.write(power_list)
    # st.sidebar.write(cp_ap_list)

    rx_list = [str(int(x))
               for x in df_conf3_lte['noOfRxAntennas'].to_list()]
    tx_list = [str(int(x))
               for x in df_conf3_lte['noOfTxAntennas'].to_list()]

    tx_rx_list = []
    for index, z in enumerate(tx_list):
        tx_rx_list.append(z + 'X' + rx_list[index])

    Ulc_list = ['UlComp' + x.split('UlComp')[1].strip()
                for x in df_conf3_lte['reservedBy'].to_list()]
    cell_name_list = [x.split('=')[1].strip()
                      for x in df_conf1_lte['MO'].to_list()]

    cell_name_list_nr = [x.split('=')[1].strip()
                         for x in df_conf4_lte['MO'].to_list()]
    cell_name_list = cell_name_list + cell_name_list_nr

    cell_id_list_nr = df_conf4_lte['cellLocalId'].to_list()
    cell_id_list = cell_id_list + cell_id_list_nr

    gnb_id = get_gnb_id(entries)
    enb_list_nr = [gnb_id for i in range(len(df_conf4_lte))]
    enb_list = enb_list + enb_list_nr

    tech_list_nr = ['NR' for i in range(len(df_conf4_lte))]
    lte_tech_list = lte_tech_list + tech_list_nr

    node_list_nr = [node_name for i in range(len(df_conf4_lte))]
    node_list = node_list + node_list_nr

    gain_list_nr = ['NA' for i in range(len(df_conf4_lte))]
    gain_list = gain_list + gain_list_nr

    Ulc_list_nr = gain_list_nr
    Ulc_list = Ulc_list + Ulc_list_nr

    rach_list_nr = df_conf4_lte['rachRootSequence'].to_list()
    rach_list = rach_list + rach_list_nr

    rx_list_nr = [str(int(x))
                  for x in df_conf6_nr['noOfRxAntennas'].to_list()]
    tx_list_nr = [str(int(x))
                  for x in df_conf6_nr['noOfTxAntennas'].to_list()]
    tx_rx_list_nr = []
    for index, z in enumerate(tx_list_nr):
        tx_rx_list_nr.append(z + 'X' + rx_list_nr[index])

    tx_rx_list = tx_rx_list + tx_rx_list_nr

    power_list_nr = [
        str(int(z)) + '_' for z in df_conf6_nr['configuredMaxTxPower'].to_list()]
    a_list_nr = df_conf5_lte_nr['availableHwOutputPower'].to_list()[:-3]
    p_list_nr = []
    for index, i in enumerate(power_list_nr):
        p_list_nr.append(str(i) + str(a_list_nr[index]))
    cp_ap_list = cp_ap_list + p_list_nr

    conf_data = {'Tech': lte_tech_list, 'Site ID': node_list, 'Cell Name': cell_name_list, 'Cell Id': cell_id_list,
                 'GNB/ENB ID': enb_list, 'CRS Gain': gain_list, 'Rach': rach_list,
                 'CPower_APower': cp_ap_list, 'TX_RX': tx_rx_list, 'UlCompGroup': Ulc_list}
    # st.sidebar.write(conf_data)
    # st.sidebar.write(a_list_nr)
    # st.sidebar.write(power_list_nr)
    # st.sidebar.write(p_list_nr)

    # Create DataFrame
    return pd.DataFrame(conf_data)


def get_df_conf2_nr(entries):
    split_str = "MO                                ;administrativeState;arfcnDL"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ru-|Sector.*[^,]= (ad|op).*State|isSharedWithExternalMe|prod|(main|oper).*indicator|con.*power|noOf.xAntennas|sectorFunctionRef|availableHwOutputPower|reservedBy|arfcndl|bSChannelBwDL') > -1:
            table_list = entry.split(split_str)[1].split('MO')[0]
    lte_list = split_str + "".join(table_list)
    df_conf2 = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_conf2.columns = [x.strip() for x in df_conf2.columns.to_list()]
    return df_conf2.dropna()


def get_df_conf1_lte(entries):
    split_str = "MO                           ;cellId"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ^EutranCell.DD= ^cellid$|^tac$|^earfcn.l$|lchannelbandwidth|rachRootSequence|isdlonly|crsgain|sectorcarrierref') > -1:
            table_list = entry.split(split_str)[1].split('----------------')[0]
    lte_list = split_str + "".join(table_list)
    df_conf1 = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_conf1.columns = [x.strip() for x in df_conf1.columns.to_list()]
    return df_conf1


def get_enb_id(entries):
    split_str = "eNBId"
    table_list = ""
    for entry in entries:
        if entry.find('get ^enodebfunction=1 ^eNBId$') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[2].split('\n')[0]
    enode_list = "".join(table_list)
    return enode_list.strip()


def get_gnb_id(entries):
    split_str = "gNBId"
    table_list = ""
    for entry in entries:
        if entry.find('get ^GNBDUFunction=1 ^gNBId$') > -1:
            #         print(entry)
            table_list = entry.split(split_str)[2].split('\n')[0]
    enode_list = "".join(table_list)
    return enode_list.strip()


def get_df_conf3_lte(entries):
    split_str = "MO             ;configuredMaxTxPower"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ru-|Sector.*[^,]= (ad|op).*State|isSharedWithExternalMe|prod|(main|oper).*indicator|con.*power|noOf.xAntennas|sectorFunctionRef|availableHwOutputPower|reservedBy|arfcndl|bSChannelBwDL') > -1:
            table_list = entry.split(split_str)[1].split('MO')[0]
    lte_list = split_str + "".join(table_list)
    df_conf3 = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_conf3.columns = [x.strip() for x in df_conf3.columns.to_list()]
    return df_conf3.dropna()


def get_df_conf6_nr(entries):
    split_str = "MO                                ;administrativeState;arfcnDL;bSChannelBwDL"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ru-|Sector.*[^,]= (ad|op).*State|isSharedWithExternalMe|prod|(main|oper).*indicator|con.*power|noOf.xAntennas|sectorFunctionRef|availableHwOutputPower|reservedBy|arfcndl|bSChannelBwDL') > -1:
            table_list = entry.split(split_str)[1].split('MO')[0]
    nr_list = split_str + "".join(table_list)
    df_conf6 = pd.read_csv(StringIO(nr_list.strip()),   sep=';', header=0)
    df_conf6.columns = [x.strip() for x in df_conf6.columns.to_list()]
    return df_conf6.dropna()


def get_df_conf4_lte(entries):
    split_str = "MO                         ;administrativeState;bandList"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc NRCellDU= (ad|op).*State|cell(Barred|LocalId|Range|ReservedForOperator|State)|nRCellDUId|nRPCI|nRTAC|^bandList$|^rachRootSequence$') > -1:
            table_list = entry.split(split_str)[1].split('MO')[0]
    lte_list = split_str + "".join(table_list)
    df_conf4 = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_conf4.columns = [x.strip() for x in df_conf4.columns.to_list()]
    return df_conf4.dropna()


def get_df_conf5_lte_nr(entries):
    split_str = "MO                       ;administrativeState;availableHwOutputPower"
    table_list = ""
    for entry in entries:
        if entry.find('hgetc ru-|Sector.*[^,]= (ad|op).*State|isSharedWithExternalMe|prod|(main|oper).*indicator|con.*power|noOf.xAntennas|sectorFunctionRef|availableHwOutputPower|reservedBy|arfcndl|bSChannelBwDL') > -1:
            table_list = entry.split(split_str)[1].split('MO')[0]
    lte_list = split_str + "".join(table_list)
    df_conf5 = pd.read_csv(StringIO(lte_list.strip()),   sep=';', header=0)
    df_conf5.columns = [x.strip() for x in df_conf5.columns.to_list()]
    return df_conf5.dropna()


def remove_bracket(list):
    new_l = []
    for l in list:
        new_l.append(l.split("(")[1].split(")")[0])
    return new_l


def get_vswr_table(string_data):
    regexp_rtwp = re.compile(r'RTWP')
    regexp_vswr = re.compile(r'VSWR')
    text_vswr = ""
    if string_data.find('VSWR') != -1:
        if regexp_rtwp.search(string_data):
            print(string_data.split(r'VSWR TABLE:')[1].split(r'RTWP TABLE')[0])
            text_vswr = string_data.split(r'VSWR TABLE:')[
                1].split(r'RTWP TABLE')[0]
        else:
            print(string_data.split(r'VSWR TABLE:')
                  [1].split(r'CLI PARSING')[0])
            text_vswr = string_data.split(r'VSWR TABLE:')[
                1].split(r'CLI PARSING')[0]
    return text_vswr


def get_no_vswr_table(string_data):
    regexp_1 = re.compile(r'CLI PARSING: STARTED:')
    regexp_2 = re.compile(r'LNCEL_ID')

    text_novswr = ""

    if regexp_1.search(string_data):
        print(string_data.split(r'CLI PARSING: STARTED:')[
              0].split(r'LNCEL_ID')[1].split(r'RM_EXID_CONF ')[0])
        text_novswr = string_data.split(r'CLI PARSING: STARTED:')[0].split(
            r'LNCEL_ID')[1].split(r'RM_EXID_CONF ')[0]

    return text_novswr


def get_first_table_df(textt):
    ddfn = pd.read_csv(StringIO(textt.strip()),
                       sep='|', skiprows=2, header=None)
    # dffs2 = pd.read_csv(StringIO(d.strip()), delim_whitespace=True, header=None)
    dffn = ddfn.iloc[:, 1:].dropna(thresh=3)
    dffn = dffn.iloc[:, :-1]
    # # st.sidebar.write(dffn)
    # # st.sidebar.write(len(dffn.index))
    # dffn= dffn.iloc[:,4:9]
    dffn = dffn.iloc[:, [4, 5, 7, 8]].copy()
    dffn.columns = ['Bandwidth', 'BBMOD', 'RMOD_ID', 'RMOD']
    return dffn, len(dffn.index)


def get_no_vswr_df(text_novswr):
    ddfnvswr = pd.read_csv(StringIO(text_novswr.strip()),
                           sep='|', skiprows=2, header=None)
    ddfnvswr = ddfnvswr.iloc[:, 1: -1]
    ddfnvswr = ddfnvswr.dropna(thresh=3)
    columns = [2, 7]
    ddfnn1 = pd.DataFrame(ddfnvswr, columns=columns)
    ddfnn1.columns = ['CELL', 'LNCEL_ID']
    ddfnn1['LNCEL_ID'] = ddfnn1['LNCEL_ID'].astype(int)
    lncel_list = list(ddfnn1['LNCEL_ID'].astype(int))
    lnid_list = [f"LNCEL-{str(x)}" for x in lncel_list if not str(x) == "nan"]
    print(lnid_list)
    ddfnn1['LNCEL_ID'] = lnid_list
    ddfnn1['VSWR_BRANCH_1'] = np.nan
    ddfnn1['VSWR_BRANCH_2'] = np.nan
    ddfnn1['VSWR_BRANCH_3'] = np.nan
    ddfnn1['VSWR_BRANCH_4'] = np.nan
    return ddfnn1


def get_vswr_df(textv):
    ddfnv = pd.read_csv(StringIO(textv.strip()),   sep='|', header=1)
    # dffs2 = pd.read_csv(StringIO(d.strip()), delim_whitespace=True, header=None)
    ddfnv = ddfnv.iloc[:, 1:].dropna(thresh=3)
    ddfnv = ddfnv.iloc[:, :-1]
    print(ddfnv.shape)
    ddfnv.head(50)
    print(ddfnv.columns)
    ddfnv.columns = ddfnv.columns.str.strip()
    cxlist = ddfnv['LNCEL'].unique().tolist()
    print(cxlist)
    cleancxlist = [x for x in cxlist if str(x) != 'LNCEL']
    # print(f"cleancxlist..{cleancxlist}")
    grouped = ddfnv.groupby('LNCEL')
    vswr_branch_1 = []
    vswr_branch_2 = []
    vswr_branch_3 = []
    vswr_branch_4 = []
    lncel_list = []
    cell_list = []
    for i in cleancxlist:
        dff = grouped.get_group(i)
        print(f"dff is..{dff}")
        print(dff.columns)
        print(f"CELL ID is..{dff['LNCEL']}")
        vswr_list = dff['VSWR'].to_list()
        lncell_list = dff['LNCELID'].to_list()
        celll_list = dff['LNCEL'].to_list()
        print(f"vswr list is..{vswr_list}")
        print(f"lncl list is..{lncell_list}")
        print(f"celll_list is.. {celll_list}")
        vswr_branch_1.append(vswr_list[0])
        vswr_branch_2.append(vswr_list[1])
        if len(vswr_list) > 2:
            vswr_branch_3.append(vswr_list[2])
            vswr_branch_4.append(vswr_list[3])
        else:
            vswr_branch_3.append(0)
            vswr_branch_4.append(0)

        lncel_list.append(lncell_list[0])
        cell_list.append(celll_list[0])

    print(f"vswr_branch_1 is.. {vswr_branch_1}")
    print(f"vswr_branch_2 is.. {vswr_branch_2}")
    print(f"vswr_branch_3 is.. {vswr_branch_3}")
    print(f"vswr_branch_4 is.. {vswr_branch_4}")
    print(f"lncel_list is.. {lncel_list}")
    print(f"cell_list is.. {cell_list}")

    data = {'CELL': cell_list, 'LNCEL_ID': lncel_list,   'VSWR_BRANCH_1': vswr_branch_1,
            'VSWR_BRANCH_2': vswr_branch_2, 'VSWR_BRANCH_3': vswr_branch_3, 'VSWR_BRANCH_4': vswr_branch_4}
    df_vswr = pd.DataFrame(data)
    # # st.sidebar.write(df_vswr)
    return df_vswr


def get_rssi_table1(string_data):

    regexp_v1 = re.compile(r'CLI PARSING: COMPLETED:')
    regexp_v2 = re.compile(r'CLI PARSING: STARTED:')
    if regexp_v1.search(string_data):
        print(string_data.split(r'CLI PARSING: COMPLETED:')[
            1].split(r'RSSI_ANT_1')[1].split(r'DL_Vol(MBs)')[0])
        textr1 = string_data.split(r'CLI PARSING: COMPLETED:')[1].split(
            r'RSSI_ANT_1')[1].split(r'DL_Vol(MBs)')[0]
    elif regexp_v2.search(string_data):
        print(string_data.split(r'CLI PARSING: STARTED:')[
            1].split(r'RSSI_ANT_1')[1].split(r'DL_Vol(MBs)')[0])
        textr1 = string_data.split(r'CLI PARSING: STARTED:')[1].split(
            r'RSSI_ANT_1')[1].split(r'DL_Vol(MBs)')[0]
    return textr1


def get_rssi_table2(string_data):

    regexp_v1 = re.compile(r'CLI PARSING: COMPLETED:')
    regexp_v2 = re.compile(r'CLI PARSING: STARTED:')
    if regexp_v1.search(string_data):
        print(string_data.split(r'CLI PARSING: COMPLETED:')[
            1].split(r'RSSI_ANT_1')[2])
        textr2 = string_data.split(r'CLI PARSING: COMPLETED:')[
            1].split(r'RSSI_ANT_1')[2]
    elif regexp_v2.search(string_data):
        print(string_data.split(r'CLI PARSING: STARTED:')[
            1].split(r'RSSI_ANT_1')[2])
        textr2 = string_data.split(r'CLI PARSING: STARTED:')[
            1].split(r'RSSI_ANT_1')[2]
    return textr2


def get_rrsi_df1(textr):
    ddf_nrr = pd.read_csv(StringIO(textr.strip()),
                          sep='|', skiprows=2,  header=None)
    # dffs2 = pd.read_csv(StringIO(d.strip()), delim_whitespace=True, header=None)
    ddf_nrr = ddf_nrr.iloc[:, 1:].dropna(thresh=3)
    ddf_nrr = ddf_nrr.iloc[: -1, :-5]
    for i in range(5, 9):
        ddf_nrr.iloc[:, i] = pd.to_numeric(
            ddf_nrr.iloc[:, i], errors='coerce').fillna(0).astype('float')
    ddf_nrr = ddf_nrr.iloc[:, 4:]
    return ddf_nrr


rssi_time = ""
rssi_date = ""


def get_combined_rssi_df(textr2, ddf_nrr):
    ddfnr1 = pd.read_csv(StringIO(textr2.strip()),
                         sep='|', skiprows=2,  header=None)
    # dffs2 = pd.read_csv(StringIO(d.strip()), delim_whitespace=True, header=None)
    ddfnr1 = ddfnr1.iloc[:, 1:].dropna(thresh=3)
    ddfnr1 = ddfnr1.iloc[:, :-5]
    for i in range(5, 9):
        ddfnr1.iloc[:, i] = pd.to_numeric(
            ddfnr1.iloc[:, i], errors='coerce').fillna(0).astype('float')
    print(ddfnr1.shape)
    rssi_time = ddfnr1.iloc[0, 1]
    # # st.sidebar.write(f"time is ..{rssi_time}")
    rssi_date = ddfnr1.iloc[0, 0]
    # # st.sidebar.write(f"Date is ..{rssi_date}")
    ddfnr1 = ddfnr1.iloc[:, 4:]
    # ddfnr1

    deff = pd.concat([ddfnr1, ddf_nrr])
    # # st.sidebar.write(deff)
    deff = deff.replace(0, np.NaN)
    # # st.sidebar.write(deff)

    # deff
    print(f"{deff.columns.tolist()}")

    # ddfnr1.combine(ddf_nrr, np.sum)
    # ddf_comb = pd.concat([ddfnr1, ddf_nrr]).groupby(ddf_comb.columns.tolist()[:5]).mean()
    # df = pd.concat([df1, df2]).groupby(df.columns.tolist()[1:4]).mean()
    # print(deff.loc['5'])
    deff.columns = ['CELL', 'RSSI_BRANCH_1',
                    'RSSI_BRANCH_2', 'RSSI_BRANCH_3', 'RSSI_BRANCH_4']
    # deff['CELL'] = deff['CELL1']
    deff = deff.groupby('CELL').mean()
    deff.reset_index(inplace=True)
    deff = deff.rename(columns={'index': 'CELL'})
    # deff['DiversityImbalance'] = (deff.max(axis=1) - deff.min(axis=1))
    Row_list = []
    # Iterate over each row
    for index, rows in deff.iterrows():
        # Create list for the current row
        my_list = [rows.RSSI_BRANCH_1, rows.RSSI_BRANCH_2,
                   rows.RSSI_BRANCH_3, rows.RSSI_BRANCH_4]
    #     my_list = np.min(my_list[np.nonzero(my_list)])
        # # st.sidebar.write(deff.columns)
        my_list = [i for i in my_list if i != 0]
        if not my_list:
            diff_my_list = np.nan
        else:
            print(f"my_list,, {my_list}")
            diff_my_list = np.around(min(my_list) - max(my_list), 2)
            print(f"diff is ..{diff_my_list}")
            # append the list to the final list
        Row_list.append(diff_my_list)
    # Print the list
    print(Row_list)

    deff['DiversityImbalance'] = Row_list
    print(deff.columns)
    print(f"max ")
    return deff, rssi_date, rssi_time


def rssi_na(ddfnr):
    rssi_list_4 = []
    rssi_list_3 = []
    rssi_list_2 = []
    rssi_list_1 = []
    for index, rows in ddfnr.iterrows():
        # # st.sidebar.write(rows.Bandwidth)
        if not rows.Bandwidth.__contains__("MHz"):
            rssi_list_4.append(np.nan)
            rssi_list_3.append(np.nan)
            rssi_list_2.append(np.nan)
            rssi_list_1.append(np.nan)
        else:
            rssi_list_4.append(rows.RSSI_BRANCH_4)
            rssi_list_3.append(rows.RSSI_BRANCH_3)
            rssi_list_2.append(rows.RSSI_BRANCH_2)
            rssi_list_1.append(rows.RSSI_BRANCH_1)
        # # st.sidebar.write(rssi_list_4)
    rssi_list_4 = [np.nan if x == 0 else x for x in rssi_list_4]
    rssi_list_3 = [np.nan if x == 0 else x for x in rssi_list_3]
    rssi_list_2 = [np.nan if x == 0 else x for x in rssi_list_2]
    rssi_list_1 = [np.nan if x == 0 else x for x in rssi_list_1]
    ddfnr["RSSI_BRANCH_4"] = rssi_list_4
    ddfnr["RSSI_BRANCH_3"] = rssi_list_3
    ddfnr["RSSI_BRANCH_2"] = rssi_list_2
    ddfnr["RSSI_BRANCH_1"] = rssi_list_1
    # st.sidebar.table(ddfnr)

    return ddfnr


def get_final_df(deff, dffn, df_vswr):
    ddfnr = deff.join(dffn)
    ddfnr = ddfnr.merge(df_vswr, on='CELL', how='inner')
    print(ddfnr.columns)
    ddfnr = ddfnr.reindex(columns=['CELL', 'LNCEL_ID',  'BBMOD', 'Bandwidth', 'RMOD', 'RMOD_ID',  'RSSI_BRANCH_1', 'RSSI_BRANCH_2', 'RSSI_BRANCH_3',
                                   'RSSI_BRANCH_4',  'DiversityImbalance', 'VSWR_BRANCH_1', 'VSWR_BRANCH_2', 'VSWR_BRANCH_3',
                                   'VSWR_BRANCH_4'])
    print(ddfnr.shape)
    # df_style = ddfnr.style.hide_index()
    # deff['DiversityImbalance'] = (deff.max(axis=1) - deff.min(axis=1))
    ddfnr = ddfnr[ddfnr["CELL"].str.contains("_I") == False]
    ddfnr['DiversityImbalance'].round(decimals=2)
    # ~df.C.str.contains("XYZ")
    return rssi_na(ddfnr)


def get_rssi_bandwidth(deff):
    Five_list = []
    Ten_list = []
    Fifteen_list = []
    Twenty_list = []
    Nan_list = []
    for index, rows in deff.iterrows():
        # Create list for the current row
        my_list = rows.Bandwidth
        #     my_list = np.min(my_list[np.nonzero(my_list)])
        # # st.sidebar.write(f"my_list is.. {my_list}")
        # min = a if a < b else b
        five_my_list = index if str(
            my_list).__contains__('5') else 1000
        ten_my_list = index if str(
            my_list).__contains__('10') else 1000
        fifteen_my_list = index if str(
            my_list).__contains__('15') else 1000
        twenty_my_list = index if str(
            my_list).__contains__('20') else 1000
        nan_my_list = index if not str(
            my_list).__contains__('MHz') else 1000

        # append the list to the final list
        Five_list.append(five_my_list)
        Ten_list.append(ten_my_list)
        Fifteen_list.append(fifteen_my_list)
        Twenty_list.append(twenty_my_list)
        Nan_list.append(nan_my_list)
        # # st.sidebar.write(f"5MHz list is ..{Five_list}")
        # # st.sidebar.write(f"10MHz list is ..{Ten_list}")
        # # st.sidebar.write(f"NaN list is ..{Nan_list}")

    # Five_listt = list(filter((np.NaN).__ne__, Five_list))
    # res = [i for i in test_list if i]
    Five_listt = [i for i in Five_list if i != 1000]
    Ten_listt = [i for i in Ten_list if i != 1000]
    Fifteen_listt = [i for i in Fifteen_list if i != 1000]
    Twenty_listt = [i for i in Twenty_list if i != 1000]
    Nan_listt = [i for i in Nan_list if i != 1000]
    return Five_listt, Ten_listt, Fifteen_listt, Twenty_listt, Nan_listt


def bg_color_di(v):
    if (v < -2.99):
        return "red"
    else:
        return "lightgreen"


def bg_color_vswr(v):
    if (v > 1.49):
        return "red"
    else:
        return "#75c609"


def bg_color_AtoF(v):
    return "#79cbf7"


rssi_dict = {'Five': (-110, -98), 'Ten': (-107, -95),
             'Fifteen': (-105.2, -93.2), 'Twenty': (-104, -92)}


def bg_color_five(v):
    if (v < rssi_dict['Five'][0] and v > rssi_dict['Five'][1]):
        return "red"
    else:
        return "lightgreen"


def bg_color_ten(v):
    if (v < int(rssi_dict['Ten'][0]) or v > int(rssi_dict['Ten'][1])):
        return "#f98136"  # "#ef15e4"
    else:
        return "lightgreen"


def bg_color_fifteen(v):
    if (v < int(rssi_dict['Fifteen'][0]) or v > int(rssi_dict['Fifteen'][1])):
        return "red"
    else:
        return "lightgreen"


def bg_color_twenty(v):
    if (v < int(rssi_dict['Twenty'][0]) or v > int(rssi_dict['Twenty'][1])):
        return "red"
    else:
        return "lightgreen"


def bg_color_nan(v):
    return "yellow"


def app():
    with st.container():

        st.header('Process AT&T Log Files')
        st.markdown('Please upload  **only log files**.')
        hide_st_style = """
            <style>
            # MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
        st.markdown(hide_st_style, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose a file", key="att")

        # def form_callback():
        #     # st.sidebar.write(st.session_state.my_slider)
        #     # st.sidebar.write(st.session_state.my_checkbox)

        if uploaded_file is not None:

            uploadedfn = uploaded_file.name
            node_name = uploadedfn.split('.')[0].lstrip().rstrip()
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()
            # st.write(bytes_data)

            # To convert to a string based() IO:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            # st.write(stringio)

            # To read file as string:
            string_data = stringio.read()
            # st.write(string_data)

            # st.table(first_table_df)
            # # st.sidebar.write(string_data)

            df_pre_cell = get_pre_cell_df(string_data, node_name)
            st.write('Pre Cell State LTE')
            st.table(df_pre_cell)

            df_pre_cell_nr = get_pre_cell_df_nr(string_data, node_name)
            st.write('Pre Cell State NR')
            st.table(df_pre_cell_nr)

            df_configuration = get_mmbb_configuration_df(
                string_data, node_name)
            st.write('Cell Configuration')
            st.table(df_configuration)
            df_car = get_lte_car_df(string_data, node_name)
            # st.write('LTE CAR')
            # st.table(df_car)

            df_cs = get_cell_state_df_lte(string_data, node_name)
            st.write('MMBB:CELL_STATE LTE')
            st.table(df_cs)

            nr_cs = get_cell_state_df_nr(string_data, node_name)
            st.write('MMBB:CELL_STATE NR')
            st.table(nr_cs)

            df_inv = get_mmbb_invx_cell_df(string_data, node_name)
            st.write('MMBB:INVX CELL')
            st.table(df_inv)

            df_ltraf = get_mmbb_lte_traffic(string_data, node_name)
            st.write('MMBB:LTE TRAFFIC')
            st.table(df_ltraf)

            df_al = get_mmbb_ext_alarm(string_data, node_name)
            st.write('MMBB:EXTERNAL ALARM PORT')
            st.table(df_al)

            # df_sdi = get_mmbb_sdi(string_data, node_name)
            # st.write('MMBB:SDI')
            # st.table(df_sdi)

            df_asm = get_asm_df(string_data, node_name)
            st.write('ASM')
            st.table(df_asm)

            df_invx_prod = get_inv_prod_df(string_data, node_name)
            st.write('MMBB:INVX PROD LTE')
            st.table(df_invx_prod)

            df_attn = get_attn_df(string_data, node_name)
            st.write('MMBB:ATTN')
            st.table(df_attn)

            df_ru = get_mmbb_ru_df(string_data, node_name)
            st.write('MMBB:RU')
            st.table(df_ru)

            df_rsu = get_mmbb_rsu(string_data, node_name)
            st.write('MMBB:RSU')
            st.table(df_rsu)

            df_post_cell = get_post_cell_df(string_data, node_name)
            st.write('Post Cell State LTE')
            st.table(df_post_cell)

            df_post_cell_nr = get_post_cell_df_nr(string_data, node_name)
            st.write('Post Cell State NR')
            st.table(df_post_cell_nr)

            st.markdown("""
            <style>
            table td:nth-child(1) {
                display: none
            }
            table th:nth-child(1) {
                display: none
            }
            </style>
            """, unsafe_allow_html=True)

            # df_final.apply(lambda x: [
            # "N/A" for v in x],  subset=(twenty_list, ["RSSI_BRANCH_1", "RSSI_BRANCH_2", "RSSI_BRANCH_3", "RSSI_BRANCH_4"]))
            # # st.sidebar.write(df_final)

            def get_col_widths(dataframe):
                # First we find the maximum length of the index column
                idx_max = max(
                    [len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
                # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
                return_list = [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [
                    len(col)]) for col in dataframe.columns]
                # # st.sidebar.write(return_list)
                return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [
                    len(col)]) for col in dataframe.columns]

            def to_excel(df_with_style, df_original, df_vswr=None, df2=None):
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                df_with_style = df_with_style.set_properties(
                    **{'text-align': 'left'})
                df_with_style.to_excel(
                    writer, index=False, na_rep='N/A', startrow=2)

                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                header_format = workbook.add_format({'bg_color': 'yellow'})
                header_format.set_align('left')
                header_format.set_text_wrap()

                text_format = workbook.add_format()
                text_format.set_bold()
                text_format.set_italic()
                text_format.set_font_size(11)
                text_format.set_font_color('navy')

                footer_format = workbook.add_format({'bg_color': '#ffd54f'})
                header_bottom_format = workbook.add_format(
                    {'bg_color': '#ffd54f', 'border': 1})
                header_top_format = workbook.add_format(
                    {'bottom': 0, 'top': 1, 'left': 0, 'right': 0})
                header_top_end_format = workbook.add_format(
                    {'bottom': 0, 'top': 1, 'left': 0, 'right': 1})
                di_format = workbook.add_format({'num_format': '#,##0.00'})
                atof_format = workbook.add_format({'bg_color': '#8fc1f7'})
                # footer_format.set_bg_color('skyblue')
                # footer_format.set_bold()
                footer_format.set_font_size(11)
                # Write the column headers with the defined format.
                for col_num, value in enumerate(df_original.columns.values):
                    worksheet.write(2, col_num, value, header_format)
                # Set the default height of all the rows, efficiently.
                worksheet.set_default_row(16)
                # Set the height of Row len(df_original)+2 to 20.
                # worksheet.set_row(len(df_original)+2, 20)
                # worksheet.set_row(len(df_original)+3, 20)
                # worksheet.set_row(len(df_original)+4, 20)
                # worksheet.set_row(len(df_original)+5, 20)

                col_width_list = get_col_widths(df_original)
                col_width_list[0] = 17  # Cell
                col_width_list[6] = 10  # RSSI_BRANCH_1
                col_width_list[7] = 10  # RSSI_BRANCH_2
                col_width_list[8] = 10  # RSSI_BRANCH_3
                col_width_list[9] = 10  # RSSI_BRANCH_4
                col_width_list[10] = 17  # DiversityImbalance
                col_width_list[11] = 10  # VSWR_BRANCH_1
                col_width_list[12] = 10  # VSWR_BRANCH_2
                col_width_list[13] = 10  # VSWR_BRANCH_3
                col_width_list[14] = 10  # VSWR_BRANCH_4

                for i, width in enumerate(col_width_list):
                    worksheet.set_column(i, i, width)
                worksheet.set_row(1, 16)  # Set the height of Row 1 to 30.
                # worksheet.set_column('A:A', None, format1)
                border_fmt = workbook.add_format(
                    {'bottom': 1, 'top': 1, 'left': 1, 'right': 1})
                border_top_fmt = workbook.add_format(
                    {'bottom': 0, 'top': 1, 'left': 1, 'right': 1})
                border_bottom_fmt = workbook.add_format(
                    {'bottom': 1, 'top': 0, 'left': 1, 'right': 1})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    2, 10, len(df_original)+2, 10), {'type': 'no_errors', 'format': di_format})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    3, 0, len(df_original)+2, len(df_original.columns) - 1), {'type': 'no_errors', 'format': border_fmt})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    3, 0, len(df_original)+2, 5), {'type': 'no_errors', 'format': atof_format})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    1, 0, 1, 14), {'type': 'no_errors', 'format': header_format})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    1, 0, 1, 5), {'type': 'no_errors', 'format': border_top_fmt})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    2, 6, 2, 9), {'type': 'no_errors', 'format': header_bottom_format})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    1, 6, 1, 9), {'type': 'no_errors', 'format': header_top_format})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    2, 11, 2, 14), {'type': 'no_errors', 'format': header_bottom_format})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    1, 11, 1, 14), {'type': 'no_errors', 'format': header_top_format})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    1, 10, 1, 10), {'type': 'no_errors', 'format': border_top_fmt})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    2, 10, 2, 10), {'type': 'no_errors', 'format': border_bottom_fmt})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    2, 0, 2, 5), {'type': 'no_errors', 'format': border_bottom_fmt})
                # <<< Then you can write to a different row
                worksheet.write(
                    1, 7, "RSSI"
                )
                worksheet.write(
                    1, 12, "Return Loss/VSWR"
                )
                worksheet.write(
                    1, 14, "", header_top_end_format
                )

                worksheet.write(
                    2, 6, "Branch 1"
                )
                worksheet.write(
                    2, 7, "Branch 2"
                )
                worksheet.write(
                    2, 8, "Branch 3"
                )
                worksheet.write(
                    2, 9, "Branch 4"
                )
                worksheet.write(
                    2, 11, "Branch 1"
                )
                worksheet.write(
                    2, 12, "Branch 2"
                )
                worksheet.write(
                    2, 13, "Branch 3"
                )
                worksheet.write(
                    2, 14, "Branch 4"
                )
                worksheet.write(
                    0, 0, f"Measured Time:    {rssi_date} {rssi_time}",  text_format)
                worksheet.write(
                    len(df_original)+3, 0, "Target Thresholds", footer_format
                )
                worksheet.write(
                    len(df_original)+3, 1, "", footer_format
                )
                worksheet.write(
                    len(df_original)+3, 6, "-110>5MHz<-98", footer_format
                )
                worksheet.write(
                    len(df_original)+3, 7, "", footer_format
                )
                worksheet.write(
                    len(df_original)+4, 6, "-107>10Mhz<-95", footer_format
                )
                worksheet.write(
                    len(df_original)+4, 7, "", footer_format
                )
                worksheet.write(
                    len(df_original)+5, 6, "-105.2>15Mhz<-93.2", footer_format
                )
                worksheet.write(
                    len(df_original)+5, 7, "", footer_format
                )
                worksheet.write(
                    len(df_original)+6, 6, "-104>20Mhz<-92", footer_format
                )
                worksheet.write(
                    len(df_original)+6, 7, "", footer_format
                )
                worksheet.write(
                    len(df_original)+3, 10, "<3.0", footer_format
                )
                worksheet.write(
                    len(df_original)+3, 12, "<1.5", footer_format
                )

                writer.save()
                processed_data = output.getvalue()
                return processed_data
            # df_xlsx = to_excel(df_with_style, df_final)
            # st.download_button(label='📥 Download As Excel',
            #                    data=df_final,
            #                    file_name=f'AT&T_{node_name}_Output_summary.xlsx')


app()
