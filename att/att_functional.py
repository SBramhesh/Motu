import re
from bs4 import BeautifulSoup
import copy
import xml_templates
import streamlit as st
import xlsxwriter
import pandas as pd
from functools import reduce
import xml.dom.minidom
import functools

# st.set_page_config(
#     page_title="AT&T Scripting",
#     page_icon="🧊",
#     layout="wide",
#     initial_sidebar_state="expanded",
#     menu_items={
#         'Get Help': 'https://www.integertel.com',
#     }
# )
# xml_dict = xml_templates.return_dict()

# mapping of decalrative rules'''
nrcell_par_dict = {
    'cellName': 'cellName',
    'gscn': 'gscn',
    'dlMimoMode': 'dlMimoMode',
    'msg1FrequencyStart': 'Msg1FrequencyStart',
    'pMax': 'pMax',
    'prachConfigurationIndex': 'prachConfigurationIndex',
    'prachRootSequenceIndex': 'prachRootSequenceIndex',
    'zeroCorrelationZoneConfig': 'zeroCorrelationZoneConfig',
    'configuredEpsTac': 'configuredEpsTac',
    'type0CoresetConfigurationIndex': 'type0CoresetConfigurationIndex',
    'physCellId': 'physCellId',
    'nrarfcnDl': 'nrarfcnDl',
    'nrarfcnUl': 'nrarfcnUl',
    'nrarfcn': 'nrarfcn',
    'fiveGsTac': 'fiveGsTac',
    'trackingAreaDN': 'fiveGsTac',
    'dlCarrierFreq': 'dlCarrierFreq',
    'ssbFrequency': 'ssbFrequency',
    'redirFreqEutra': 'redirFreqEutra'
}

key_list = [key for key in nrcell_par_dict]

filter_dict = {
    'nrarfcnUl': 'fdd_replace',
    'nrarfcn': 'fdd_replace',
}

filter_key_list = [key for key in filter_dict]


def fdd_replace(parName, soup=None, mf_dict=None):
    mf_tags = soup.find_all(
        attrs={"name": str(parName).rstrip().lstrip()})
    for mf_tag in mf_tags:
        cell_value = re.findall(
            r'NRCELL-[0-9]+', mf_tag.parent['distName'])[-1].split('-')[1]
        mf_val = mf_dict.get(int(cell_value))
        print(
            f"the  mf value is.. {str(mf_val).lstrip().rstrip()}")
        print(f"text is..{mf_tag.text}")
        mf_tag.string = str(mf_val).lstrip().rstrip()
    return parName, copy.copy(soup),


def enb_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "enbName"})
    for mf_tag in mf_tags:
        mf_tag.string = get_ciq_value(
            "enbName", st.session_state['ciq_sitemain_par'])
    return soup


def bts_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "btsName"})
    for mf_tag in mf_tags:
        mf_tag.string = get_ciq_value(
            "enbName", st.session_state['ciq_sitemain_par'])
    return soup


def userLabel_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "userLabel"})
    for mf_tag in mf_tags:
        mf_tag.string = get_ciq_value(
            "enbName", st.session_state['ciq_sitemain_par'])
    return soup


def utraCarrierFreq_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "utraCarrierFreq"})
    for mf_tag in mf_tags:
        mf_tag.string = str(get_ciq_value(
            "dlCarFrqUtra", st.session_state['ciq_cell_par']))
    return soup


def adjGnbId_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "adjGnbId"})
    for mf_tag in mf_tags:
        mf_tag.string = str(get_ciq_value(
            "mrbtsId", st.session_state['ciq_sitemain_par']))
    return soup


def gatewayIpv6Addr_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "gatewayIpv6Addr"})
    for i in [0, 1, 2, 4]:
        mf_tags[i].string = str(get_ciq_value(
            "IPV6_SIAD_OAM_IP_DEF_ROUTER", st.session_state['edp_raptor']))
    mf_tags[3].string = str(get_ciq_value(
        "IPV6_SIAD_BEARER_IP_DEF_ROUTER", st.session_state['edp_raptor']))
    return soup


def first_localIpAddr_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "localIpAddr"})
    mf_tags[0].string = str(get_ciq_value(
        "IPV6_ENODEB_OAM_IP", st.session_state['edp_raptor']))
    return soup


def cPlaneIpAddr_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "cPlaneIpAddr"})
    for mf_tag in mf_tags:
        mf_tag.string = str(get_ciq_value(
            "IPV6_ENODEB_BEARER_IP", st.session_state['edp_raptor']))
    return soup


def second_localIpAddr_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "localIpAddr"})
    mf_tags[1].string = str(get_ciq_value(
        "IPV6_ENODEB_BEARER_IP", st.session_state['edp_raptor']))
    return soup


def first_vlan_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "vlanId"})
    mf_tags[0].string = str(get_ciq_value(
        "oam_enodeb_siad_oam_vlan", st.session_state['edp_raptor']))
    return soup


def second_vlan_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "vlanId"})
    mf_tags[1].string = str(get_ciq_value(
        "bearer_enodeb_sb_vlan_id", st.session_state['edp_raptor']))
    return soup


def endEarfcnDl_replace_first_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "endEarfcnDl"})
    ear_ciq = str(get_ear_value(
        st.session_state['ciq_cell_par']))
    if len(mf_tags) > 0 and ear_ciq != 'nan':
        mf_tags[0].string = ear_ciq
        # else delete the <item>
    return soup


def endEarfcnDl_replace_second_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "endEarfcnDl"})
    ear_ciq = str(get_port_value(
        st.session_state['ciq_cell_par']))
    if len(mf_tags) > 0 and ear_ciq != 'nan':
        mf_tags[1].string = ear_ciq
        # else delete the <item>
    return soup


def startEarfcnDl_replace_second_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "startEarfcnDl"})
    ear_ciq = str(get_port_value(
        st.session_state['ciq_cell_par']))
    if len(mf_tags) > 0 and ear_ciq != 'nan':
        mf_tags[1].string = ear_ciq
        # else delete the <item>
    return soup


def startEarfcnDl_replace_first_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "startEarfcnDl"})
    ear_ciq = str(get_ear_value(
        st.session_state['ciq_cell_par']))
    if len(mf_tags) > 0 and ear_ciq != 'nan':
        mf_tags[0].string = ear_ciq
        # else delete the <item>
    return soup


def freqLayListDedLteLB_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "freqLayListDedLteLB"})
    ear_ciq_list = str(get_freqLayListDedLteLB_value(
        st.session_state['ciq_cell_par']))
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_p_tags(modpr_soup, "freqLayListDedLteLB")
        for freq in ear_ciq_list:
            modpr_soup = add_p_tags(modpr_soup, freq, "freqLayListDedLteLB")
    return modpr_soup


def freqLayListDedLteLB_mopr_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "freqLayListDedLteLB"})
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_p_tags(modpr_soup, "freqLayListDedLteLB")
    for mf_tag in mf_tags:
        parent_mo = str(mf_tag.find_parent(
            "managedObject")['class']).split('/')[-1]
        ear_ciq_list = str(get_freqLayListDedLteLB_value(
            st.session_state['ciq_cell_par'], parent_mo))
        if len(mf_tag) > 0 and ear_ciq_list != 'nan':
            for freq in ear_ciq_list:
                new_tag = modpr_soup.new_tag("p")
                mf_tag.append(new_tag)
                new_tag.string = str(freq)
    return modpr_soup


def dlCarFrqEutL_mopr_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "dlCarFrqEutL"})
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_dlCarFrqEutL_item_tags(modpr_soup)
    for mf_tag in mf_tags:
        parent_mo = str(mf_tag.find_parent(
            "managedObject")['class'])
        ear_ciq_list = str(get_dlCarFrqEutL_value(
            st.session_state['ciq_cell_par'], parent_mo))
        if len(mf_tag) > 0 and ear_ciq_list != 'nan':
            for freq in ear_ciq_list:
                new_tag = modpr_soup.new_tag("p")
                mf_tag.append(new_tag)
                new_tag.string = str(freq)
    return modpr_soup


def redirFreqUtra_mopr_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "redirFreqUtra"})
    for mf_tag in mf_tags:
        parent_mo = str(mf_tag.find_parent(
            "managedObject")['class'])
        ear_ciq_list = str(get_redirFreqUtra_value(
            st.session_state['ciq_cell_par'], parent_mo))
        if len(mf_tag) > 0 and ear_ciq_list != 'nan':
            mf_tag.string = str(ear_ciq_list[-1])
    return modpr_soup


def freqLayListLte_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "freqLayListLte"})
    ear_ciq_list = get_freqLayListLte_value(
        st.session_state['ciq_cell_par'])
    ear_ciq_list = list(set(ear_ciq_list))
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_p_tags(modpr_soup, "freqLayListLte")
        for freq in ear_ciq_list:
            modpr_soup = add_p_tags(modpr_soup, freq, "freqLayListLte")
    return modpr_soup


def freqLayListLte_mopr_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "freqLayListLte"})
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_p_tags(modpr_soup, "freqLayListDedLteLB")
    for mf_tag in mf_tags:
        parent_mo = str(mf_tag.find_parent(
            "managedObject")['class']).split('/')[-1]
        ear_ciq_list = str(get_freqLayListLte_mopr_value(
            st.session_state['ciq_cell_par'], parent_mo))
        if len(mf_tag) > 0 and ear_ciq_list != 'nan':
            for freq in ear_ciq_list:
                new_tag = modpr_soup.new_tag("p")
                mf_tag.append(new_tag)
                new_tag.string = str(freq)
    return modpr_soup


def freqLayListPsHoWcdma_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "freqLayListPsHoWcdma"})
    ear_ciq_list = get_freqLayListPsHoWcdma_value(
        st.session_state['ciq_cell_par'])
    ear_ciq_list = list(set(ear_ciq_list))
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_p_tags(modpr_soup, "freqLayListPsHoWcdma")
        for freq in ear_ciq_list:
            modpr_soup = add_p_tags(modpr_soup, freq, "freqLayListPsHoWcdma")
    return modpr_soup


def freqLayListPsHoWcdma_mopr_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "freqLayListPsHoWcdma"})
    ear_ciq_list = get_freqLayListPsHoWcdma_mopr_value(
        st.session_state['ciq_cell_par'])
    ear_ciq_list = list(set(ear_ciq_list))
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_p_tags(modpr_soup, "freqLayListPsHoWcdma")
        for freq in ear_ciq_list:
            modpr_soup = add_p_tags(modpr_soup, freq, "freqLayListPsHoWcdma")
    return modpr_soup


def freqLayListEndcHo_mopr_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "freqLayListEndcHo"})
    ear_ciq_list = get_freqLayListEndcHo_mopr_value(
        st.session_state['ciq_cell_par'])
    ear_ciq_list = list(set(ear_ciq_list))
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_p_tags(modpr_soup, "freqLayListEndcHo")
        for freq in ear_ciq_list:
            modpr_soup = add_p_tags(modpr_soup, freq, "freqLayListEndcHo")
    return modpr_soup


def redirFreqUtra_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "redirFreqUtra"})
    ear_ciq_list = get_redirFreqUtra_value(
        st.session_state['ciq_cell_par'])
    ear_ciq_list = list(set(ear_ciq_list))
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        for mf_tag in mf_tags:
            mf_tag.string = str(ear_ciq_list[-1])
    return modpr_soup


def redirFreqEutra_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "redirFreqEutra"})
    ear_ciq_list = get_redirFreqEutra_value(
        st.session_state['ciq_cell_par'])
    ear_ciq_list = list(set(ear_ciq_list))
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        mf_tags[-1].string = str(ear_ciq_list[-1])
    return modpr_soup


def freqLayListSrvccWcdma_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "freqLayListSrvccWcdma"})
    ear_ciq_list = get_freqLayListPsHoWcdma_value(
        st.session_state['ciq_cell_par'])
    ear_ciq_list = list(set(ear_ciq_list))
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_p_tags(modpr_soup, "freqLayListSrvccWcdma")
        for freq in ear_ciq_list:
            modpr_soup = add_p_tags(modpr_soup, freq, "freqLayListSrvccWcdma")
    return modpr_soup


def freqLayListSrvccWcdma_mopr_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "freqLayListSrvccWcdma"})
    ear_ciq_list = get_freqLayListPsHoWcdma_mopr_value(
        st.session_state['ciq_cell_par'])
    ear_ciq_list = list(set(ear_ciq_list))
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_p_tags(modpr_soup, "freqLayListSrvccWcdma")
        for freq in ear_ciq_list:
            modpr_soup = add_p_tags(modpr_soup, freq, "freqLayListSrvccWcdma")
    return modpr_soup


def freqLayListServiceBasedHo_xducer(modpr_soup):
    mf_tags = modpr_soup.find_all(
        attrs={"name": "freqLayListServiceBasedHo"})
    ear_ciq_list = get_freqLayListServiceBasedHo_value(
        st.session_state['ciq_cell_par'])
    ear_ciq_list = list(set(ear_ciq_list))
    if len(mf_tags) > 0 and ear_ciq_list != 'nan':
        modpr_soup = delete_p_tags(modpr_soup, "freqLayListServiceBasedHo")
        for freq in ear_ciq_list:
            modpr_soup = add_p_tags(
                modpr_soup, freq, "freqLayListServiceBasedHo")
    return modpr_soup


def lcrid_transducer(soup):
    nrdcdpr_soup, lcrid_ciq = lcrid_nrdcdpr_xducer(st.session_state['NRDCDPR'])
    if lcrid_ciq != 'nan':
        cmData_tag = soup.cmData
        cmData_tag.append(nrdcdpr_soup)
    return soup


def psgrp_transducer(soup):
    psgrp_soup_list = lcrid_psgrp_xducer(st.session_state['PSGRP'])
    cmData_tag = soup.cmData
    for p_soup in psgrp_soup_list:
        cmData_tag.append(p_soup)
    return soup


def capr_transducer(soup):
    capr_soup_list = capr_xducer(st.session_state['CAPR'])
    cmData_tag = soup.cmData
    for c_soup in capr_soup_list:
        cmData_tag.append(c_soup)
    return soup


def carel_transducer(soup):
    carel_soup_list = carel_xducer(st.session_state['CAPR'])
    cmData_tag = soup.cmData
    for c_soup in carel_soup_list:
        cmData_tag.append(c_soup)
    return soup


def amlepr_transducer(soup):
    amlepr_soup_list = amlepr_xducer(st.session_state['AMLEPR'])
    cmData_tag = soup.cmData
    for c_soup in amlepr_soup_list:
        cmData_tag.append(c_soup)
    return soup


def lnhoif_transducer(soup):
    ln_soup_list = lnhoif_xducer(st.session_state['LNHOIF'])
    cmData_tag = soup.cmData
    for c_soup in ln_soup_list:
        cmData_tag.append(c_soup)
    return soup


def modpr_transducer(soup):
    processed_modpr = modpr_compose(st.session_state['MODPR'])
    cmData_tag = soup.cmData
    cmData_tag.append(processed_modpr)
    return soup


def mopr_transducer(soup):
    processed_mopr = mopr_compose(st.session_state['MOPR'])
    cmData_tag = soup.cmData
    cmData_tag.append(processed_mopr)
    return soup


def lcrid_psgrp_xducer(psgrp_soup):
    st.session_state['PSGRP'] = delete_items(psgrp_soup)
    psgrp_list = get_psgrp_value(
        st.session_state['ciq_cell_par'])
    return list(filter(lambda x: x != 'nan', psgrp_list))


def capr_xducer(capr_soup):
    capr_dict = get_capr_value(
        st.session_state['ciq_cell_par'])
    capr_band_dict = get_capr_band_value(
        st.session_state['ciq_cell_par'])
    capr_list = []
    for lcrid in capr_dict.keys():
        for earfcnDl in capr_band_dict.keys().remove(capr_dict[lcrid]):
            new_capr_soup = process_capr_soup(capr_soup, lcrid, earfcnDl)
            capr_list.append(new_capr_soup)
    return list(filter(lambda x: x != 'nan', capr_list))


def carel_xducer(carel_soup):
    carel_list = get_carel_value(
        st.session_state['ciq_cell_par'])
    carrel_list = []
    for l in carel_list:
        greek_list = return_greek_list(l[0])
        for index, _ in enumerate(greek_list):
            new_carel_soup = process_carel_soup(
                carel_soup, index, greek_list, l)
            carrel_list.append(new_carel_soup)
    return list(filter(lambda x: x != 'nan', carrel_list))


def amlepr_xducer(aml_soup):
    aml_dict = get_capr_value(
        st.session_state['ciq_cell_par'])
    aml_band_dict = get_amlepr_band_value(
        st.session_state['ciq_cell_par'])
    aml_list = []
    for lcrid in aml_dict.keys():
        for index, earfcnDl in enumerate(aml_band_dict.keys().remove(aml_dict[lcrid])):
            new_aml_soup = process_amlepr_soup(
                aml_soup, lcrid, earfcnDl, index, aml_dict[lcrid])
            aml_list.append(new_aml_soup)
    return list(filter(lambda x: x != 'nan', aml_list))


def lnhoif_xducer(lnh_soup):
    lnh_dict = get_capr_value(
        st.session_state['ciq_cell_par'])
    lnh_band_dict = get_amlepr_band_value(
        st.session_state['ciq_cell_par'])
    lnh_list = []
    for lcrid in lnh_dict.keys():
        for index, earfcnDl in enumerate(lnh_band_dict.keys().remove(lnh_dict[lcrid])):
            new_lnh_soup = process_lnhoif_soup(
                lnh_soup, lcrid, earfcnDl, index, lnh_dict[lcrid], int(lnh_band_dict[earfcnDl]))
            lnh_list.append(new_lnh_soup)
    return list(filter(lambda x: x != 'nan', lnh_list))


def return_greek_list(lcrid):
    alpha_list = [x[1] for x in st.session_state['band_cell_mapping']['alpha']]
    alpha_list = [int(i) for i in alpha_list]
    # alpha_list = list(map(int, alpha_list))
    beta_list = [i+1 for i in alpha_list]
    gamma_list = [i+2 for i in alpha_list]
    delta_list = [i+3 for i in alpha_list]
    epsilon_list = [i+4 for i in alpha_list]
    for g in [alpha_list, beta_list, gamma_list, delta_list, epsilon_list]:
        if lcrid in g:
            return g.remove(lcrid)


def process_capr_soup(kapr_soup, lcrid, earfcnDl):
    dist_string = kapr_soup.managedObject['distName']
    dist_array = dist_string.split('/')
    kapr_soup.managedObject['distName'] = '/'.join([
        dist_array[0], dist_array[1], "LNCEL-" + lcrid, "CAPR-" + earfcnDl])
    kapr_soup = process_resprio(kapr_soup, get_resprio_val(earfcnDl))
    kapr_soup = process_enableA3Event(kapr_soup, earfcnDl)
    return kapr_soup


def process_amlepr_soup(kapr_soup, lcrid, earfcnDl, index, fcnDl):
    dist_string = kapr_soup.managedObject['distName']
    dist_array = dist_string.split('/')
    kapr_soup.managedObject['distName'] = '/'.join([
        dist_array[0], dist_array[1], "LNCEL-" + lcrid, "AMLEPR-" + index])

    tgt_tags = kapr_soup.find_all(attrs={"name": "targetCarrierFreq"})
    for freq_tag in tgt_tags:
        freq_tag.string = earfcnDl
    kapr_soup = process_amlepr_cac(kapr_soup, earfcnDl, fcnDl)
    return kapr_soup


def process_lnhoif_soup(kapr_soup, lcrid, earfcnDl, index, fcnDl, dlChBw):
    dist_string = kapr_soup.managedObject['distName']
    dist_array = dist_string.split('/')
    kapr_soup.managedObject['distName'] = '/'.join([
        dist_array[0], dist_array[1], "LNCEL-" + lcrid, "LNHOIF-" + index])

    tgt_tags = kapr_soup.find_all(attrs={"name": "eutraCarrierInfo"})
    for freq_tag in tgt_tags:
        freq_tag.string = earfcnDl
    dlch_tags = kapr_soup.find_all(attrs={"name": "measurementBandwidth"})
    for dl_tag in dlch_tags:
        dl_tag.string = st.session_state['lnh_dlch'][dlChBw]
    kapr_soup = process_lnhoif_freq(kapr_soup, earfcnDl, fcnDl)
    return kapr_soup


def process_amlepr_cac(amlo_soup, earfcnDl, fcnDl):
    if is_first_net(earfcnDl):
        if is_low_band(fcnDl):
            amlo_soup = set_cac_values(
                st.session_state['amlepr']['FirstNet']['LB'])
        elif is_first_net(fcnDl):
            amlo_soup = set_cac_values(
                st.session_state['amlepr']['FirstNet']['FirstNet'])
        else:
            amlo_soup = set_cac_values(
                st.session_state['amlepr']['FirstNet']['MB/HB'])
    else:
        amlo_soup = set_cac_values(st.session_state['amlepr']['Default'])

    return amlo_soup


def process_lnhoif_freq(amlo_soup, earfcnDl, fcnDl):
    if is_first_net(earfcnDl):
        if is_low_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['FirstNet']['LB'])
        elif is_high_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['FirstNet']['HB'])
        elif is_medium_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['FirstNet']['MB'])
    elif is_low_band(earfcnDl):
        if is_low_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['LB']['LB'])
        elif is_high_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['LB']['HB'])
        elif is_medium_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['LB']['MB'])
        else:
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['LB']['FirstNet'])
    elif is_high_band(earfcnDl):
        if is_low_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['HB']['LB'])
        elif is_medium_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['HB']['MB'])
        elif is_first_net(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['HB']['FirstNet'])
    elif is_medium_band(earfcnDl):
        if is_low_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['MB']['LB'])
        elif is_high_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['MB']['HB'])
        elif is_medium_band(fcnDl):
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['MB']['MB'])
        else:
            amlo_soup = set_lnh_freq_values(
                st.session_state['lnhoif']['MB']['FirstNet'])

    else:
        amlo_soup = set_lnh_freq_values(st.session_state['lnhoif']['Default'])

    return amlo_soup


def set_cac_values(amll_soup, value_dict):
    amll_soup = set_cac_head(amll_soup, value_dict['cacHeadroom'])
    amll_soup = set_max_cac(amll_soup, value_dict['maxCacThreshold'])
    amll_soup = set_target_car(amll_soup, value_dict['targetCarrierFreq'])
    return amll_soup


def set_lnh_freq_values(amll_soup, value_dict):
    amll_soup = set_if(amll_soup, value_dict['threshold3InterFreq'])
    amll_soup = set_ifq(amll_soup, value_dict['threshold3InterFreqQci1'])
    amll_soup = set_aif(amll_soup, value_dict['threshold3aInterFreqQci1'])
    amll_soup = set_aifq(amll_soup, value_dict['threshold3aInterFreqQci1'])
    amll_soup = set_filt(amll_soup, value_dict['thresholdRsrpIFLBFilter'])
    return amll_soup


def set_if(kapr_soup, value):
    tgt_tags = kapr_soup.find_all(attrs={"name": "threshold3InterFreq"})
    for freq_tag in tgt_tags:
        freq_tag.string = value
    return kapr_soup


def set_ifq(kapr_soup, value):
    tgt_tags = kapr_soup.find_all(attrs={"name": "threshold3InterFreqQci1"})
    for freq_tag in tgt_tags:
        freq_tag.string = value
    return kapr_soup


def set_aif(kapr_soup, value):
    tgt_tags = kapr_soup.find_all(attrs={"name": "threshold3aInterFreq"})
    for freq_tag in tgt_tags:
        freq_tag.string = value
    return kapr_soup


def set_aifq(kapr_soup, value):
    tgt_tags = kapr_soup.find_all(attrs={"name": "threshold3aInterFreqQci1"})
    for freq_tag in tgt_tags:
        freq_tag.string = value
    return kapr_soup


def set_filt(kapr_soup, value):
    tgt_tags = kapr_soup.find_all(attrs={"name": "thresholdRsrpIFLBFilter"})
    for freq_tag in tgt_tags:
        freq_tag.string = value
    return kapr_soup


def set_cac_head(kapr_soup, value):
    tgt_tags = kapr_soup.find_all(attrs={"name": "cacHeadroom"})
    for freq_tag in tgt_tags:
        freq_tag.string = value
    return kapr_soup


def set_max_cac(kapr_soup, value):
    tgt_tags = kapr_soup.find_all(attrs={"name": "maxCacThreshold"})
    for freq_tag in tgt_tags:
        freq_tag.string = value
    return kapr_soup


def set_target_car(kapr_soup, value):
    tgt_tags = kapr_soup.find_all(attrs={"name": "targetCarrierFreq"})
    for freq_tag in tgt_tags:
        freq_tag.string = value
    return kapr_soup


def process_carel_soup(kapr_soup, carel_index, greek_list, carel_tuple):
    lcrid = carel_tuple[0]
    dist_string = kapr_soup.managedObject['distName']
    dist_array = dist_string.split('/')
    kapr_soup.managedObject['distName'] = '/'.join([
        dist_array[0], dist_array[1], "LNCEL-" + lcrid, "CAREL-" + carel_index])
    lnbts_tags = kapr_soup.find_all(attrs={"name": "lnBtsId"})
    for freq_tag in lnbts_tags:
        freq_tag.string = get_ciq_value(
            "mrbtsId", st.session_state['ciq_sitemain_par'])
    lcrid_tags = kapr_soup.find_all(attrs={"name": "lcrId"})
    for freq_tag in lcrid_tags:
        freq_tag.string = greek_list[carel_index]
    kapr_soup = process_mimo(kapr_soup, carel_tuple)
    return kapr_soup


def get_resprio_val(earfcnDl):
    capr_band_dict = get_capr_band_value(
        st.session_state['ciq_cell_par'])
    resprio_val = 0
    if is_medium_band(earfcnDl) == 'True':
        resprio_val = st.sesssion_state['freq_prio_medium_band'][capr_band_dict[earfcnDl]]
    if is_low_band(earfcnDl) == 'True':
        resprio_val = st.sesssion_state['freq_prio_low_band'][capr_band_dict[earfcnDl]]
    if is_high_band(earfcnDl) == 'True':
        resprio_val = st.sesssion_state['freq_prio_high_band']
    return resprio_val


def process_resprio(kapr_soup, resprio_val):
    freq_tags = kapr_soup.find_all(attrs={"name": "sFreqPrio"})
    for freq_tag in freq_tags:
        freq_tag.string = resprio_val
    return kapr_soup


def process_enableA3Event(kapr_soup, earfcnDl):
    enable_A3Event_val = len(filter_b14_list(
        [earfcnDl]) + filter_earfcnDl_list([earfcnDl]) + filter_port_list([earfcnDl])) > 0
    freq_tags = kapr_soup.find_all(attrs={"name": "enableA3Event"})
    for freq_tag in freq_tags:
        freq_tag.string = enable_A3Event_val
    return kapr_soup


def process_mimo(kapr_soup, carel_tuple):
    mimo_tags = kapr_soup.find_all(attrs={"name": "maxNumOfSuppMimoLayer"})
    for freq_tag in mimo_tags:
        freq_tag.string = st.session_state['dlMimoMode'][carel_tuple[3]]
    return kapr_soup


def delete_items(psgrp_soup):
    for i in range(len(psgrp_soup.list.find_all("item"))):
        psgrp_soup.list.item.decompose()
    return psgrp_soup


def delete_p_tags(modpr_soup, freq_type):
    freq_tags = modpr_soup.find_all(attrs={"name": freq_type})
    for freq_tag in freq_tags:
        for i in range(len(freq_tag.find_all("p"))):
            modpr_soup.find(attrs={"name": freq_type}).p.decompose()
    return modpr_soup


def delete_dlCarFrqEutL_item_tags(modpr_soup, parentmo=None):
    freq_tags = modpr_soup.find_all(attrs={"name": "dlCarFrqEutL"})
    for freq_tag in freq_tags:
        parent_mo = str(freq_tag.find_parent(
            "managedObject")['class'])
        for i in range(len(freq_tag.find_all("item"))):
            modpr_soup.find(attrs={"name": "dlCarFrqEutL"}).item.decompose()
    return modpr_soup


def add_dlCarFrqEutL_item_tags(modpr_soup, parentmo=None):
    freq_tags = modpr_soup.find_all(attrs={"name": "dlCarFrqEutL"})
    for freq in freq_tags:
        new_tag = modpr_soup.new_tag("p")
        freq.append(new_tag)
        new_tag.string = str(freq)
    return modpr_soup


def add_p_tags(modpr_soup, text, freq_type, parent_mo=None):
    freq_tags = modpr_soup.find_all(attrs={"name": freq_type})
    for freq_tag in freq_tags:
        original_tag = freq_tag
        new_tag = modpr_soup.new_tag("p")
        original_tag.append(new_tag)
        new_tag.string = str(text)
    return modpr_soup


def add_p_tags_mopr(modpr_soup, freq_tag, text):
    original_tag = freq_tag
    new_tag = modpr_soup.new_tag("p")
    original_tag.append(new_tag)
    new_tag.string = str(text)
    return modpr_soup


def lcrid_nrdcdpr_xducer(nrdcdpr_soup):
    mf_tags = nrdcdpr_soup.find_all(
        attrs={"name": "lcrId"})
    lcrid_ciq = str(get_lcrid_value(
        st.session_state['ciq_cell_par']))
    if len(mf_tags) > 0 and lcrid_ciq != 'nan':
        for mf_tag in mf_tags:
            if not (str(mf_tag.text) in lcrid_ciq):
                # delete the enclosing <item>
                item_tag = mf_tag.find_parent("item")
                item_tag.decompose()
    return nrdcdpr_soup, lcrid_ciq


def eutraCarrierFreq_b66_mfbipr(mfbirp_soup):
    mf_tags = mfbirp_soup.find_all(
        attrs={"name": "eutraCarrierFreq"})
    eutra_ciq = str(get_eutra_value_66(
        st.session_state['ciq_cell_par']))
    if len(mf_tags) > 0 and eutra_ciq != 'nan':
        mf_tags[0].string = eutra_ciq
    return mfbirp_soup, eutra_ciq


def eutraCarrierFreq_b12_mfbipr(mfbirp_soup):
    mf_tags = mfbirp_soup.find_all(
        attrs={"name": "eutraCarrierFreq"})
    eutra_ciq = str(get_eutra_value_12(
        st.session_state['ciq_cell_par']))
    if len(mf_tags) > 0 and eutra_ciq != 'nan':
        mf_tags[0].string = eutra_ciq
    return mfbirp_soup, eutra_ciq


def eutraCarrierFreq_b66_append_transducer(soup):
    mfbipr_soup, eutra_ciq = eutraCarrierFreq_b66_mfbipr(
        st.session_state['mfbipr_66'])
    if eutra_ciq != 'nan':
        cmData_tag = soup.cmData
        cmData_tag.append(mfbipr_soup)
    return soup


def eutraCarrierFreq_b12_append_transducer(soup):
    mfbipr_soup, eutra_ciq = eutraCarrierFreq_b12_mfbipr(
        st.session_state['mfbipr_12'])
    if eutra_ciq != 'nan':
        cmData_tag = soup.cmData
        cmData_tag.append(mfbipr_soup)
    return soup


# pure function transducer replacing all pattern instances'''

def replace_transducer(soup, pattern,  replace_value=None, num_digits=None):
    new_soup = re.sub(f'{pattern}'r'-(\d{'f'{int(num_digits)}'r',})',
                      f'{pattern}-{int(replace_value)}', str(soup))
    soup_1 = BeautifulSoup(new_soup, "xml")
    soup_1 = str(soup_1).replace('\n', '')
    return soup_1


def replace_transducer_mrbts_mrtbtsid_5(soup):
    ciq_value = get_ciq_value("mrbtsId", st.session_state['ciq_sitemain_par'])
    new_soup = re.sub(r'MRBTS-(\d{5})',
                      r'MRBTS-'f'{ciq_value}', str(soup))
    soup_1 = BeautifulSoup(new_soup, "xml")
    soup_1 = str(soup_1).replace('\n', '')
    return soup_1


def replace_transducer_lnbts_mrtbtsid_5(soup):
    ciq_value = get_ciq_value("mrbtsId", st.session_state['ciq_sitemain_par'])
    new_soup = re.sub(r'LNBTS-(\d{5})',
                      r'LNBTS-'f'{ciq_value}', str(soup))
    soup_1 = BeautifulSoup(new_soup, "xml")
    soup_1 = str(soup_1).replace('\n', '')
    return soup_1


# chain all the processing functions'''

def transducer_compose(soup):
    transducer_function = composite_function(
        replace_transducer_lnbts_mrtbtsid_5, replace_transducer_mrbts_mrtbtsid_5, enb_replace_transducer,
        bts_replace_transducer, userLabel_replace_transducer, utraCarrierFreq_replace_transducer, gatewayIpv6Addr_replace_transducer,
        endEarfcnDl_replace_first_transducer, startEarfcnDl_replace_first_transducer, startEarfcnDl_replace_second_transducer,
        endEarfcnDl_replace_second_transducer, second_vlan_replace_transducer, first_vlan_replace_transducer, first_localIpAddr_replace_transducer,
        second_localIpAddr_replace_transducer, cPlaneIpAddr_replace_transducer, adjGnbId_replace_transducer, eutraCarrierFreq_b66_append_transducer,
        eutraCarrierFreq_b12_append_transducer, lcrid_transducer, psgrp_transducer, modpr_transducer, capr_transducer, carel_transducer,
        mopr_transducer, amlepr_transducer, lnhoif_transducer)
    return transducer_function(soup)


def modpr_compose(modpr_soup):
    modpr_function = composite_function(freqLayListServiceBasedHo_xducer, freqLayListDedLteLB_xducer,
                                        freqLayListLte_xducer, freqLayListSrvccWcdma_xducer, redirFreqUtra_xducer, redirFreqEutra_xducer,
                                        freqLayListPsHoWcdma_xducer)
    return modpr_function(modpr_soup)


def mopr_compose(modr_soup):
    mopr_function = composite_function(freqLayListServiceBasedHo_xducer, freqLayListDedLteLB_mopr_xducer,
                                       freqLayListLte_mopr_xducer, freqLayListSrvccWcdma_mopr_xducer, redirFreqUtra_xducer, redirFreqEutra_xducer,
                                       freqLayListPsHoWcdma_mopr_xducer)
    return mopr_function(modr_soup)


# composite_function accepts N
# number of function as an
# argument and then compose them


def composite_function(*func):

    def compose(f, g):
        return lambda x: f(g(x))

    return reduce(compose, func, lambda x: x)


def get_rnd_sheet(sheet_name, uploaded_file_rnd_ciq):
    cell_par = pd.read_excel(
        uploaded_file_rnd_ciq, sheet_name=str(sheet_name), header=2, skiprows=None)
    cell_par = cell_par.dropna(thresh=5)
    # st.sidebar.write(cell_par)
    return cell_par


def get_edp_sheet(sheet_name, uploaded_file_edp):
    edp = pd.read_excel(uploaded_file_edp,
                        sheet_name=str(sheet_name), header=0, skiprows=25)
    return edp


def get_port_sheet(uploaded_file_port):
    port = pd.read_excel(uploaded_file_port, header=0, skiprows=None)
    port = port.iloc[:1, :4]
    return port


def get_ciq_value(parName, sheet):
    par_col = sheet[parName]
    col_list = [b for b in par_col.to_list() if not str(b).find('nan') > -1]
    par_str = col_list[-2]
    return par_str


def filter_int_list(par_list):
    return [e for e in par_list if isinstance(e, int)]


def filter_ear_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if int(st.session_state['endEarfcnDl_map'].get(
        'yes_freq_min')) < int(b) < int(st.session_state['endEarfcnDl_map'].get('yes_freq_max'))]
    return col_list


def filter_earfcnDl_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if int(st.session_state['endEarfcnDl_map'].get(
        'yes_freq_min')) < int(b) < int(st.session_state['endEarfcnDl_map'].get('yes_freq_max'))]
    return col_list


def filter_eutra_list_66(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if int(st.session_state['mfbipr_map'].get(
        'b66_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b66_max'))]
    return col_list


def filter_eutra_list_12(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if (int(st.session_state['mfbipr_map'].get(
        'b12_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b12_max'))) or (int(st.session_state['mfbipr_map'].get(
            'b17_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b17_max')))]
    return col_list


def filter_b12_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if (int(st.session_state['mfbipr_map'].get(
        'b12_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b12_max')))]
    return col_list


def filter_b17_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if (int(st.session_state['mfbipr_map'].get(
        'b17_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b17_max')))]
    return col_list


def filter_b29_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if (int(st.session_state['mfbipr_map'].get(
        'b29_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b29_max')))]
    return col_list


def filter_b25_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if (int(st.session_state['mfbipr_map'].get(
        'b25_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b25_max')))]
    return col_list


def filter_b14_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if (int(st.session_state['mfbipr_map'].get(
        'b14_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b14_max')))]
    return col_list


def filter_b4_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if (int(st.session_state['mfbipr_map'].get(
        'b4_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b4_max')))]
    return col_list


def filter_b30_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if (int(st.session_state['mfbipr_map'].get(
        'b30_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b30_max')))]
    return col_list


def filter_b66_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if (int(st.session_state['mfbipr_map'].get(
        'b66_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b66_max')))]
    return col_list


def filter_b2_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if (int(st.session_state['mfbipr_map'].get(
        'b2_min')) < int(b) < int(st.session_state['mfbipr_map'].get('b2_max')))]
    return col_list


def filter_port_list(par_list):
    int_list = filter_int_list(par_list)
    col_list = [b for b in int_list if int(st.session_state['endEarfcnDl_map'].get(
        'port_matrix_min')) < int(b) < int(st.session_state['endEarfcnDl_map'].get('port_matrix_max'))]
    return col_list


def get_ear_return_value(col_list):
    if len(col_list) > 0:
        par_str = col_list[-1]
    else:
        par_str = 'nan'
    return par_str


def get_lcrid_return_value(col_list):
    if len(col_list) > 0:
        par_str = col_list
    else:
        par_str = 'nan'
    return par_str


def get_port_return_value(col_list):
    if len(col_list) > 0 and str(st.session_state['port_matrix'].iloc[:, 3][0]).find('YES') > -1:
        par_str = col_list[-1]
    else:
        par_str = 'nan'
    return par_str


def get_ear_value(sheet):
    par_col = sheet["EARFCNdownlink"]
    col_list = filter_ear_list(par_col.to_list())
    return get_ear_return_value(col_list)


def get_wcdma_value(sheet):
    par_col = sheet["UTRADownlinkFrequencyasARFCNvalue"]
    col_list = filter_int_list(par_col.to_list())
    return get_ear_return_value(col_list)


def get_wcdma_femto_value(sheet):
    par_col = sheet["UTRADownlinkFrequencyasARFCNvalue"]
    col_list = filter_int_list(par_col.to_list())
    return get_ear_return_value(col_list)


def get_freqLayListDedLteLB_value(sheet, parent_mo=None):
    filt_list = get_modpr_list(sheet)
    dl_only_value = get_ear_value(sheet)
    port_value = get_port_value(sheet)
    dl_list = [b for b in filt_list if b not in [dl_only_value, port_value]]
    if str(parent_mo).find('MOPR-5') > -1 or str(parent_mo).find('MOPR-6') > -1:
        dl_list = get_mopr_5_6_value(sheet)
    return dl_list


def get_dlCarFrqEutL_value(sheet, parent_mo=None):
    filt_list = get_modpr_list(sheet)
    dl_only_value = get_ear_value(sheet)
    port_value = get_port_value(sheet)
    b2_value = filter_b2_list(filt_list)
    dl_list = [b for b in filt_list if b not in [dl_only_value, port_value]]
    if str(parent_mo).find('MOPR-2') > -1:
        dl_list = [b for b in filt_list if b not in [
            dl_only_value, port_value, b2_value]]
    if str(parent_mo).find('MOPR-5') > -1 or str(parent_mo).find('MOPR-6') > -1:
        dl_list = get_mopr_5_6_value(sheet)
    return dl_list


def get_redirFreqUtra_value(sheet, parent_mo=None):
    wcdma_value = get_wcdma_value(sheet)
    dl_list = [wcdma_value]
    if str(parent_mo).find('MOPR-5/MORED-1') > -1 or str(parent_mo).find('MOPR-6/MORED-1') > -1:
        dl_list = get_mopr_5_6_mored_1_value(sheet)
    return dl_list


def get_mopr_5_6_value(sheet):
    filt_list = get_modpr_list(sheet)
    b12_value = filter_eutra_list_12(filt_list)
    b2_value = filter_b2_list(filt_list)
    b4_value = filter_b4_list(filt_list)
    b30_value = filter_b30_list(filt_list)
    b66_value = filter_b66_list(filt_list)
    return b12_value + b2_value + b4_value + b30_value + b66_value


def get_mopr_5_6_mored_1_value(sheet):
    filt_list = get_modpr_list(sheet)
    b2_value = filter_b2_list(filt_list)
    return b2_value


def get_freqLayListLte_value(sheet):
    filt_list = get_modpr_list(sheet)
    dl_only_value = get_ear_value(sheet)
    port_value = get_port_value(sheet)
    b14_value = filter_b14_list(filt_list)
    dl_list = [b for b in filt_list if b not in [
        dl_only_value, port_value, b14_value]]
    return dl_list


def get_freqLayListLte_mopr_value(sheet, parent_mo=None):
    filt_list = get_modpr_list(sheet)
    dl_only_value = get_ear_value(sheet)
    port_value = get_port_value(sheet)
    b14_value = filter_b14_list(filt_list)
    dl_list = [b for b in filt_list if b not in [
        dl_only_value, port_value]]
    if str(parent_mo).find('MOPR-3') > -1 or str(parent_mo).find('MOPR-4') > -1:
        dl_list = [b for b in filt_list if b not in [
            dl_only_value, port_value, b14_value]]
    if str(parent_mo).find('MOPR-5') > -1 or str(parent_mo).find('MOPR-6') > -1:
        dl_list = get_mopr_5_6_value(sheet)
    return dl_list


def get_freqLayListPsHoWcdma_value(sheet):
    filt_list = get_modpr_list(sheet)
    wcdma_value = get_wcdma_value(sheet)
    wcdma_femto_value = get_wcdma_femto_value(sheet)
    dl_list = [wcdma_femto_value, wcdma_value]
    return dl_list


def get_freqLayListPsHoWcdma_mopr_value(sheet):
    filt_list = get_modpr_list(sheet)
    wcdma_value = get_wcdma_value(sheet)
    dl_list = [wcdma_value]
    return dl_list


def get_freqLayListEndcHo_mopr_value(sheet):
    filt_list = get_modpr_list(sheet)
    b14_value = filter_b14_list(filt_list)
    dl_list = [b14_value]
    return dl_list


def get_redirFreqEutra_value(sheet):
    filt_list = get_modpr_list(sheet)
    b2_value = filter_b2_list(filt_list)
    dl_list = b2_value
    return dl_list


def get_freqLayListServiceBasedHo_value(sheet):
    filt_list = get_modpr_list(sheet)
    b12_value = filter_eutra_list_12(filt_list)
    dl_list = b12_value
    return dl_list


def get_lcrid_value(sheet):
    par_col = sheet["lcrId"]
    col_list = filter_int_list(par_col.to_list())
    return get_lcrid_return_value(col_list)


def get_psgrp_value(sheet):
    par_col_key = sheet["LocalcellresourceID"].to_list()[4:]
    par_col_value = sheet["Cellname"].to_list()[4:]

    psgrp_dict = {lcrid: cellName for lcrid,
                  cellName in zip(par_col_key, par_col_value)}
    filt_psgrp_dict = filter_psgrp_panh(par_col_key, psgrp_dict)

    alpha = get_alpha_values(filt_psgrp_dict)
    beta = get_beta_values(filt_psgrp_dict)
    gamma = get_gamma_values(filt_psgrp_dict)
    delta = get_delta_values(filt_psgrp_dict)
    epsilon = get_epsilon_values(filt_psgrp_dict)

    return [alpha, beta, gamma, delta, epsilon]


def get_capr_value(sheet):
    par_col_key = sheet["LocalcellresourceID"].to_list()[4:]
    par_col_value = sheet["EARFCNdownlink"].to_list()[4:]
    capr_dict = {lcrid: earfcnDL for lcrid,
                 earfcnDL in zip(par_col_key, par_col_value)}
    filt_capr_dict = filter_psgrp_panh(par_col_key, capr_dict)
    return filt_capr_dict

# DownlinkMIMOmode


def get_carel_value(sheet):
    par_col_lcrid = sheet["LocalcellresourceID"].to_list()[4:]
    par_col_cell = sheet["Cellname"].to_list()[4:]
    par_col_ear = sheet["EARFCNdownlink"].to_list()[4:]
    par_col_mimo = sheet["DownlinkMIMOmode"].to_list()[4:]
    return filter_out_panh_and_dl_only(zip(par_col_lcrid, par_col_cell, par_col_ear, par_col_mimo))


def get_amlepr_value(sheet):
    par_col_lcrid = sheet["LocalcellresourceID"].to_list()[4:]
    par_col_ear = sheet["EARFCNdownlink"].to_list()[4:]
    return filter_out_panh_and_dl_only(zip(par_col_lcrid, par_col_ear))


def get_capr_band_value(sheet):
    par_col_key = sheet["EARFCNdownlink"].to_list()[4:]
    par_col_key = list(set(par_col_key))
    par_col_value = sheet["Downlinkchannelbandwidth"].to_list()[4:]
    par_col_value = list(set(par_col_value))
    capr_dict = {lcrid: earfcnDL for lcrid,
                 earfcnDL in zip(par_col_key, par_col_value)}
    return capr_dict


def get_amlepr_band_value(sheet):
    par_col_key = sheet["EARFCNdownlink"].to_list()[4:]
    par_col_key = list(set(par_col_key))
    par_col_value = sheet["Downlinkchannelbandwidth"].to_list()[4:]
    par_col_value = list(set(par_col_value))
    capr_dict = {lcrid: earfcnDL for lcrid,
                 earfcnDL in zip(par_col_key, par_col_value)}
    return capr_dict


def is_low_band(freq):
    return (len(filter_b12_list([freq]) + filter_b17_list([freq]) + filter_b29_list([freq])) > 0)


def is_high_band(freq):
    return (len(filter_b30_list([freq])) > 0)


def is_first_net(freq):
    return (len(filter_b14_list([freq])) > 0)


def is_medium_band(freq):
    return (len(filter_b2_list([freq]) + filter_b4_list([freq]) + filter_b25_list([freq]) + filter_eutra_list_66([freq])) > 0)


def get_modpr_list(sheet):
    par_col_key = sheet["LocalcellresourceID"].to_list()[4:]
    par_col_value = sheet["EARFCNdownlink"].to_list()[4:]

    psgrp_dict = {lcrid: earfcnDL for lcrid,
                  earfcnDL in zip(par_col_key, par_col_value)}
    return filter_modpr_panh(par_col_key, psgrp_dict)


def get_alpha_values(filt_psgrp_dict):
    filter_string = "A_"
    psgrp_soup = st.session_state['PSGRP']
    psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '0'
    filtered_dict = {
        k: v for (k, v) in filt_psgrp_dict.items() if filter_string in k}
    return get_psgrp_return_value(filtered_dict, psgrp_soup)


def get_beta_values(filt_psgrp_dict):
    filter_string = "B_"
    psgrp_soup = st.session_state['PSGRP']
    psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '1'
    filtered_dict = {
        k: v for (k, v) in filt_psgrp_dict.items() if filter_string in k}
    return get_psgrp_return_value(filtered_dict, psgrp_soup)


def get_gamma_values(filt_psgrp_dict):
    filter_string = "C_"
    psgrp_soup = st.session_state['PSGRP']
    psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '2'
    filtered_dict = {
        k: v for (k, v) in filt_psgrp_dict.items() if filter_string in k}
    return get_psgrp_return_value(filtered_dict, psgrp_soup)


def get_delta_values(filt_psgrp_dict):
    filter_string = "D_"
    psgrp_soup = st.session_state['PSGRP']
    psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '3'
    filtered_dict = {
        k: v for (k, v) in filt_psgrp_dict.items() if filter_string in k}
    return get_psgrp_return_value(filtered_dict, psgrp_soup)


def get_epsilon_values(filt_psgrp_dict):
    filter_string = "E_"
    psgrp_soup = st.session_state['PSGRP']
    psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '4'
    filtered_dict = {
        k: v for (k, v) in filt_psgrp_dict.items() if filter_string in k}
    return get_psgrp_return_value(filtered_dict, psgrp_soup)

# (reduce(lambda a, b: a if a > b else b, lis))
#  reduce(lambda a, b: a+b, lis)


def get_psgrp_return_value(filtered_dict, psgrp_soup):
    psgrp_soup = delete_items(psgrp_soup)
    if len(filtered_dict) > 0:
        for k in list(filtered_dict.values()):
            psgrp_soup.list.append(BeautifulSoup(return_item(k), "xml"))
            dom = xml.dom.minidom.parseString(str(psgrp_soup))
        par_str = BeautifulSoup(dom.toxml().replace('\n', ''), "xml")
    else:
        par_str = 'nan'
    return par_str


def return_item(i):
    return r'<item><p name="lbpsCellSOOrder">100</p><p name="lnCelId">' + str(i) + r'</p></item>'


def filter_psgrp_panh(par_col_key, psgrp_dict):
    key_list = st.session_state['5G_filter']
    filt_set = set(key_list)
    lcrid = set(par_col_key)
    filt_lcrid = [x for x in lcrid if x not in filt_set]
    print(filt_lcrid)
    filt_vals = [psgrp_dict[i] for i in filt_lcrid]
    print(filt_vals)
    return {Cellname: LocalcellresourceID for Cellname, LocalcellresourceID
            in zip(filt_vals, filt_lcrid)}


def filter_out_panh_and_dl_only(lcrid_list):
    key_list = st.session_state['5G_filter']
    filt_set = set(key_list)
    lcrid = set(lcrid_list)
    return [x for x in lcrid if x[0] not in filt_set and is_not_dl_only(x[2])]


def is_not_dl_only(freq):
    return len(filter_ear_list([freq]) + filter_port_list([freq])) > 0


def filter_modpr_panh(par_col_key, modpr_dict):
    key_list = st.session_state['psgrp_filter']
    filt_set = set(key_list)
    lcrid = set(par_col_key)
    filt_lcrid = [x for x in lcrid if x not in filt_set]
    print(filt_lcrid)
    filt_vals = [modpr_dict[i] for i in filt_lcrid]
    print(filt_vals)
    return filt_vals


def get_eutra_value_66(sheet):
    par_col = sheet["EARFCNdownlink"]
    col_list = filter_eutra_list_66(par_col.to_list())
    return get_ear_return_value(col_list)


def get_eutra_value_12(sheet):
    par_col = sheet["EARFCNdownlink"]
    col_list = filter_eutra_list_12(par_col.to_list())
    return get_ear_return_value(col_list)


def get_port_value(sheet):
    par_col = sheet["EARFCNdownlink"]
    col_list = filter_port_list(par_col.to_list())
    return get_port_return_value(col_list)


def app():
    st.title('AT&T Scripting')
    st.session_state['download'] = False
    st.session_state['xml_soup'] = ''
    st.session_state['ciq_sitemain_par'] = ''
    st.session_state['edp_raptor'] = ''
    st.session_state['port_matrix'] = ''
    st.session_state['endEarfcnDl_map'] = {'yes_freq_min': 9660, 'yes_freq_max': 9769,
                                           'port_matrix_min': 66436, 'port_matrix_max': 67335}
    st.session_state['mfbipr_map'] = {'b12_min': 5010, 'b12_max': 5179,
                                      'b17_min': 5730, 'b17_max': 5849, 'b66_min': 66436, 'b66_max': 67335,
                                      'b14_min': 5280, 'b14_max': 5379, 'b2_min': 600, 'b2_max': 800,
                                      'b4_min': 1950, 'b4_max': 2399, 'b30_min': 9770, 'b30_max': 9869,
                                      'b29_min': 9660, 'b29_max': 9769, 'b25_min': 825, 'b25_max': 1100}
    st.session_state['band_cell_mapping'] = {'alpha': [('B12', 15, '_7A_1'), ('B2', 8, '_9A_1'), ('B4', 22, '_2A_1'),
                                                       ('B30', 149, '_3A_1'), ('B29', 172, '_7A_2_E'), (
                                                           'B25', 179, '_9A_2'), ('B14', 193, '_7A_3_F'),
                                                       ('B66', 186, '_2A_2'), ('B2_C2', 200, '_9A_3'), ], }
    st.session_state['dlMimoMode'] = {'SingleTX':	0,
                                      'TXDiv':	0,
                                      '4-way TXDiv':	0,
                                      'Dynamic Open Loop MIMO':	'2-layer',
                                      'Closed Loop Mimo':	'2-layer',
                                      'Closed Loop MIMO (4x2)':	'2-layer',
                                      'Closed Loop MIMO (8x2)':	'2-layer',
                                      'Closed Loop MIMO (4x4)':	'4-layer',
                                      'Closed Loop MIMO (8x4)':	'4-layer',
                                      'Closed Loop MIMO (16x2)':	'2-layer'}

    st.session_state['lnh_dlch'] = {
        20: 'mbw100',
        15: 'mbw75',
        10: 'mbw50',
        5:  'mbw25'
    }

    st.session_state['amlepr'] = {'FirstNet': {
        'FirstNet': {
            'cacHeadroom': 100,
            'maxCacThreshold':  40,
            'deltaCac': 15
        },
        'LB': {
            {
                'cacHeadroom': 0,
                'maxCacThreshold':  80,
                'deltaCac': 0
            }
        },
        'MB/HB': {
            'cacHeadroom': 0,
            'maxCacThreshold':  60,
            'deltaCac': 0
        }

    },
        'Default': {
        'cacHeadroom': 40,
        'maxCacThreshold':  40,
        'deltaCac': 15
    }
    }
    st.session_state['lnhoif'] = {'MB': {
        'FirstNet': {
            'threshold3InterFreq': 20,
            'threshold3InterFreqQci1':  22,
            'threshold3aInterFreq': 20,
            'threshold3aInterFreqQci1': 22,
            'thresholdRsrpIFLBFilter': -108

        },
        'LB': {
            {
                'threshold3InterFreq': 18,
                'threshold3InterFreqQci1':  20,
                'threshold3aInterFreq': 18,
                'threshold3aInterFreqQci1': 20,
                'thresholdRsrpIFLBFilter': -108
            }
        },
        'MB': {
            'threshold3InterFreq': 18,
            'threshold3InterFreqQci1':  20,
            'threshold3aInterFreq': 18,
            'threshold3aInterFreqQci1': 20,
            'thresholdRsrpIFLBFilter': -116
        },
        'HB': {
            'threshold3InterFreq': 18,
            'threshold3InterFreqQci1':  20,
            'threshold3aInterFreq': 18,
            'threshold3aInterFreqQci1': 20,
            'thresholdRsrpIFLBFilter': -116
        }

    },
        'HB': {
        'FirstNet': {
            'threshold3InterFreq': 20,
            'threshold3InterFreqQci1':  22,
            'threshold3aInterFreq': 20,
            'threshold3aInterFreqQci1': 22,
            'thresholdRsrpIFLBFilter': -108

        },
        'LB': {
            {
                'threshold3InterFreq': 22,
                'threshold3InterFreqQci1':  22,
                'threshold3aInterFreq': 22,
                'threshold3aInterFreqQci1': 22,
                'thresholdRsrpIFLBFilter': -108
            }
        },
        'MB': {
            'threshold3InterFreq': 18,
            'threshold3InterFreqQci1':  20,
            'threshold3aInterFreq': 18,
            'threshold3aInterFreqQci1': 20,
            'thresholdRsrpIFLBFilter': -116
        }

    },
        'LB': {
        'FirstNet': {
            'threshold3InterFreq': 20,
            'threshold3InterFreqQci1':  22,
            'threshold3aInterFreq': 20,
            'threshold3aInterFreqQci1': 22,
            'thresholdRsrpIFLBFilter': -116

        },
        'LB': {
            {
                'threshold3InterFreq': 20,
                'threshold3InterFreqQci1':  22,
                'threshold3aInterFreq': 20,
                'threshold3aInterFreqQci1': 22,
                'thresholdRsrpIFLBFilter': -108
            }
        },
        'MB': {
            'threshold3InterFreq': 27,
            'threshold3InterFreqQci1':  27,
            'threshold3aInterFreq': 32,
            'threshold3aInterFreqQci1': 32,
            'thresholdRsrpIFLBFilter': -116
        },
        'HB': {
            'threshold3InterFreq': 27,
            'threshold3InterFreqQci1':  27,
            'threshold3aInterFreq': 32,
            'threshold3aInterFreqQci1': 32,
            'thresholdRsrpIFLBFilter': -116
        }

    },
        'FirstNet': {
        'LB': {
            {
                'threshold3InterFreq': 22,
                'threshold3InterFreqQci1':  22,
                'threshold3aInterFreq': 22,
                'threshold3aInterFreqQci1': 22,
                'thresholdRsrpIFLBFilter': -116
            }
        },
        'MB': {
            'threshold3InterFreq': 22,
            'threshold3InterFreqQci1':  22,
            'threshold3aInterFreq': 22,
            'threshold3aInterFreqQci1': 22,
            'thresholdRsrpIFLBFilter': -116
        },
        'HB': {
            'threshold3InterFreq': 19,
            'threshold3InterFreqQci1':  19,
            'threshold3aInterFreq': 97,
            'threshold3aInterFreqQci1': 97,
            'thresholdRsrpIFLBFilter': -116
        }

    },
        'Default': {
        'threshold3InterFreq': 19,
        'threshold3InterFreqQci1':  19,
        'threshold3aInterFreq': 97,
        'threshold3aInterFreqQci1': 97,
        'thresholdRsrpIFLBFilter': -108

    }
    }

    st.session_state['mrbts_id'] = get_ciq_value(
        "mrbtsId", st.session_state['ciq_sitemain_par'])

    st.session_state['psgrp_filter'] = [25, 49, 72, 73, 193, 194, 195]
    st.session_state['5G_filter'] = [25, 49, 72, 73]
    st.sesssion_state['freq_prio_medium_band'] = {
        '5mhz': 8, '15mhz': 3, '20mhz': 3, '10mhz': 5}
    st.sesssion_state['freq_prio_low_band'] = {
        '5mhz': 9, '10mhz': 7}
    st.sesssion_state['freq_high_medium_band'] = 10
    # MFBIPR-B66
    st.session_state['mfbipr_66'] = BeautifulSoup(
        xml_templates.return_xml('MFBIPR-B66'), "xml")
    st.session_state['mfbipr_12'] = BeautifulSoup(
        xml_templates.return_xml('MFBIPR-B12'), "xml")
    st.session_state['NRDCDPR'] = BeautifulSoup(
        xml_templates.return_xml('NRDCDPR'), "xml")
    st.session_state['PSGRP'] = BeautifulSoup(
        xml_templates.return_xml('PSGRP'), "xml")
    st.session_state['MODPR'] = BeautifulSoup(
        xml_templates.return_xml('MODPR'), "xml")
    st.session_state['MOPR'] = BeautifulSoup(
        xml_templates.return_xml('MOPR'), "xml")
    st.session_state['CAPR'] = BeautifulSoup(
        xml_templates.return_xml('CAPR'), "xml")
    st.session_state['CAREL'] = BeautifulSoup(
        xml_templates.return_xml('CAREL'), "xml")
    st.session_state['AMLEPR'] = BeautifulSoup(
        xml_templates.return_xml('CAREL'), "xml")
    st.session_state['LNHOIF'] = BeautifulSoup(
        xml_templates.return_xml('CAREL'), "xml")
    st.session_state['root_xml'] = BeautifulSoup(
        xml_templates.return_xml(), "xml")

    def process_xml(soup, ciq_sitemain_par, key_list, filter_dict):
        # st.sidebar.table(ciq_sitemain_par)
        if uploaded_file_rnd_ciq is not None:

            with st.spinner('Please Kindly Wait...'):
                processed_soup = transducer_compose(soup)
            st.session_state['download'] = True
            st.success('XML successfully parsed :point_down:!!')
            st.session_state['xml_soup'] = str(processed_soup)
        return processed_soup

    with st.form("my_form"):
        with st.container():

            hide_st_style = """
                    <style>
                    # MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
            st.markdown(hide_st_style, unsafe_allow_html=True)

            # col1, col2 = st.columns([1, 3])

            # col1.markdown('**Upload NR CIQ file**.')
            uploaded_file_rnd_ciq = st.file_uploader(
                "Upload RND CIQ File", key="rndciq")
            if uploaded_file_rnd_ciq is not None:
                ciq_cell_par = get_rnd_sheet('CELLPAR', uploaded_file_rnd_ciq)
                # st.sidebar.table(ciq_cell_par)
                st.session_state['ciq_cell_par'] = ciq_cell_par
                ciq_sitemain_par = get_rnd_sheet(
                    'SITEMAINPAR', uploaded_file_rnd_ciq)
                st.session_state['ciq_sitemain_par'] = ciq_sitemain_par
            uploaded_file_edp_raptor = st.file_uploader(
                "Upload EDP File", key="edp")
            if uploaded_file_edp_raptor is not None:
                edp_raptor = get_edp_sheet('raptor', uploaded_file_edp_raptor)
                st.session_state['edp_raptor'] = edp_raptor
            uploaded_file_port_matrix = st.file_uploader(
                "Upload Port Matrix File", key="port")
            if uploaded_file_port_matrix is not None:
                port_matrix = get_port_sheet(uploaded_file_edp_raptor)
                st.session_state['port_matrix'] = port_matrix

            # xml_list = list(xml_dict.keys())
            # option = st.selectbox('FDD EQM Options', xml_list)
            # print(
            # len(xml_dict["3AHLOA(shared)_20BW+3AEHC (shared)_100BW_NoAHFIG"]))

            soup = st.session_state['root_xml']
        submitted = st.form_submit_button("Process XML")
        if submitted:
            # time.sleep(1)
            st.session_state['xml_soup'] = process_xml(
                soup, ciq_sitemain_par, key_list, filter_dict)
    if st.session_state['download']:

        # or xml.dom.minidom.parseString(xml_string)
        # print(soup.prettify())
        dom = xml.dom.minidom.parseString(str(st.session_state['xml_soup']))
        pretty_xml_as_string = dom.toprettyxml()
        mrbts_id = get_ciq_value(
            "mrbtsId", st.session_state['ciq_sitemain_par'])
        st.download_button(label='📥 Download XML ',
                           data=pretty_xml_as_string,
                           file_name=f'{str(mrbts_id)}.xml')


app()
