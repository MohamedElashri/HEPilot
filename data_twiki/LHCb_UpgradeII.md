LHCbUpgradeII \< LHCb \< TWiki \@import
url(\'/twiki/pub/TWiki/TWikiTemplates/base.css\'); #patternTopBar,
#patternClearHeaderCenter, #patternClearHeaderLeft,
#patternClearHeaderRight, #patternTopBarContentsOuter,
#patternTopBarContents { height:64px; /\\\* top bar height; make room
for header columns \\\*/ overflow:hidden; } #patternOuter {
margin-left:14em; } #patternLeftBar { width:14em; margin-left:-14em; }
\@import url(\'/twiki/pub/TWiki/PatternSkin/layout.css\'); \@import
url(\'/twiki/pub/TWiki/PatternSkin/style.css\'); \@import
url(\'/twiki/pub/TWiki/PatternSkin/colors.css\'); /\\\* Styles that are
set using variables \\\*/ .patternBookView .twikiTopRow,
.patternWebIndicator a img, .patternWebIndicator a:hover img {
background-color:#99FF99; } #patternTopBarContents {
background-image:url(/twiki/pub/TWiki/PatternSkin/TWiki\\\_header.gif);
background-repeat:no-repeat;} .patternBookView { border-color:#99FF99; }
.patternPreviewPage #patternMain { /\\\* uncomment to set the preview
image \\\*/
/\\\*background-image:url(\"/twiki/pub/TWiki/PreviewBackground/preview2bg.gif\");\\\*/
} \@import url(\"/twiki/pub/TWiki/PatternSkin/print.css\");
.twikiMakeVisible{display:inline;}.twikiMakeVisibleInline{display:inline;}.twikiMakeVisibleBlock{display:block;}.twikiMakeHidden{display:none;}
// inspired by
www.dhtmlgoodies.com/index.html?whichScript=scrolling\\\_content var
scrollData = new Array(); function doScrollCanvas( containerID ) { var
vPos = scrollData\\\[containerID\\\]\\\[\'canvasObj\'\\\].style.top; if(
scrollData\\\[containerID\\\]\\\[\'doScroll\'\\\] ) { vPos =
vPos.replace(/\\\[\^\\\\-0-9\\\]/g,\'\') -
scrollData\\\[containerID\\\]\\\[\'verticalStep\'\\\]; if( vPos/1 +
scrollData\\\[containerID\\\]\\\[\'canvasHeight\'\\\]/1 \< 1 ) { vPos =
0 }; scrollData\\\[containerID\\\]\\\[\'canvasObj\'\\\].style.top =
vPos + \'px\'; } setTimeout(\'doScrollCanvas(\"\' + containerID +
\'\")\', scrollData\\\[containerID\\\]\\\[\'delay\'\\\]); } function
doStopScroll() { var containerID = this.id;
scrollData\\\[containerID\\\]\\\[\'doScroll\'\\\] = false; } function
doStartScroll() { var containerID = this.id;
scrollData\\\[containerID\\\]\\\[\'doScroll\'\\\] = true; } function
initScrollBox( containerID, delay, vstep, width, height ) { var
scrollContainer = document.getElementById( containerID ); var
scrollCanvas = scrollContainer.getElementsByTagName( \'DIV\' )\\\[0\\\];
if( ! delay ) { delay = 1000; } if( ! vstep ) { vstep =
scrollContainer.clientHeight; } if( width ) {
scrollContainer.parentNode.style.width = width + \'px\'; } if( height )
{ scrollContainer.style.height = height + \'px\'; }
scrollContainer.onmouseover = doStopScroll; scrollContainer.onmouseout =
doStartScroll; scrollData\\\[containerID\\\] = new Array();
scrollData\\\[containerID\\\]\\\[\'canvasObj\'\\\] = scrollCanvas;
scrollData\\\[containerID\\\]\\\[\'canvasHeight\'\\\] =
scrollCanvas.offsetHeight;
scrollData\\\[containerID\\\]\\\[\'verticalStep\'\\\] = vstep;
scrollData\\\[containerID\\\]\\\[\'delay\'\\\] = delay;
scrollData\\\[containerID\\\]\\\[\'doScroll\'\\\] = true;
scrollCanvas.style.top =
scrollData\\\[containerID\\\]\\\[\'verticalStep\'\\\] + \'px\';
doScrollCanvas( containerID ); } .scrollBoxOuter { border: solid #d0d0d0
1px; -moz-box-shadow: 2px 2px 3px #e8e8e8; -webkit-box-shadow: 2px 2px
3px #e8e8e8; box-shadow: 2px 2px 3px #e8e8e8; -moz-border-radius: 4px;
border-radius: 4px; width: 300px; padding: 15px; background-image:
url(/twiki/pub/TWiki/ScrollBoxAddOn/gradient-title.png);
background-repeat: repeat-x; background-color: #ffffff; }
.scrollBoxTitle { text-align:center; font-size:19px; font-weight:bold;
color: #333335; margin: -5px 0 0 0; padding: 0 0 12px 0; white-space:
nowrap; overflow: hidden; } .scrollBoxTitle a:link, .scrollBoxTitle
a:visited { color: #333335; } .scrollBoxContainer { overflow: hidden;
height: 40px; padding: 0px; position: relative; } .scrollBoxContent {
position: relative; top: 0px; padding: 0px; text-align: justify; }
.scrollBoxContent img { padding: 0px; vertical-align: middle; }
.tableSortIcon img {padding-left:.3em; vertical-align:text-bottom;}
.twikiTable#twikiAttachmentsTable td {border-style:solid none;}
.twikiTable#twikiAttachmentsTable th {border-style:solid none;}
.twikiTable#twikiAttachmentsTable td {vertical-align:middle;}
.twikiTable#twikiAttachmentsTable th {vertical-align:middle;}
.twikiTable#twikiAttachmentsTable td {vertical-align:top;}
.twikiTable#twikiAttachmentsTable th {background-color:#ffffff;}
.twikiTable#twikiAttachmentsTable th.twikiSortedCol
{background-color:#eeeeee;} .twikiTable#twikiAttachmentsTable th
{color:#0066cc;} .twikiTable#twikiAttachmentsTable th a:link
{color:#0066cc;} .twikiTable#twikiAttachmentsTable th a:visited
{color:#0066cc;} .twikiTable#twikiAttachmentsTable th a:link font
{color:#0066cc;} .twikiTable#twikiAttachmentsTable th a:visited font
{color:#0066cc;} .twikiTable#twikiAttachmentsTable th a:hover
{color:#ffffff;background-color:#0066cc;}
.twikiTable#twikiAttachmentsTable th a:hover font
{color:#ffffff;background-color:#0066cc;}
.twikiTable#twikiAttachmentsTable tr.twikiTableRowdataBg0 td
{background-color:#ffffff;} .twikiTable#twikiAttachmentsTable
tr.twikiTableRowdataBg0 td.twikiSortedCol {background-color:#f5f5f5;}
.twikiTable#twikiAttachmentsTable td.twikiTableCol0 {text-align:center;}
.twikiTable#twikiAttachmentsTable td.twikiTableCol1 {text-align:left;}
.twikiTable#twikiAttachmentsTable td.twikiTableCol2 {text-align:left;}
.twikiTable#twikiAttachmentsTable td.twikiTableCol3 {text-align:right;}
.twikiTable#twikiAttachmentsTable td.twikiTableCol4 {text-align:left;}
.twikiTable#twikiAttachmentsTable td.twikiTableCol5 {text-align:left;}
.twikiTable#twikiAttachmentsTable td.twikiTableCol6 {text-align:left;}
.twikiTable#twikiAttachmentsTable td.twikiTableCol7 {text-align:left;}
\@import
url(\"https://twiki.cern.ch/twiki/pub/TWiki/TwistyContrib/twist.css\");
// \<!\\\[CDATA\\\[ var styleText = \'\<style type=\"text/css\"
media=\"all\"\>.twikiMakeVisible{display:inline;}.twikiMakeVisibleInline{display:inline;}.twikiMakeVisibleBlock{display:block;}.twikiMakeHidden{display:none;}\</style\>\';
document.write(styleText); // \\\]\\\]\>
.twikiMakeVisible{display:inline;}.twikiMakeVisibleInline{display:inline;}.twikiMakeVisibleBlock{display:block;}.twikiMakeHidden{display:none;}
.twDashboardOuter { margin: 0; padding: 0; width: 1040px; /\\\* = 1024 +
2\\\*7 margin + 2 extra \\\*/ } .twDashboardOuter div div div ul {
padding-left: 1.7em; } .twDashboardBanner { position: relative; margin:
7px; padding: 0; width: 1024px; /\\\* = 3 \\\* (300w+2\\\*15p+2\\\*1b) +
2\\\*2\\\*7m \\\*/ height: 150px; -moz-box-shadow: 2px 2px 3px #e8e8e8;
-webkit-box-shadow: 2px 2px 3px #e8e8e8; box-shadow: 2px 2px 3px
#e8e8e8; -moz-border-radius: 4px; border-radius: 4px; background-color:
#dddddd; background-image:
url(/twiki/pub/TWiki/TWikiDashboardImages/golden-gate-sunset.jpg); }
.twDashboardBannerTitle { position: absolute; margin: 10px 15px;
padding: 0; font-size: 18pt; font-weight: 600; color: #333333; }
.twDashboardBannerButtonRow { position: absolute; bottom: 0; right: 0;
margin: 0; padding: 10px 10px; color: #333333; }
.twDashboardBannerButton { float:right; } .twDashboardBannerButton a {
display: inline-block; margin: 5px 10px; padding: 3px 8px; } .ui-dialog
.ui-dialog-content { text-align: left; } .twDashboardBox { float: left;
padding: 7px; }

\[TWiki\](https://twiki.cern.ch/twiki/bin/view/Main/WebHome)\\\>\![\](./LHCbUpgradeII
\_ LHCb \_ TWiki_files/web-bg-small.gif) \[LHCb
Web\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebHome)\\\>\[LHCbUpgradeII\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII
\"Topic revision: 81 (2025-10-31 - 17:19:44)\") (2025-10-31,
\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon))
\[\![\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/uweb-o14.gif)
Edit\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbUpgradeII?t=1762217581;nowysiwyg=1
\"Edit this topic
text\")\[Attach\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII
\"Attach an image or document to this
topic\")\[PDF\](https://twiki.cern.ch/twiki/bin/genpdf/LHCb/LHCbUpgradeII
\"Create a PDF file for the topic\")

The LHCb Upgrade II ===================

\* \[LHCb Upgrade II
Organisation\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#LHCb_Upgrade_II_Organisation)
\* \[Main documents and approval steps for Upgrade
II\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#Main_documents_and_approval_step)
\* \[LHCb Upgrade II
Workshops\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#LHCb_Upgrade_II_Workshops)
\* \[Upgrade II presentations in front of the RRB and
SPC\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#Upgrade_II_presentations_in_fron)
\* \[Luminosity and detector
figures\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#Luminosity_and_detector_figures)
\* \[LS3
Enhancements\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#LS3_Enhancements)
\* \[U2PG and related
meetings\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#U2PG_and_related_meetings)
\* \[LHCb Upgrade II Project
webpages\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#LHCb_Upgrade_II_Project_webpages)

LHCb Upgrade II Organisation
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

Upgrade 2 Planning Group (UPG)

\_This committee oversees the preparation activities of Upgrade II,
which is planned for LS4, and the review of proposals for LS3 detector
enhancements\_

\*\*Membership:\*\* (as of October 2025)

\* Chair: Tim Gershon, Giovanni Punzi \* U2RB chair: Hassan Jawahery \*
Spokesperson and deputies: Vincenzo Vagnoni, Uli Uwer, Patrick Robbe \*
Oversight of Accelerator and Technical Coordination: Eric Thomas \*
Oversight of Sustainability: Heinrich Schindler \* Software and
Computing Coordination: Ben Couturier \* Oversight of Physics and
Performance: Fred Blanc, Phoebe Hamilton, Renato Quagliani \* Oversight
of Tracking Detectors: Matt Needham, Marina Artuso, Abraham Gallas, Mara
Senghi Soares \* Oversight of Particle Identification Detectors: Guy
Wilkinson, Roberta Cardinale, Zhenwei Yang \* Oversight of Data
Processing; Renaud Le Gac, Conor Fitzpatrick, Federico Alessio \*
Oversight of Electronics: Ken Wyllie, Sophie Baron

Project responsibilities on U2

\_All PLs and deputies are listed in this table, with the specific
responsibilities on Upgrade II indicated, as they have been approved by
the CB\_

\* VELO: PL Victor Coco, deputies David Friday, Kazu Akiba (U2) \* UT:
PL Jianchun Wang, deputy Tomasz Skwarnicki, Benjamin Audurier (U2) \*
RICH: PL Silvia Gambetta, deputies Chris Jones, Claudio Gotti; upgrade
coordinators Antonis Papanestis (U2), Carmelo D\'Ambrosio (U1b) \*
SciFi: PL Pascal Perret, deputy Blake Leverington, U2 coordinator Matt
Needham \* CALO: PL Frederic Machefert, deputies Yuri Guz, Philipp
Roloff (U2) \* Muon: PL Barbara Sciascia, deputies Marco Santimaria,
Alessia Satta (U2) \* Online: PL Niko Neufeld, deputies Clara Gaspar,
Renaud Le Gac, Tommaso Colombo (U2) \* RTA: Michel de Cian, deputy
Marianna Fontana (U2) \* Simulation: PL Mark Whitehead, deputies Gloria
Corti, Michal Kreps (U2) \* DPA: PL Nicole Skidmore, deputies Chris Burr
\* Computing: PL Jan Van Eldik, deputy Federico Stagni \* TORCH R&D: Tom
Blake, deputy Jochen Schwiening \* Magnet Stations R&D: Cesar Luiz Da
Silva, deputy Marcin Chrzaszcz

Main documents and approval steps for Upgrade II
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\*\*Expression of Interest (EoI) 2017\*\*

\* The LHCb Upgrade II EoI was submitted to the LHCC in February 2017.
\* Feedback was received in the LHCC \[Minutes Feb
2017\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2253239/files/LHCC-129.pdf)
\* The EoI is available on CDS:
\[CERN-LHCC-2017-003\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/2244311?ln=en)

\*\*Accelerator Study 2018\*\*

\* The feasibility of an LHCb Upgrade II at the HL-LHC is studied in an
accelerator group note \[CERN-ACC-NOTE-2018-0038\![\](./LHCbUpgradeII \_
LHCb \_
TWiki_files/external-link.gif)\](http://cds.cern.ch/record/2319258?ln=en)
\* Recommendations from the U2PG on the preferred operating conditions
and luminosity in response to the accelerator note are given in
\[CERN-LHCb-PUB-2019-001\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/2653011?ln=en)

\*\*Physics Case 2018\*\*

\* The LHCb Upgrade II Physics Case document was submitted to the LHCC
in August 2018. \* Feedback was received in the LHCC \[Minutes Sept
2018\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2642266/files/LHCC-135.pdf)
\* The Physics Case document is available on CDS:
\[CERN-LHCC-2018-027\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/2636441?ln=en)

\*\*Framework Technical Design Report (FTDR) 2021\*\*

\* The LHCb Upgrade II FTDR was submitted to the LHCC in September 2021.
\* Feedback was received from the LHCC in March 2022 meeting:
\[slides\\\_LHCb.pdf\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709884/LHCb_upgrade2_LHCC_march2022_v4.pdf),
\[slides\\\_LHCb.pptx\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709880/LHCb_upgrade2_LHCC_march2022_v4.pptx),
\[LHCC recommendations\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1134643/attachments/2711962/4709351/LHCC149%20minutes%20draft%20extract.pdf)
\* The FTDR is available on CDS:
\[CERN-LHCC-2023-002\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2776420/files/LHCB-TDR-023.pdf)

\*\*Scoping Document 2024\*\*

\* To get to the TDR stage, LHCb collaboration is requested by LHCC and
CERN management to produce a Scoping Document, illustrating scoping
scenarios for the Upgrade II detector, with their expected physics
performance and cost. The complete approval process is discussed in the
LHCC document available at this \[link\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4710803/LHCC-G-184.pdf)
\* The main guidelines for Scoping Document discussed in the U2PG as of
June 2023 are summarised in a short document available at this
\[link\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1291591/contributions/5432822/attachments/2665902/4619674/Towards%20Scoping%20Document.pdf),
available informations from the subdetectors, as of September 2023, are
summarised in \[this\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4710866/Detector%20Scenarios%20for%20Upgrade%20II(4).pdf)
document. These notes on scoping scenarios are not meant for
distribution outside the collaboration or to be used in public
presentations \* The plan is to deliver the Scoping Document to the LHCC
on 2 September 2024, 1st circulation draft is available here
\[indico\\\_link\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1442564/)
\* The version submitted to the LHCC (2 September 2024) is available
\[here\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cernbox.cern.ch/index.php/s/O2biQWwDYqVIcYt).
This is not yet a public document but figures and tables, except those
relating to costs and national/institutional commitments, can be shown
in public talks. \* A first set of comments was received from the LHCC
on 18 November 2024:
\[pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCb_SD_Questions_Selections_20241118.pdf)
and
\[docx\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCb_SD_Questions_Selections_20241118.docx)
\* \[LHCC focus session (19 November 2024)\![\](./LHCbUpgradeII \_ LHCb
\_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1476161/)
to present the Scoping Document and discuss these comments and others \*
A complete (?) set of comments from the LHCC was received on 13 December
2024:
\[pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCC-LHCb-Questions.pdf)
and
\[docx\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCC-LHCb-Questions.docx)
\* Draft responses as of 22 January 2025:
\[pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCC-LHCb-Questions-responses22Jan.pdf)
\* \[Meeting with LHCC referees (24 January 2025)\![\](./LHCbUpgradeII
\_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1502158/)
\* Documents submitted to LHCC referees 17 February 2025: \[Updated
version of Scoping
Document\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCb_Upgrade_II_Scoping_Document-17Feb.pdf),
\[Complete set of responses to LHCC
questions\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCC-LHCb-Questions-responses17Feb.pdf)
\* \[Meeting with LHCC referees (4 March 2025)\![\](./LHCbUpgradeII \_
LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1511426/)
\* The LHCC green light to finalise the Scoping Document came on 14
March 2025: The final version is available on CDS: \[CERN-LHCC-2024-010
; LHCB-TDR-026\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2903094), or
\[Final version (no
cover)\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCb_Upgrade_II_Scoping_Document-final-noCover.pdf)

\*\*Submissions to the \[European Strategy for Particle Physics Update
2024-26\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://europeanstrategyupdate.web.cern.ch/welcome)\*\*

\* \[LHCB-PUB-2025-001\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2920833?ln=en),
\"Discovery potential of LHCb Upgrade II\",
\[arXiv:2503.23087\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://arxiv.org/abs/2503.23087) \*
\[LHCB-PUB-2025-002\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2920835?ln=en),
\"Technology developments for LHCb Upgrade II\",
\[arXiv:2504.03088\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://arxiv.org/abs/2504.03088) \*
\[LHCB-PUB-2025-003\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2920836?ln=en),
\"Heavy ion physics at LHCb Upgrade II\",
\[arXiv:2503.23093\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://arxiv.org/abs/2503.23093) \*
\[LHCB-PUB-2025-004\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2920838?ln=en),
\" Computing and software for LHCb Upgrade II\",
\[arXiv:2503.24106\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://arxiv.org/abs/2503.24106) \*
\[LHCB-PUB-2025-008\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2927944?ln=en),
\"Projections for Key Measurements in Heavy Flavour Physics\" together
with the ATLAS, CMS and Belle II collaborations,
\[arXiv:2503.24346\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://arxiv.org/abs/2503.24346).
Plots summarising the tabulated data from these submissions are
available from \[CDS\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2927944/files/)
(many thanks to Abhijit Mathad).

LHCb Upgrade II Workshops
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* 9th Workshop, 11-13 March 2026, LLR, Paris \* 8th Workshop 26-28
March 2025, \[Heidelberg\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1491351/)
\* 7th Workshop 25-27 March 2024, \[CERN\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1377881/)
\* Tracking Workshop 6-7 March 2024
\[Evian-Les-Bains\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1342873/overview)
\* 6th Workshop \[Barcelona 2023\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.icc.ub.edu/event/163/)
\* Virtual Workshop \[Zoomland 2021\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/)
\* 5th Workshop \[Barcelona 2020\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.icc.ub.edu/event/48/)
(virtual only) \* 4th Workshop \[Amsterdam 2019\![\](./LHCbUpgradeII \_
LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/790856/)
\* 3rd Workshop \[Annecy 2018\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.in2p3.fr/event/16795/)
\* 2nd Workshop \[Elba 2017\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://agenda.infn.it/conferenceDisplay.py?confId=12253)
\* 1st Workshop \"Theatre of Dreams\" \[Manchester
2016\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](http://www.hep.manchester.ac.uk/theatre-of-dreams/index.html)

Upgrade II presentations in front of the RRB and SPC
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

Links to presentations given in front of the Resource Review Board
(panel composed by CERN management, LHCb management and the
representatives of the Funding Agencies) and the Scientific Policy
Committee, the body preparing recommendations for the Council on CERN
scientific policy. This material can be used in public presentations.

\* Status report at LHCb RRB meeting, October 2025
\[slides.pdf\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1562013/contributions/6580241/attachments/3162184/5618766/gershon-RRB-28Oct2025.pdf)
(CERN-RRB-2025-114) \* Status report at LHCb RRB meeting, April 2025
\[slides.pdf\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1523284/contributions/6411037/attachments/3057976/5407133/gershon-RRB-29Apr2025.pdf)
(CERN-RRB-2025-035) \* 6th dedicated RRB meeting on LHCb Upgrade II,
October 2024 \[slides.pdf\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1475179/contributions/6212309/attachments/2961081/5208094/gershon-Upgrade2-RRB-30Oct2024.pdf)
(CERN-RRB-2024-118) \* SPC meeting, September 2024
\[slides.pdf\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1460149/contributions/6147801/attachments/2933569/5152205/SPC%2024%20September%202024.pdf)
\* 5th dedicated RRB meeting on LHCb Upgrade II, April 2024
\[physics\\\_case\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1397598/attachments/2831295/4976328/gershon-Upgrade2-RRB-24April2024(1).pdf),
\[detector\\\_scenarios\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1397598/attachments/2831295/4976327/LHCb_phase2b_RRB\_\_24apr2024(5).pdf)
\* SPC meeting, December 2023 \[slides.pdf\![\](./LHCbUpgradeII \_ LHCb
\_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1345994/attachments/2758517/4838077/Vincenzo_SPC_v1.pdf)
\* 4th dedicated RRB meeting on LHCb Upgrade II, October 2023
\[slides.pdf\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1334351/attachments/2736802/4769223/LHCb_upgrade2_RRB_october2023.pdf),
\[slides.pptx\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1334351/attachments/2736802/4769227/LHCb_upgrade2_RRB_october2023.pptx)
\* 3rd dedicated RRB meeting on LHCb Upgrade II, April 2023
\[slides.pdf\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709583/CERN-RRB-2023-052.pdf),
\[slides.pptx\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709584/LHCb_upgrade2_RRB_april2023.pptx),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709582/minutes_CERN-RRB-2023-060_LHCb_PhII-APR2023-skeleton.pdf)
\* 2nd dedicated RRB meeting on LHCb Upgrade II, October 2022
\[slides.pdf\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709640/LHCb_upgrade2_RRB_october2022.pdf),
\[slides.pptx\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709641/LHCb_upgrade2_RRB_october2022.pptx),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709642/CERN-RRB-2022-123.pdf)
\* 1st dedicated RRB meeting on LHCb Upgrade II, June 2022
\[slides.pdf\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709834/LHCbU2_RRB_240622.pdf),
\[slides.pptx\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709835/LHCbU2_RRB_240622.pptx),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4709833/CERN-RRB-2022-060.pdf)

Luminosity and detector figures
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

At the links below, the expected LHCb luminosity profile and the
detector overview are avaialble

\* Integrated (recorded) luminosity: \* Plot assuming peak luminosity of
1.5 10\^34/cm2/s
\[lumi\\\_15.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/lumi_15.pdf)
\-- this is the current default to be shown in conferences \* Plot
assuming peak luminosity of 1.0 10\^34/cm2/s
\[lumi\\\_10.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/lumi_10.pdf)
\* Spreadsheet for the calculation
\[lumi-projection-2024.ods\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/lumi-projection-2024.ods)
\* Version with old LHC schedule, assuming peak luminosity of 1.5
10\^34/cm2/s \[plot\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1434005/attachments/2905877/5097413/lumiplot.pdf)
and corresponding numbers \[table\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1434005/attachments/2905877/5097440/lumi_table.pdf)
\* Detector, y-view: \[col,
pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/y-LHCb-upgrade-II-LS4_v1.pdf)
(updated March 2025, thanks to Heinrich Schindler)

LS3 Enhancements \-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* U2PG review on RICH enhancement of March 22 2023, agenda at \[this
link\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1260711/),
Q&A available \[here\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4710668/Questions%20and%20requests%20arising%20from%20RICH%20LS3%20Enhancement%20Review_QA_11.pdf)
and final report \[here\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1025939/attachments/2712101/4710669/RICH_LS3_report_v2.pdf)
\* U2PG review on ECAL enhancement of May 3-4 2023, including Q&A,
available at \[this link\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1267345/)
\* TDR for RICH and ECAL LS3 enhacements has been presented to the LHCC
on September 11 2023 (meeting \[link\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1318297/)),
and it has been finally approved on March 6 2024, the final document is
available \[here\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/2866493/files/LHCB-TDR-024.pdf)
\* TDR for Data Acquisition LS3 enhacements has been presented to the
LHCC on 27 February 2023 (meeting \[link\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1385837/)),
the TDR version submitted for review is available
\[here\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1369345/attachments/2805753/4895834/TDR_daq_enhancement_final_240212.pdf)

U2PG and related meetings
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

For quick reference, a list of the U2PG meetings as from July 2022 with
links to the agenda pages is given.

\* 10 September 2025, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb
\_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1540880/)
\* 13 August 2025, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1540879/)
\* 16 July 2025, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1540878/)
\* 11 June 2025, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1540877/)
\* 14 May 2025, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1540876/)
\* 9 April 2025, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1500768/)
\* 12 March 2025, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1500767/)
\* 12 February 2025, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb
\_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1500765/)
\* 20 January 2025, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb
\_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1500764/)
\* 12 December 2024, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb
\_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1470623/)
\* 14 November 2024, U2PG meeting \[agenda\![\](./LHCbUpgradeII \_ LHCb
\_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1470622/)
\* 10 October 2024, U2PG meeting preparing next steps
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1457546/)
\* 17 July 2024, U2PG wrap-up meeting on Scoping Document
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1434005/)
\* 14 June 2024, U2PG on RICH/TORCH integration
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1425761/)
\* 29 May 2024, U2PG 2nd wrap-up meeting on performance studies for
scoping document \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1415659/)
\* 23 May 2024, U2PG 1st wrap-up meeting on performance studies for
scoping document \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1417941/)
\* 21 May 2024, U2PG discussion on polarised target
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1416068/)
\* 3 May 2024, U2PG debriefing of RRB and Scoping Document finalisation
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1408684/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1408684/attachments/2849733/4984099/matteo_minutes_U2PG_3may.pdf)
\* 3 April 2024, U2PG debriefing of U2 workshop
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1397598/),
minutes available at the meeting page \* 20 March 2024, Discussion on
detector scenarios \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1391215/),
minutes available at the meeting page \* 15 March 2024, U2PG on RTA and
online aspects \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1393767/)
\* 12 March 2024, Discussion on detector space envelopes
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1388031/)
\* 11 March 2024, U2PG on PID detectors \[agenda\![\](./LHCbUpgradeII \_
LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1387820/)
\* 1 March 2024, U2PG on benchmark physics studies
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1378464/)
\* 15 February 2024, technical discussion on detector space envelopes
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1359647/)
\* 7 February 2024, U2PG with PLs to monitor progress on sub-detector
studies \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1369345/)
\* 5 February 2024, U2PG on PID detectors \[agenda\![\](./LHCbUpgradeII
\_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1326872/)
\* 1 February 2024, U2PG on tracking detectors
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1359245/)
\* 21 December 2023, U2PG on benchmark physics studies
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1351552/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1351552/attachments/2778663/4842933/Phys%20discussion%20dec%2021.pdf)
\* 20 December 2023, wrap-up discussion with PLs on organisation and
scoping scenarios \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1351551/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1351551/attachments/2775627/4837085/notes-U2PG-20Dec2023.pdf)
\* 14 December 2023, focus on tracking detectors
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1351555/),
minutes available at the meeting page \* 23 November 2023, focus on
benchmark physics channels \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1345994/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1345994/)
\* 16 November 2023, focus on scoping scenarios for tracking detectors
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1341437/)
\* 15 November 2023, focus on heavy Ion physics
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1345634/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1345634/attachments/2754205/4795157/minutes_U2PG_15nov.pdf)
\* 14 November 2023, focus on scoping scenarios for PID detectors
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1345334/)
\* 26 October 2023, focus on scoping scenarios for tracking detectors
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1337708/?note=254265),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1337708/?note=254265)
\* 18 October 2023, focus on organisation for Scoping Document and
lunminosity scenarios \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1334351/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1334351/attachments/2736802/4760442/notes-U2PG-18Oct2023.pdf)
\* 5 October 2023, focus on scoping scenarios for tracking detectors
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1332892/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1332892/#)
\* 5 October 2023, focus on scoping scenarios for PID detectors
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1326872/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1326872/attachments/2731117/4747848/Minutes%20-%20U2PG%20PID%20detectors.pdf)
\* 5-6 September 2023, focus on machine studies and scoping scenarios
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1319415/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1319415/attachments/2705731/4715169/U2PG_combo_v2.rtf)
\* 24 August 2023, sub-systems roundtable on simulation for Scoping
Document \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1315660/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1315660/attachments/2700783/4697370/U2PG_24082023.rtf)
\* 20 July 2023, sub-systems roundtable on simulation for Scoping
Document \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1308598/),
\[minutes\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1315660/attachments/2700783/4687771/u2pg_minutes.pdf)
\* 15 June 2023, focus on Magnet Stations and long-term operation of
LHCb magnet \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1295775/)
\* 11 May 2023, focus on simulation plans \[agenda\![\](./LHCbUpgradeII
\_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1283685/)
\* 9 March 2023, focus on Upgrade II workshop
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1254306/)
\* 23 February 2023, discussion on HCAL at Run4/5
\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1245669/)
\* 14 December 2022, \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1231381/)
\* 9 November 2022, \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1219601/)
\* 12 October 2022, \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1209922/)
\* 21 September 2022, \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1202504/)
\* 31 August 2022, \[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1186010/)
\* 6 July 2022, \[\\\[agenda\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/1173786/)

LHCb Upgrade II Project webpages
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* \[U2 VELO\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/external-link.gif)\](https://lbtwiki.cern.ch/bin/view/VELO/VELOUpgradeII)
\* \[U2 Tracking\](https://twiki.cern.ch/twiki/bin/view/LHCb/U2Tracking)
\* \[U2 Mighty
Tracker\](https://twiki.cern.ch/twiki/bin/view/LHCb/MightyTracker) \*
\[U2 ECAL\](https://twiki.cern.ch/twiki/bin/view/LHCb/PicoCal) \* \[U2
UT\](https://twiki.cern.ch/twiki/bin/view/LHCb/U2UT) \*
\[Testbeam\](https://twiki.cern.ch/twiki/bin/view/LHCb/Testbeam)

\\\-- Main.Matteo Palutan - 2023-09-13

\[\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/toggleopen.gif)Attachments\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#)
\[\![\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/toggleclose.gif)Attachments\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#)

Topic attachments

\[I\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?sortcol=0;table=1;up=0#sorted_table
\"Sort by this column\")

\[Attachment\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?sortcol=1;table=1;up=0#sorted_table
\"Sort by this column\")

\[History\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?sortcol=2;table=1;up=0#sorted_table
\"Sort by this column\")

\[Action\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?sortcol=3;table=1;up=0#sorted_table
\"Sort by this column\")

\[Size\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?sortcol=4;table=1;up=0#sorted_table
\"Sort by this column\")

\[Date\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?sortcol=5;table=1;up=0#sorted_table
\"Sort by this column\")

\[Who\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?sortcol=6;table=1;up=0#sorted_table
\"Sort by this column\")

\[Comment\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?sortcol=7;table=1;up=0#sorted_table
\"Sort by this column\")

\![PDF\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LHCC-LHCb-Questions-responses17Feb.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCC-LHCb-Questions-responses17Feb.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=LHCC-LHCb-Questions-responses17Feb.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

583.9 K

2025-02-19 - 13:20

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

Feb 17 responses to LHCC questions on the Scoping Document

\![PDF\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LHCC-LHCb-Questions-responses22Jan.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCC-LHCb-Questions-responses22Jan.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=LHCC-LHCb-Questions-responses22Jan.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

533.1 K

2025-01-22 - 18:23

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

Jan 22 draft of responses to LHCC questions on the Scoping Document

\![Unknown file format\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/else.gif
\"Unknown file format\")docx

\[LHCC-LHCb-Questions.docx\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCC-LHCb-Questions.docx)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=LHCC-LHCb-Questions.docx;revInfo=1
\"change, update, previous revisions, move, delete\...\")

18.3 K

2025-01-03 - 16:39

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

Complete set of LHCC questions on the Scoping Document

\![PDF\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LHCC-LHCb-Questions.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCC-LHCb-Questions.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=LHCC-LHCb-Questions.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

48.6 K

2025-01-03 - 16:39

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

Complete set of LHCC questions on the Scoping Document

\![Unknown file format\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/else.gif
\"Unknown file format\")docx

\[LHCb\\\_SD\\\_Questions\\\_Selections\\\_20241118.docx\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCb_SD_Questions_Selections_20241118.docx)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=LHCb_SD_Questions_Selections_20241118.docx;revInfo=1
\"change, update, previous revisions, move, delete\...\")

13.3 K

2024-11-26 - 12:11

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

First set of LHCC questions on the Scoping Document

\![PDF\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LHCb\\\_SD\\\_Questions\\\_Selections\\\_20241118.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCb_SD_Questions_Selections_20241118.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=LHCb_SD_Questions_Selections_20241118.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

57.1 K

2024-11-26 - 12:11

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

First set of LHCC questions on the Scoping Document

\![PDF\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LHCb\\\_Upgrade\\\_II\\\_Scoping\\\_Document-17Feb.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCb_Upgrade_II_Scoping_Document-17Feb.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=LHCb_Upgrade_II_Scoping_Document-17Feb.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

68468.9 K

2025-02-19 - 13:20

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

Updated version of the Scoping Document (17 Feb 2025)

\![PDF\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LHCb\\\_Upgrade\\\_II\\\_Scoping\\\_Document-final-noCover.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/LHCb_Upgrade_II_Scoping_Document-final-noCover.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=LHCb_Upgrade_II_Scoping_Document-final-noCover.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

24893.0 K

2025-03-17 - 12:28

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

Final version of scoping document (without cover)

\![Unknown file format\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/else.gif
\"Unknown file format\")ods

\[lumi-projection-2024.ods\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/lumi-projection-2024.ods)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=lumi-projection-2024.ods;revInfo=1
\"change, update, previous revisions, move, delete\...\")

26.8 K

2025-02-10 - 17:59

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

Projection for integrated (recorded) luminosity

\![PDF\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[lumi\\\_10.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/lumi_10.pdf)

r2
\[r1\](https://twiki.cern.ch/twiki/bin/viewfile/LHCb/LHCbUpgradeII?filename=lumi_10.pdf;rev=1)

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=lumi_10.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

14.7 K

2025-02-10 - 18:57

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

Projection for integrated (recorded) luminosity

\![PDF\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[lumi\\\_15.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/lumi_15.pdf)

r2
\[r1\](https://twiki.cern.ch/twiki/bin/viewfile/LHCb/LHCbUpgradeII?filename=lumi_15.pdf;rev=1)

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=lumi_15.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

14.7 K

2025-02-10 - 18:57

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

Projection for integrated (recorded) luminosity

\![PDF\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[y-LHCb-upgrade-II-LS4\\\_v1.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgradeII/y-LHCb-upgrade-II-LS4_v1.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII?filename=y-LHCb-upgrade-II-LS4_v1.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

208.9 K

2025-03-21 - 12:42

\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

LHCb Upgrade 2 detector (y view)

\[\![\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/uweb-o14.gif)
Edit\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbUpgradeII?t=1762217582;nowysiwyg=1
\"Edit this topic
text\") \| \[Attach\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgradeII
\"Attach an image or document to this topic\") \| \[Print
version\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?cover=print
\"Printable version of this
topic\") \| \[History\](https://twiki.cern.ch/twiki/bin/oops/LHCb/LHCbUpgradeII?template=oopshistory
\"View total topic history\"):
r81 \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbUpgradeII?rev1=81;rev2=80) \[r80\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?rev=80) \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbUpgradeII?rev1=80;rev2=79) \[r79\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?rev=79) \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbUpgradeII?rev1=79;rev2=78) \[r78\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?rev=78) \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbUpgradeII?rev1=78;rev2=77) \[r77\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?rev=77) \| \[Backlinks\](https://twiki.cern.ch/twiki/bin/oops/LHCb/LHCbUpgradeII?template=backlinksweb
\"Search the LHCb Web for topics that link to here\") \| \[Raw
View\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?raw=on
\"View raw text without
formatting\") \| \[WYSIWYG\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbUpgradeII?t=1762217582;nowysiwyg=0
\"WYSIWYG editor\") \| \[More topic
actions\](https://twiki.cern.ch/twiki/bin/oops/LHCb/LHCbUpgradeII?template=oopsmore&param1=81&param2=81
\"Delete or rename this topic; set parent topic; view and compare
revisions\")

Topic revision: r81 - 2025-10-31
\[\\-\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbUpgradeII?t=1762217582;nowysiwyg=1)
\[TimGershon\](https://twiki.cern.ch/twiki/bin/view/Main/TimGershon)

\![\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/person.gif)
\[YagnaSwaroopDhurbhakula\](https://twiki.cern.ch/twiki/bin/edit/Main/YagnaSwaroopDhurbhakula?topicparent=LHCb.LHCbUpgradeII;nowysiwyg=1
\"this topic does not yet exist; you can create it.\")
\![Lock\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/lock.gif \"Lock\")
\[Log
Out\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII?logout=1)

\* \[\![Web background\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/web-bg-small.gif \"Web background\")
LHCb\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebHome)

\* \*\*LHCb Web\*\* \* \[LHCb Web
Home\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebHome) \*
\[Changes\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebChanges) \*
\[Index\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebIndex) \*
\[Search\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebSearch)

\* \* \*

\* \*\*LHCb webs\*\* \*
\[LHCbComputing\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbComputing)
\* \[LHCb FAQs\](https://twiki.cern.ch/twiki/bin/view/LHCb/FAQ/WebHome)
\* \[LHCbOnline\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbOnline)
\*
\[LHCbPhysics\](https://twiki.cern.ch/twiki/bin/view/LHCbPhysics/LHCbPhysics)
\* \[LHCbVELO\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbVELO) \*
\[LHCbST\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbST) \*
\[LHCbOT\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbOT) \*
\[LHCbPlume\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbPlume) \*
\[LHCbRICH\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbRICH) \*
\[LHCbMuon\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbMuon) \*
\[LHCbTrigger\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbTrigger)
\*
\[LHCbDetectorAlignment\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment)
\*
\[LHCbTechnicalCoordination\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbTechnicalCoordination)
\*
\[LHCbUpgrade\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade)

\* \* \*

\[\![\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/toggleopen.gif)Public
webs\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#)
\[\![\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/toggleclose.gif)Public
webs\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgradeII#)

\* \[ABATBEA\](https://twiki.cern.ch/twiki/bin/view/ABATBEA/WebHome) \*
\[ACPP\](https://twiki.cern.ch/twiki/bin/view/ACPP/WebHome) \*
\[ADCgroup\](https://twiki.cern.ch/twiki/bin/view/ADCgroup/WebHome) \*
\[AEGIS\](https://twiki.cern.ch/twiki/bin/view/AEGIS/WebHome) \*
\[AfricaMap\](https://twiki.cern.ch/twiki/bin/view/AfricaMap/WebHome) \*
\[AgileInfrastructure\](https://twiki.cern.ch/twiki/bin/view/AgileInfrastructure/WebHome)
\* \[ALICE\](https://twiki.cern.ch/twiki/bin/view/ALICE/WebHome) \*
\[AliceEbyE\](https://twiki.cern.ch/twiki/bin/edit/AliceEbyE/WebHome?topicparent=LHCb.LHCbUpgradeII;nowysiwyg=1
\"this topic does not yet exist; you can create it.\") \*
\[AliceSPD\](https://twiki.cern.ch/twiki/bin/view/AliceSPD/WebHome) \*
\[AliceSSD\](https://twiki.cern.ch/twiki/bin/view/AliceSSD/WebHome) \*
\[AliceTOF\](https://twiki.cern.ch/twiki/bin/view/AliceTOF/WebHome) \*
\[AliFemto\](https://twiki.cern.ch/twiki/bin/view/AliFemto/WebHome) \*
\[ALPHA\](https://twiki.cern.ch/twiki/bin/view/ALPHA/WebHome) \*
\[Altair\](https://twiki.cern.ch/twiki/bin/view/Altair/WebHome) \*
\[ArdaGrid\](https://twiki.cern.ch/twiki/bin/view/ArdaGrid/WebHome) \*
\[ASACUSA\](https://twiki.cern.ch/twiki/bin/view/ASACUSA/WebHome) \*
\[AthenaFCalTBAna\](https://twiki.cern.ch/twiki/bin/view/AthenaFCalTBAna/WebHome)
\* \[Atlas\](https://twiki.cern.ch/twiki/bin/view/Atlas/WebHome) \*
\[AtlasLBNL\](https://twiki.cern.ch/twiki/bin/view/AtlasLBNL/WebHome) \*
\[AXIALPET\](https://twiki.cern.ch/twiki/bin/view/AXIALPET/WebHome) \*
\[CAE\](https://twiki.cern.ch/twiki/bin/view/CAE/WebHome) \*
\[CALICE\](https://twiki.cern.ch/twiki/bin/view/CALICE/WebHome) \*
\[CDS\](https://twiki.cern.ch/twiki/bin/view/CDS/WebHome) \*
\[CENF\](https://twiki.cern.ch/twiki/bin/view/CENF/WebHome) \*
\[CERNSearch\](https://twiki.cern.ch/twiki/bin/view/CERNSearch/WebHome)
\* \[CLIC\](https://twiki.cern.ch/twiki/bin/view/CLIC/WebHome) \*
\[Cloud\](https://twiki.cern.ch/twiki/bin/view/Cloud/WebHome) \*
\[CloudServices\](https://twiki.cern.ch/twiki/bin/view/CloudServices/WebHome)
\* \[CMS\](https://twiki.cern.ch/twiki/bin/view/CMS/WebHome) \*
\[Controls\](https://twiki.cern.ch/twiki/bin/view/Controls/WebHome) \*
\[CTA\](https://twiki.cern.ch/twiki/bin/view/CTA/WebHome) \*
\[CvmFS\](https://twiki.cern.ch/twiki/bin/view/CvmFS/WebHome) \*
\[DB\](https://twiki.cern.ch/twiki/bin/view/DB/WebHome) \*
\[DefaultWeb\](https://twiki.cern.ch/twiki/bin/view/DefaultWeb/WebHome)
\* \[DESgroup\](https://twiki.cern.ch/twiki/bin/view/DESgroup/WebHome)
\* \[DPHEP\](https://twiki.cern.ch/twiki/bin/view/DPHEP/WebHome) \*
\[DM-LHC\](https://twiki.cern.ch/twiki/bin/view/DMLHC/WebHome) \*
\[DSSGroup\](https://twiki.cern.ch/twiki/bin/view/DSSGroup/WebHome) \*
\[EGEE\](https://twiki.cern.ch/twiki/bin/view/EGEE/WebHome) \*
\[EgeePtf\](https://twiki.cern.ch/twiki/bin/view/EgeePtf/WebHome) \*
\[ELFms\](https://twiki.cern.ch/twiki/bin/view/ELFms/WebHome) \*
\[EMI\](https://twiki.cern.ch/twiki/bin/view/EMI/WebHome) \*
\[ETICS\](https://twiki.cern.ch/twiki/bin/view/ETICS/WebHome) \*
\[FIOgroup\](https://twiki.cern.ch/twiki/bin/view/FIOgroup/WebHome) \*
\[FlukaTeam\](https://twiki.cern.ch/twiki/bin/view/FlukaTeam/WebHome) \*
\[Frontier\](https://twiki.cern.ch/twiki/bin/view/Frontier/WebHome) \*
\[Gaudi\](https://twiki.cern.ch/twiki/bin/view/Gaudi/WebHome) \*
\[GeneratorServices\](https://twiki.cern.ch/twiki/bin/view/GeneratorServices/WebHome)
\*
\[GuidesInfo\](https://twiki.cern.ch/twiki/bin/view/GuidesInfo/WebHome)
\*
\[HardwareLabs\](https://twiki.cern.ch/twiki/bin/view/HardwareLabs/WebHome)
\* \[HCC\](https://twiki.cern.ch/twiki/bin/view/HCC/WebHome) \*
\[HEPIX\](https://twiki.cern.ch/twiki/bin/view/HEPIX/WebHome) \*
\[ILCBDSColl\](https://twiki.cern.ch/twiki/bin/view/ILCBDSColl/WebHome)
\* \[ILCTPC\](https://twiki.cern.ch/twiki/bin/view/ILCTPC/WebHome) \*
\[IMWG\](https://twiki.cern.ch/twiki/bin/view/IMWG/WebHome) \*
\[Inspire\](https://twiki.cern.ch/twiki/bin/view/Inspire/WebHome) \*
\[IPv6\](https://twiki.cern.ch/twiki/bin/view/IPv6/WebHome) \*
\[IT\](https://twiki.cern.ch/twiki/bin/view/IT/WebHome) \*
\[ItCommTeam\](https://twiki.cern.ch/twiki/bin/view/ItCommTeam/WebHome)
\* \[ITCoord\](https://twiki.cern.ch/twiki/bin/view/ITCoord/WebHome) \*
\[ITdeptTechForum\](https://twiki.cern.ch/twiki/bin/view/ITdeptTechForum/WebHome)
\* \[ITDRP\](https://twiki.cern.ch/twiki/bin/view/ITDRP/WebHome) \*
\[ITGT\](https://twiki.cern.ch/twiki/bin/view/ITGT/WebHome) \*
\[ITSDC\](https://twiki.cern.ch/twiki/bin/view/ITSDC/WebHome) \*
\[LAr\](https://twiki.cern.ch/twiki/bin/view/LAr/WebHome) \*
\[LCG\](https://twiki.cern.ch/twiki/bin/view/LCG/WebHome) \*
\[LCGAAWorkbook\](https://twiki.cern.ch/twiki/bin/view/LCGAAWorkbook/WebHome)
\* \[Leade\](https://twiki.cern.ch/twiki/bin/view/Leade/WebHome) \*
\[LHCAccess\](https://twiki.cern.ch/twiki/bin/view/LHCAccess/WebHome) \*
\[LHCAtHome\](https://twiki.cern.ch/twiki/bin/view/LHCAtHome/WebHome) \*
\[LHCb\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebHome) \*
\[LHCgas\](https://twiki.cern.ch/twiki/bin/view/LHCgas/WebHome) \*
\[LHCONE\](https://twiki.cern.ch/twiki/bin/view/LHCONE/WebHome) \*
\[LHCOPN\](https://twiki.cern.ch/twiki/bin/view/LHCOPN/WebHome) \*
\[LinuxSupport\](https://twiki.cern.ch/twiki/bin/view/LinuxSupport/WebHome)
\* \[Main\](https://twiki.cern.ch/twiki/bin/view/Main/WebHome) \*
\[Medipix\](https://twiki.cern.ch/twiki/bin/view/Medipix/WebHome) \*
\[Messaging\](https://twiki.cern.ch/twiki/bin/view/Messaging/WebHome) \*
\[MPGD\](https://twiki.cern.ch/twiki/bin/view/MPGD/WebHome) \*
\[NA49\](https://twiki.cern.ch/twiki/bin/view/NA49/WebHome) \*
\[NA61\](https://twiki.cern.ch/twiki/bin/view/NA61/WebHome) \*
\[NA62\](https://twiki.cern.ch/twiki/bin/view/NA62/WebHome) \*
\[NTOF\](https://twiki.cern.ch/twiki/bin/view/NTOF/WebHome) \*
\[Openlab\](https://twiki.cern.ch/twiki/bin/view/Openlab/WebHome) \*
\[PDBService\](https://twiki.cern.ch/twiki/bin/view/PDBService/WebHome)
\*
\[Persistency\](https://twiki.cern.ch/twiki/bin/view/Persistency/WebHome)
\* \[PESgroup\](https://twiki.cern.ch/twiki/bin/view/PESgroup/WebHome)
\* \[Plugins\](https://twiki.cern.ch/twiki/bin/view/Plugins/WebHome) \*
\[PSAccess\](https://twiki.cern.ch/twiki/bin/view/PSAccess/WebHome) \*
\[PSBUpgrade\](https://twiki.cern.ch/twiki/bin/view/PSBUpgrade/WebHome)
\*
\[R2Eproject\](https://twiki.cern.ch/twiki/bin/view/R2Eproject/WebHome)
\* \[RCTF\](https://twiki.cern.ch/twiki/bin/view/RCTF/WebHome) \*
\[RD42\](https://twiki.cern.ch/twiki/bin/view/RD42/WebHome) \*
\[RFCond12\](https://twiki.cern.ch/twiki/bin/view/RFCond12/WebHome) \*
\[RFLowLevel\](https://twiki.cern.ch/twiki/bin/view/RFLowLevel/WebHome)
\* \[ROXIE\](https://twiki.cern.ch/twiki/bin/view/ROXIE/WebHome) \*
\[Sandbox\](https://twiki.cern.ch/twiki/bin/view/Sandbox/WebHome) \*
\[SocialActivities\](https://twiki.cern.ch/twiki/bin/view/SocialActivities/WebHome)
\* \[SPI\](https://twiki.cern.ch/twiki/bin/view/SPI/WebHome) \*
\[SRMDev\](https://twiki.cern.ch/twiki/bin/view/SRMDev/WebHome) \*
\[SSM\](https://twiki.cern.ch/twiki/bin/view/SSM/WebHome) \*
\[Student\](https://twiki.cern.ch/twiki/bin/view/Student/WebHome) \*
\[SuperComputing\](https://twiki.cern.ch/twiki/bin/view/SuperComputing/WebHome)
\* \[Support\](https://twiki.cern.ch/twiki/bin/view/Support/WebHome) \*
\[SwfCatalogue\](https://twiki.cern.ch/twiki/bin/view/SwfCatalogue/WebHome)
\* \[TMVA\](https://twiki.cern.ch/twiki/bin/view/TMVA/WebHome) \*
\[TOTEM\](https://twiki.cern.ch/twiki/bin/view/TOTEM/WebHome) \*
\[TWiki\](https://twiki.cern.ch/twiki/bin/view/TWiki/WebHome) \*
\[UNOSAT\](https://twiki.cern.ch/twiki/bin/view/UNOSAT/WebHome) \*
\[Virtualization\](https://twiki.cern.ch/twiki/bin/view/Virtualization/WebHome)
\* \[VOBox\](https://twiki.cern.ch/twiki/bin/view/VOBox/WebHome) \*
\[WITCH\](https://twiki.cern.ch/twiki/bin/view/WITCH/WebHome) \*
\[XTCA\](https://twiki.cern.ch/twiki/bin/view/XTCA/WebHome)

\[Create\](https://twiki.cern.ch/twiki/bin/edit/Main/YagnaSwaroopDhurbhakulaLeftBar?templatetopic=TWiki.WebLeftBarPersonalTemplate)
personal sidebar

\[\![CERN\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/logo_lhcb.png)\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebHome)

\*   

\* \* \![TWiki Search Icon\](./LHCbUpgradeII \_ LHCb \_
TWiki_files/twikisearchicon.gif) TWiki Search \* \![Google Search
Icon\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/googlesearchicon.png)
Google Search

LHCb All webs

   

\<!\-- \$(function() { // We use the current web name to form the
redirect in the TWiki search var currentWeb = undefined; // If the web
starts with alice\\\* atlas\\\* cms\\\* or lhcb\\\* (case-insensitive),
// the \"Web search\" should be altered so that AtlasFoo =\> Atlas var
specialWeb = undefined; // Remembering what the user have entered into
the searchbox to after // he has selected a new search engine from the
dropdown var searchPhrase = \'\'; // \-\-- BEGIN: CONFIGURABLE LIST FOR
SUBWEB SEARCH \-\-- // List of webs for which sub-web searching should
be enabled var subWebSearchWebs = \\\[\'AtlasProtected\',
\'AtlasComputing\', \'Atlas\'\\\]; // \-\-- END: CONFIGURABLE LIST FOR
SUBWEB SEARCH \-\-- // \-\-- ORIGINAL WEB DETECTION LOGIC \-\-- // We
want to store the current web for later use. var currentWebSearch =
window.location.pathname.match(/\\\\/(\\\[A-Z\\\]\\\[\^\\\\/\\\]+)/); if
(currentWebSearch != null) { currentWeb = currentWebSearch\\\[1\\\]; //
Do we have a special kind of web? If so, the web search should be
altered a little to fetch more broader results. var specialWebSearch =
currentWeb.match(/\^(alice\|atlas\|cms\|lhcb)/i); if (specialWebSearch
!= null) { var lowercaseToCorrect = { \'alice\' : \'Alice\', \'atlas\' :
\'Atlas\', \'cms\' : \'CMS\', \'lhcb\' : \'LHCb\' }; specialWeb =
lowercaseToCorrect\\\[specialWebSearch\\\[1\\\].toLowerCase()\\\];
\$(\'span.webScopeDescription\').text(specialWeb); } } else { currentWeb
= \'DefaultWeb\'; } // \-\-- BEGIN: SUBWEB LOGIC TO EXTRACT SUBWEB PATH
(EXCLUDING TOPIC) \-\-- var subWebSearchWebs = \\\[\'AtlasProtected\',
\'AtlasComputing\', \'Atlas\'\\\]; // Build regex to match web/subweb
path and topic var subWebsPattern = new RegExp( \'/((\' +
subWebSearchWebs.join(\'\|\') +
\')(?=(?:/\|\$))(?:/\\\[A-Za-z0-9\\\_\\\]+)\\\*)/(\\\[A-Za-z0-9\\\_\\\]+)\$\'
); var subWebMatch = window.location.pathname.match(subWebsPattern); if
(subWebMatch) { // subWebMatch\\\[1\\\] is the full web/subweb path
(e.g. \"AtlasComputing/AtlasComputingArchive\") // subWebMatch\\\[3\\\]
is the topic (e.g. \"WebHome\") currentWeb = subWebMatch\\\[1\\\];
specialWeb = currentWeb;
\$(\'span.webScopeDescription\').text(specialWeb); } // \-\-- END:
SUBWEB LOGIC TO EXTRACT SUBWEB PATH (EXCLUDING TOPIC) \-\-- // Do we
have a favourite search engine in localStorage? We set Twiki search as
default anyways if (window.localStorage) { // var storedEngine =
localStorage.getItem(\'defaultSearchEngine\'); // console.log(\'stored
engine preference: \' + storedEngine); var storedEngine =
\'twikisearch\'; var storedEngineLi = \$(\'.cernTWikiSearch li#\' +
storedEngine); if (!storedEngineLi.hasClass(\'active\')) {
changeActiveSearchEngine(storedEngineLi); } if (storedEngine ==
\'twikisearch\') {
\$(\'input\\\[name=scope\\\]\\\[value=AllWebs\\\]\').attr(\'disabled\',\'disabled\');
\$(\'.allWebsScopeDescription\').addClass(\'disabled\'); } } // Toggle
the searchEngines list on and off on click \$(\'.cernTWikiSearch
ul.engineList\').click(function(e) { e.stopPropagation(); if
(\$(this).hasClass(\'open\')) { \$(this).removeClass(\'open\'); } else {
\$(this).addClass(\'open\'); } }); // Stupid IE8 hack because the click
handler on ul.engineList does not work properly there. if
(\$.browser.msie && document.documentMode && document.documentMode \< 9)
{ \$(\'.cernTWikiSearch #quickSearchBox\').focus(function(e) {
\$(\'.cernTWikiSearch ul.engineList\').removeClass(\'open\'); }); } //
Handle clicks on one of the search engines \$(\'.cernTWikiSearch
ul.engineList li\').click(function(e) { // If we clicked on a \<li\>
that does not has class \'active\', it means this should become active
and swap places with this. if (!\$(this).hasClass(\'active\')) {
changeActiveSearchEngine(\$(this)); } if
(\$(this).parent().hasClass(\'open\')) { \$(\'.cernTWikiSearch
#quickSearchBox\').val(searchPhrase); \$(\'.cernTWikiSearch
#quickSearchBox\').focus(); } if (\$(this).attr(\'id\') ==
\'twikisearch\') { var allWebsRadio =
\$(\'input\\\[name=scope\\\]\\\[value=AllWebs\\\]\');
allWebsRadio.attr(\'disabled\',\'disabled\');
allWebsRadio.siblings(\'input\\\[type=radio\\\]\').attr(\'checked\',true)
\$(\'.allWebsScopeDescription\').addClass(\'disabled\'); } else {
\$(\'input\\\[name=scope\\\]\\\[value=AllWebs\\\]\').attr(\'disabled\',\'\');
\$(\'.allWebsScopeDescription\').removeClass(\'disabled\'); } }); //
Show the engine description text on hover \$(\'.engineList.open
li\').live(\'hover\',function() { var displayText =
\$(this).find(\'span.engineDescription\').text(); \$(\'.cernTWikiSearch
#quickSearchBox\').val(displayText); }); // The form is submitted, now
let\'s do the search. \$(\'.cernTWikiSearch\').submit(function(e) {
e.preventDefault(); var scope = \$(\'input\\\[name=scope\\\]:checked\',
\$(this)).val(); if (scope != \'AllWebs\' && specialWeb !== undefined) {
scope = specialWeb; } var val = \$(\'.cernTWikiSearch
#quickSearchBox\').val(); var engine = \$(\'.engineList
li.active\').attr(\'id\') switch (engine) { case \'googlesearch\':
window.open(\'https://google.com/search?q=site:\' +
encodeURIComponent(\'https://twiki.cern.ch\') + (scope != \'AllWebs\' ?
\' \' + scope : \'\') + \' \' + val); break; case \'cernsearch\':
window.open(\'https://search.cern.ch/Pages/TwikiResults.aspx?k=\' +
val + (scope != \'AllWebs\' ? \' cernscope:\' + scope : \'\') +
\'&autologin=1\'); break; case \'twikisearch\':
window.open(window.location.pathname.replace(/\\\\/\\\[A-Z\\\].+\$/,\'\') +
\'/\' + currentWeb + \'/WebSearch?search=\' + val + \'&scope=all\');
break; default: break; } // Save the search engine. If the user reloads
the page he should get the last one used. if (window.localStorage) {
console.log(\'store engine preference: \' + engine);
localStorage.setItem(\'defaultSearchEngine\',engine); } }); // Save the
search phrase on every key up \$(\'.cernTWikiSearch
#quickSearchBox\').keyup(function() { searchPhrase = \$(this).val(); });
// If a user clicks outside the search engine list, the search engine
list should be closed. \$(\'html\').click(function() { if
(\$(\'.engineList\').hasClass(\'open\')) {
\$(\'.engineList\').removeClass(\'open\'); \$(\'.cernTWikiSearch
#quickSearchBox\').val(searchPhrase); } }); }); // We want to change the
active search engine function changeActiveSearchEngine(engineLi) { var
activeEngine = engineLi.siblings(\':first\');
engineLi.detach().insertBefore(activeEngine);
activeEngine.removeClass(\'active\'); engineLi.addClass(\'active\'); if
(engineLi.attr(\'id\') == \'twikiSearch\') { deactivateAllWebsOption();
} } // The user has chosen twiki search (or the preference was stored in
localStorage). // We will then disable the \'All Webs\' option since
this will time out. function deactivateAllWebsOption() { } // Helper
method to check input attribute browser compability function
checkInputAttributeSupport(attribute) { var i =
document.createElement(\"input\"); return typeof i.placeholder !==
\'undefined\'; } //\--\>

\[\![This site is powered by the TWiki collaboration
platform\](./LHCbUpgradeII \_ LHCb \_ TWiki_files/T-badge-88x31.gif
\"This site is powered by the TWiki collaboration
platform\")\](http://twiki.org/) \[\![Powered by Perl\](./LHCbUpgradeII
\_ LHCb \_ TWiki_files/perl-logo-88x31.gif \"Powered by
Perl\")\](http://www.perl.org/)Copyright &� 2008-2025 by the
contributing authors. All material on this collaboration platform is the
property of the contributing authors. or Ideas, requests, problems
regarding TWiki? use
\[Discourse\](https://discourse.web.cern.ch/c/collaborative-editing/wikis/12)
or \[Send
feedback\](https://twiki.cern.ch/twiki/bin/view/Main/ServiceNow)

var \\\_paq = window.\\\_paq = window.\\\_paq \|\| \\\[\\\]; /\\\*
tracker methods like \"setCustomDimension\" should be called before
\"trackPageView\" \\\*/ \\\_paq.push(\\\[\'trackPageView\'\\\]);
\\\_paq.push(\\\[\'enableLinkTracking\'\\\]); (function() { var
u=\"https://webanalytics.web.cern.ch/\";
\\\_paq.push(\\\[\'setTrackerUrl\', u+\'matomo.php\'\\\]);
\\\_paq.push(\\\[\'setSiteId\', \'5\'\\\]); var d=document,
g=d.createElement(\'script\'),
s=d.getElementsByTagName(\'script\')\\\[0\\\]; g.async=true;
g.src=u+\'matomo.js\'; s.parentNode.insertBefore(g,s); })();
