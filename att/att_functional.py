import re
from bs4 import BeautifulSoup
import copy
import xml_templates
import streamlit as st
import xlsxwriter
import pandas as pd
from functools import reduce
import xml.dom.minidom

xml_dict = xml_templates.return_dict()

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


def gatewayIpv6Addr_replace_transducer(soup):
    mf_tags = soup.find_all(
        attrs={"name": "gatewayIpv6Addr"})
    for mf_tag in mf_tags:
        mf_tag.string = str(get_ciq_value(
            "IPV6_SIAD_OAM_IP_DEF_ROUTER", st.session_state['edp_raptor']))
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


def get_nrcell_dict(parName, ciq_cell_par):
    mode = ciq_cell_par[str(parName)]
    lcrid = ciq_cell_par['lcrid']
    mode_lst = mode.to_list()
    lcrid_lst = lcrid.to_list()
    comb_list = zip(mode_lst, lcrid_lst)
    dict = {lcrid: mode for mode, lcrid in comb_list}
    return dict


# chain all the processing functions'''


def nrcell_modify(key_list, filter_dict, ciq_sheet, soup):
    for i in key_list:
        pci_dict = get_nrcell_dict(i, ciq_sheet)
        filter_function = filter_dict.get(i)
        comp_function = composite_function(
            filter_function(nrcell_par_dict.get(i), soup, pci_dict))
    parName, soup, mf_dict = comp_function()
    return copy.copy(soup)


def transducer_compose(soup):
    transducer_function = composite_function(
        replace_transducer_lnbts_mrtbtsid_5, replace_transducer_mrbts_mrtbtsid_5, enb_replace_transducer, bts_replace_transducer, userLabel_replace_transducer, utraCarrierFreq_replace_transducer, gatewayIpv6Addr_replace_transducer)
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


def get_ciq_value(parName, sheet):
    par_col = sheet[parName]
    col_list = [b for b in par_col.to_list() if not str(b).find('nan') > -1]
    par_str = col_list[-1]
    return par_str


def app():
    st.title('AT&T Scripting')
    st.session_state['download'] = False
    st.session_state['xml_soup'] = ''
    st.session_state['ciq_sitemain_par'] = ''
    st.session_state['edp_raptor'] = ''

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
                # st.sidebar.table(ciq_cell_par)
                st.session_state['edp_raptor'] = edp_raptor

            xml_list = list(xml_dict.keys())
            option = st.selectbox('FDD EQM Options', xml_list)
            # print(
            # len(xml_dict["3AHLOA(shared)_20BW+3AEHC (shared)_100BW_NoAHFIG"]))
            xml_str = str(xml_dict[option]).replace('\n', '')

            soup = BeautifulSoup(xml_str, "xml")
        submitted = st.form_submit_button("Process XML")
        if submitted:
            # time.sleep(1)
            final_soup = process_xml(
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
                           file_name=f'{str(mrbts_id)}-{option}.xml')


app()
