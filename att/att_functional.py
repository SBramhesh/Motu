import re
from bs4 import BeautifulSoup
import copy
import xml_templates
import streamlit as st
import xlsxwriter
import pandas as pd
from functools import reduce
import xml.dom.minidom

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


def lcrid_psgrp_xducer(psgrp_soup):
    psgrp_soup = delete_items(psgrp_soup)
    psgrp_list = get_psgrp_value(
        st.session_state['ciq_cell_par'], psgrp_soup)
    return list(filter(lambda x: x != 'nan', psgrp_list))


def delete_items(psgrp_soup):
    for i in range(len(psgrp_soup.list.find_all("item"))):
        psgrp_soup.list.item.decompose()
    return psgrp_soup


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
        eutraCarrierFreq_b12_append_transducer, lcrid_transducer, psgrp_transducer)
    return transducer_function(soup)


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
    par_col = sheet["earfcnDL"]
    col_list = filter_ear_list(par_col.to_list())
    return get_ear_return_value(col_list)


def get_lcrid_value(sheet):
    par_col = sheet["lcrId"]
    col_list = filter_int_list(par_col.to_list())
    return get_lcrid_return_value(col_list)


def get_psgrp_value(sheet, psgrp_soup):
    par_col_key = sheet["LocalcellresourceID"].to_list()[4:]
    par_col_value = sheet["Cellname"].to_list()[4:]

    psgrp_dict = {lcrid: cellName for lcrid,
                  cellName in zip(par_col_key, par_col_value)}
    filt_psgrp_dict = filter_psgrp_panh(par_col_key, psgrp_dict)

    alpha = get_alpha_values(filt_psgrp_dict, psgrp_soup)
    beta = get_beta_values(filt_psgrp_dict, psgrp_soup)
    gamma = get_gamma_values(filt_psgrp_dict, psgrp_soup)
    delta = get_delta_values(filt_psgrp_dict, psgrp_soup)
    epsilon = get_epsilon_values(filt_psgrp_dict, psgrp_soup)

    return [alpha, beta, gamma, delta, epsilon]


def get_alpha_values(filt_psgrp_dict, psgrp_soup):
    filter_string = "A_"
    psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '0'
    filtered_dict = {
        k: v for (k, v) in filt_psgrp_dict.items() if filter_string in k}
    return get_psgrp_return_value(filtered_dict, psgrp_soup)


def get_beta_values(filt_psgrp_dict, psgrp_soup):
    filter_string = "B_"
    psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '1'
    filtered_dict = {
        k: v for (k, v) in filt_psgrp_dict.items() if filter_string in k}
    return get_psgrp_return_value(filtered_dict, psgrp_soup)


def get_gamma_values(filt_psgrp_dict, psgrp_soup):
    filter_string = "C_"
    psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '2'
    filtered_dict = {
        k: v for (k, v) in filt_psgrp_dict.items() if filter_string in k}
    return get_psgrp_return_value(filtered_dict, psgrp_soup)


def get_delta_values(filt_psgrp_dict, psgrp_soup):
    filter_string = "D_"
    psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '3'
    filtered_dict = {
        k: v for (k, v) in filt_psgrp_dict.items() if filter_string in k}
    return get_psgrp_return_value(filtered_dict, psgrp_soup)


def get_epsilon_values(filt_psgrp_dict, psgrp_soup):
    filter_string = "E_"
    psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '4'
    filtered_dict = {
        k: v for (k, v) in filt_psgrp_dict.items() if filter_string in k}
    return get_psgrp_return_value(filtered_dict, psgrp_soup)


def get_psgrp_return_value(filtered_dict, psgrp_soup):
    if len(len(filtered_dict)) > 0:
        for k in list(filtered_dict.values()):
            psgrp_soup.list.append(BeautifulSoup(return_item(k), "xml"))
            psgrp_soup.managedObject['distName'] = psgrp_soup.managedObject['distName'][:-1] + '0'
            dom = xml.dom.minidom.parseString(str(psgrp_soup))
        par_str = BeautifulSoup(dom.toxml().replace('\n', ''), "xml")
    else:
        par_str = 'nan'
    return par_str


def return_item(i):
    return r'<item><p name="lbpsCellSOOrder">100</p><p name="lnCelId">' + str(i) + r'</p></item>'


def filter_psgrp_panh(par_col_key, psgrp_dict):
    key_list = st.session_state['psgrp_filter']
    filt_set = set(key_list)
    lcrid = set(par_col_key)
    filt_lcrid = [x for x in lcrid if x not in filt_set]
    print(filt_lcrid)
    filt_vals = [psgrp_dict[i] for i in filt_lcrid]
    print(filt_vals)
    return {Cellname: LocalcellresourceID for Cellname, LocalcellresourceID
            in zip(filt_vals, filt_lcrid)}


def get_eutra_value_66(sheet):
    par_col = sheet["earfcnDL"]
    col_list = filter_eutra_list_66(par_col.to_list())
    return get_ear_return_value(col_list)


def get_eutra_value_12(sheet):
    par_col = sheet["earfcnDL"]
    col_list = filter_eutra_list_12(par_col.to_list())
    return get_ear_return_value(col_list)


def get_port_value(sheet):
    par_col = sheet["earfcnDL"]
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
                                      'b17_min': 5730, 'b17_max': 5849, 'b66_min': 66436, 'b66_max': 67335}
    st.session_state['psgrp_filter'] = [25, 49, 72, 73, 193, 194, 195]
    # MFBIPR-B66
    st.session_state['mfbipr_66'] = BeautifulSoup(
        xml_templates.return_xml('MFBIPR-B66'), "xml")
    st.session_state['mfbipr_12'] = BeautifulSoup(
        xml_templates.return_xml('MFBIPR-B12'), "xml")
    st.session_state['NRDCDPR'] = BeautifulSoup(
        xml_templates.return_xml('NRDCDPR'), "xml")
    st.session_state['PSGRP'] = BeautifulSoup(
        xml_templates.return_xml('PSGRP'), "xml")
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
