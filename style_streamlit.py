import streamlit as st
import streamlit.components.v1 as components


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">',
                unsafe_allow_html=True)


def icon(icon_name):
    st.markdown(
        f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)


local_css("style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

icon("search")
selected = st.text_input("", "Search...")
button_clicked = st.button("OK")

uploaded_file = st.file_uploader("Choose a file")


# bootstrap 4 collapse example
components.html(
    """
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <link
      rel="stylesheet"
      href="http://3.108.61.21/assets/css/bootstrap.min.css"
    />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    <!-- <link rel="stylesheet" href="./style.css" />
    <link
      rel="stylesheet"
      href="http://3.108.61.21/assets/font-awesome/4.5.0/css/font-awesome.min.css"
    />
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/fork-awesome/1.1.7/css/fork-awesome.min.css"
      integrity="sha256-gsmEoJAws/Kd3CjuOQzLie5Q3yshhvmo7YNtBG7aaEY="
      crossorigin="anonymous"
    />
    <link
      rel="stylesheet"
      href="http://3.108.61.21/assets/css/fonts.googleapis.com.css"
    /> -->
    <link
      rel="stylesheet"
      href="http://3.108.61.21/assets/css/ace.min.css"
      class="ace-main-stylesheet"
      id="main-ace-style"
    />
    
    </style> -->
    <link rel="stylesheet" href="./index.css">
    <link
      rel="stylesheet"
      href="/assets/css/bootstrap-multiselect.min.css"
    />
  </head>
  <body>
    
    <div class="main-container ">
      
      <!-- <div class="sidebar responsive ace-save-state">

        </div> -->
      <div class="main-content">
        <div class="main-content-inner">
          <div class="page-content">
            <div class="row">
              <div class="col-xs-12"></div>
            </div>
            <div class="row">
              <div class="col-xs-3">
                
                                
                             
              </div>
              
              <div class="col-xs-5">
                <form action="" class="form-horizontal" role="form">
                  <div class="widget-box">
                    <div class="widget-header">
                      <!-- :: before -->
                      <h4 class="widget-title">5G / NR Input</h4>
                      <!-- :: after -->
                    </div>
                    <div class="widget-main">
                      <div class="form-group">
                        <label
                          for=""
                          class="col-sm-3 control-label no-padding-right"
                          >NR CIQ File</label
                        >
                        <div class="col-sm-8 button-wrap style">
                          <label for="" class="button">
                            <input
                              type="file"
                              name=""
                              id=""
                              class="form-control"
                              accept=".xlsx"
                            />
                            
                          </label>
                        </div>
                        <!-- ::after -->
                      </div>
                      <div class="form-group">
                        <label
                          for=""
                          class="col-sm-3 control-label no-padding-right"
                          >LTE CIQ File</label
                        >
                        <div class="col-sm-8 style button-wrap">
                          <label for="" class="button">
                            <input
                              type="file"
                              name=""
                              id=""
                              class="form-control"
                              accept=".xlsx"
                            />
                           
                           
                          </label>
                        </div>
                        <!-- ::after -->
                      </div>
                      <div class="form-group">
                        <label
                          for=""
                          class="col-sm-3 control-label no-padding-right"
                          >Transmission 5G</label
                        >
                        <div class="col-sm-8 style button-wrap" padding-top-3>
                          <label for="" class="button">
                            <input
                              type="file"
                              name=""
                              id=""
                              class="form-control"
                              accept=".xlsx"
                            />
                            
                            
                          </label>
                        </div>
                        <!-- ::after -->
                      </div>
                      <div class="form-group">
                        <label
                          for=""
                          class="col-sm-3 control-label  no-padding-right"
                          >Transmission 4G</label
                        >
                        <div class="col-sm-8 style button-wrap">
                          <label for="" class="button">
                            <input
                              type="file"
                              name=""
                              class="form-control"
                              id=""
                              accept=""
                            />
                            
                          </label>
                        </div>
                        <!-- ::after -->
                      </div>
                      <div class="form-group">
                        <!-- ::before -->
                          <label
                            for="form-field-2"
                            class="col-sm-3 control-label no-padding-right"
                            >FDD EQM</label
                          >
                          <div class="col-sm-8">
                            <select
                              name=""
                              id=""
                              class="form-control"
                              required
                            >
                              <option value>-- Select FDD EQM --</option>
                              <option
                                value="5G_FDD_1-AHLOA(Shared) + 1 - AHFIG(Shared)_1-ASIK+2-ABIL_N6_N19.xml"
                              >
                                3AHLOA(shared)_15BW_3AEHC(shared)_100BW_NoAHFIG
                              </option>
                              <option
                                value="5G_FDD_2-AHLOA(Shared) + 2 - AHFIG(Shared)_1-ASIK+2-ABIL_N6_N19.xml"
                              >
                                3AHLOA(shared)_15BW_3AEHC(shared)_100BW_NoAHFIG
                              </option>
                              <option
                                value="5G_FDD_3-AHLOA(Shared) + 3 - AHFIG(Shared)_1-ASIK+2-ABIL_N6_N19.xml"
                              >
                                3AHLOA(shared)_15BW_3AEHC(shared)_100BW_NoAHFIG
                              </option>
                              <option
                                value="5G_FDD_4-AHLOA(Shared) + 4 - AHFIG(Shared)_1-ASIK+2-ABIL_N6_N19.xml"
                              >
                                3AHLOA(shared)_15BW_3AEHC(shared)_100BW_NoAHFIG
                              </option>
                              <option
                                value="5G_FDD_5-AHLOA(Shared) + 5 - AHFIG(Shared)_1-ASIK+2-ABIL_N6_N19.xml"
                              >
                                3AHLOA(shared)_15BW_3AEHC(shared)_100BW_NoAHFIG
                              </option>
                              <option
                                value="5G_FDD_6-AHLOA(Shared) + 6 - AHFIG(Shared)_1-ASIK+2-ABIL_N6_N19.xml"
                              >
                                3AHLOA(shared)_15BW_3AEHC(shared)_100BW_NoAHFIG
                              </option>
                              <option
                                value="5G_FDD_7-AHLOA(Shared) + 7 - AHFIG(Shared)_1-ASIK+2-ABIL_N6_N19.xml"
                              >
                                3AHLOA(shared)_15BW_3AEHC(shared)_100BW_NoAHFIG
                              </option>
                              <option
                                value="5G_FDD_8-AHLOA(Shared) + 8 - AHFIG(Shared)_1-ASIK+2-ABIL_N6_N19.xml"
                              >
                                3AHLOA(shared)_15BW_3AEHC(shared)_100BW_NoAHFIG
                              </option>
                            </select>
                          </div>
                        <!-- :: after -->
                      </div>
                      <div class="clearfix form-actions">
                        <div class="col-md-offset-2 col-md-9">
                          <button class="btn btn-sm btn-info" type="submit">
                            <i class="ace-icon fa fa-check"> Submit </i>
                          </button>
  
                          &nbsp; &nbsp; &nbsp;
  
                          <button class="btn btn-sm" type="reset">
                            <i class="ace-icon fa fa-undo"> Reset </i>
                          </button>
                        </div>
                      </div>
                    </div>
                     

                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <script src="http://3.108.61.21/assets/js/jquery-2.1.4.min.js"></script>
    <script type="text/javascript">
      if ("ontouchstart" in document.documentElement)
        document.write(
          "<script src='http://3.108.61.21/assets/js/jquery.mobile.custom.min.js'>" +
            "<" +
            "/script>"
        );

      $(".alert")
        .delay(4000)
        .slideUp(200, function () {
          $(this).alert("close");
        });
    </script>
    <script src="http://3.108.61.21/assets/js/bootstrap.min.js"></script>
    <script src="http://3.108.61.21/assets/js/ace-elements.min.js"></script>
    <script src="http://3.108.61.21/assets/js/ace.min.js"></script>
    <script type="text/javascript">
    

      $("#NR_CIQ_File").ace_file_input({
        no_file: "Please Select NR CIQ File...",
        btn_choose: "Choose",
        btn_change: "Change",
        droppable: false,
        onchange: null,
        thumbnail: false, //| true | large
        whitelist: "xlsx",
        //blacklist:'exe|php'
      });
      $("#LTE_CIQ_File").ace_file_input({
        no_file: "Please Select LTE CIQ File...",
        btn_choose: "Choose",
        btn_change: "Change",
        droppable: false,
        onchange: null,
        thumbnail: false, //| true | large
        whitelist: "xlsx",
        //blacklist:'exe|php'
      });
      $("#TND_File_5G").ace_file_input({
        no_file: "Please Select Transmission 5G Ciq File...",
        btn_choose: "Choose",
        btn_change: "Change",
        droppable: false,
        onchange: null,
        thumbnail: false, //| true | large
        whitelist: "xlsx",
        //blacklist:'exe|php'
      });

      $("#TND_File_4G").ace_file_input({
        no_file: "Please Select Transmission 4G Ciq File...",
        btn_choose: "Choose",
        btn_change: "Change",
        droppable: false,
        onchange: null,
        thumbnail: false, //| true | large
        whitelist: "xlsx",
        //blacklist:'exe|php'
      });
    </script>
    <script src="http://3.108.61.21/assets/js/bootstrap-multiselect.min.js"></script>
    <script>
      $(".multiselect").multiselect({
        buttonWidth: "100%",

        enableFiltering: false,
        enableHTML: true,
        buttonClass: "btn btn-white btn-primary",
        templates: {
          button:
            '<button type="button" class="multiselect dropdown-toggle" data-toggle="dropdown"><span class="multiselect-selected-text"></span> &nbsp;<b class="fa fa-caret-down"></b></button>',
          ul: '<ul class="multiselect-container dropdown-menu"></ul>',
          filter:
            '<li class="multiselect-item filter"><div class="input-group"><span class="input-group-addon"><i class="fa fa-search"></i></span><input class="form-control multiselect-search" type="text"></div></li>',
          filterClearBtn:
            '<span class="input-group-btn"><button class="btn btn-default btn-white btn-grey multiselect-clear-filter" type="button"><i class="fa fa-times-circle red2"></i></button></span>',
          li: '<li><a tabindex="0"><label></label></a></li>',
          divider: '<li class="multiselect-item divider"></li>',
          liGroup:
            '<li class="multiselect-item multiselect-group"><label></label></li>',
        },
      });
    </script>
  </body>
</html>
    """,
    height=600,
)
