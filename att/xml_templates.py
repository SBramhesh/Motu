import os
from bs4 import BeautifulSoup
from os.path import exists
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS, RDF
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS, XSD
import redis
import uuid
from uuid import UUID
from kazoo.client import KazooClient
import streamlit as st
from io import StringIO

zk = KazooClient(hosts='127.0.0.1:2181', read_only=True)
zk.start()

r = redis.Redis(
    host='localhost',
    port='6379')

st.session_state['g_template'] = Graph()

st.session_state['redis'] = redis.Redis(
    host='localhost',
    port='6379')


# Tool_4G_MRBTS-26178_PAL06178


def return_xml(template='Root'):
    ttl_data, ttl_stat = zk.get(
        "/www.integertel.com/att_scripting/template")
    g_read = Graph()
    g_read.parse(data=ttl_data)
    for s, p, o in g_read.triples((Literal(str(template)),  RDF.XMLLiteral, None)):
        print(f"{s} is a ===>>{o}")
    return str(o).replace('\n', '')


def app():
    st.title('AT&T Template Admin')
    ttl_data, ttl_stat = zk.get(
        "/www.integertel.com/att_scripting/template")
    st.session_state['g_template'] = Graph().parse(data=ttl_data)

    def set_redis_data(ttl_data, ttl_stat, r):
        stat_string = ttl_stat.__repr__()
        meta_str = stat_string.split('(')[1][:-2]
        print(meta_str)
        meta_dict = dict(meta_string.split("=")
                         for meta_string in meta_str.split(","))
        meta_dict['data'] = str(ttl_data).replace('\\n', '')
        r.hmset(str(ttl_uuid), meta_dict)
    # r.set(int(ttl_stat.version), att_ttl)

    with st.form("upload_template_form"):
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
            uploaded_file_template = st.file_uploader(
                "Upload template File", key="template")

            submitted = st.form_submit_button("Upload template")
            if submitted:
                with st.spinner('Please Kindly Wait...'):
                    # commit_file()
                    if uploaded_file_template is not None:
                        uploadedfn = uploaded_file_template.name
                        print(type(uploaded_file_template))

                        # To convert to a string based IO:
                        stringio = StringIO(
                            uploaded_file_template.getvalue().decode("utf-8"))
                        # print(stringio.read())

                    # xml_dict[str(uploadedfn)[:-4]] = str(stringio.read())
                    st.session_state['g_template'].add((
                        Literal(str(uploadedfn)[:-4]),
                        RDF.XMLLiteral,
                        Literal(str(stringio.read()), datatype=XSD.string)
                    ))
                    print(st.session_state['g_template'].serialize(
                        format="turtle"))
                    att_ttl = st.session_state['g_template'].serialize(
                        format="turtle")
                    att_bytes = bytes(att_ttl, 'utf-8')
                    ttl_uuid = uuid.uuid4()
                    # Ensure a path, create if necessary
                    zk.ensure_path(
                        "/www.integertel.com/att_scripting/template")
                    zk.set("/www.integertel.com/att_scripting/template", att_bytes)
                    # zk.set(
                    # "/www.integertel.com/att_scripting/template/uuid", ttl_uuid)
                    # Now store data and metadata in Redis with the uuid

                    st.success('File successfully uploaded :fire:!!')

    @zk.DataWatch("/www.integertel.com/att_scripting/template")
    def watch_node(ttl_data, ttl_stat, r):
        print("Version: %s, data: %s" %
              (ttl_stat.version, ttl_data.decode("utf-8")))
        set_redis_data(ttl_data, ttl_stat, st.session_state['redis'])
        # put the stat and the data on the pub/sun channel


app()
