LHCbUpgrade \< LHCb \< TWiki \@import
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
padding: 7px; } .tableSortIcon img {padding-left:.3em;
vertical-align:text-bottom;} .twikiTable#twikiAttachmentsTable td
{border-style:solid none;} .twikiTable#twikiAttachmentsTable th
{border-style:solid none;} .twikiTable#twikiAttachmentsTable td
{vertical-align:middle;} .twikiTable#twikiAttachmentsTable th
{vertical-align:middle;} .twikiTable#twikiAttachmentsTable td
{vertical-align:top;} .twikiTable#twikiAttachmentsTable th
{background-color:#ffffff;} .twikiTable#twikiAttachmentsTable
th.twikiSortedCol {background-color:#eeeeee;}
.twikiTable#twikiAttachmentsTable th {color:#0066cc;}
.twikiTable#twikiAttachmentsTable th a:link {color:#0066cc;}
.twikiTable#twikiAttachmentsTable th a:visited {color:#0066cc;}
.twikiTable#twikiAttachmentsTable th a:link font {color:#0066cc;}
.twikiTable#twikiAttachmentsTable th a:visited font {color:#0066cc;}
.twikiTable#twikiAttachmentsTable th a:hover
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

\[TWiki\](https://twiki.cern.ch/twiki/bin/view/Main/WebHome)\\\>\![\](./LHCbUpgrade
\_ LHCb \_ TWiki_files/web-bg-small.gif) \[LHCb
Web\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebHome)\\\>\[LHCbUpgrade\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade
\"Topic revision: 167 (2020-11-16 - 16:02:33)\") (2020-11-16,
\[RolfLindner\](https://twiki.cern.ch/twiki/bin/view/Main/RolfLindner))
\[\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/uweb-o14.gif)
Edit\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbUpgrade?t=1762217467;nowysiwyg=1
\"Edit this topic
text\")\[Attach\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade
\"Attach an image or document to this
topic\")\[PDF\](https://twiki.cern.ch/twiki/bin/genpdf/LHCb/LHCbUpgrade
\"Create a PDF file for the topic\")

\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/upgrade-logo-small2.jpg)

The LHCb Upgrade ================

\* \[LHCb Upgrade
Organisation\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#LHCb_Upgrade_Organisation)
\* \[LHCb Upgrade
Activities\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#LHCb_Upgrade_Activities)
\* \[Detector LHCb upgrade milestones, reported to
LHCC\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#Detector_LHCb_upgrade_milestones)
\* \[Paper on the LHCb Upgrade
construction\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#Paper_on_the_LHCb_Upgrade_constr)
\* \[Material for
presentations\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#Material_for_presentations)
\* \[Detector TDRs for the LHCb
Upgrade\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#Detector_TDRs_for_the_LHCb_Upgra)
\* \[Framework TDR (FTDR) for the LHCb
Upgrade\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#Framework_TDR_FTDR_for_the_LHCb)
\* \[Letter of Intent (LoI) for the LHCb
Upgrade\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#Letter_of_Intent_LoI_for_the_LHC)
\* \[Expression of Interest (EoI) for an LHCb
Upgrade\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#Expression_of_Interest_EoI_for_a)
\* \[Meetings and
Workshops\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#Meetings_and_Workshops)

LHCb Upgrade Organisation
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

Upgrade Planning Group (UPG)

\_Upgrade matters will be overseen by the UPG:\_

\*\*Membership:\*\*

\* Spokesperson (chair) \[Giovanni Passaleva\![\](./LHCbUpgrade \_ LHCb
\_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Passaleva&first=Giovanni&email=&pemail=&off=&tel=)
\* Deputy Spokesperson \[Chris Parkes\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Parkes&first=Chris&email=&pemail=&off=&tel=)
\* Technical Coordinator \[Rolf Lindner\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=lindner&first=Rolf&email=&pemail=&off=&tel=)
\* Deputy Physics Coordinator \[Vincenzo Vagnoni\![\](./LHCbUpgrade \_
LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Vagnoni&first=Vincenzo&email=&pemail=&off=&tel=)
\* Upgrade Detector Coordinator \[Massimiliano
Ferro-Luzzi\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Ferro-Luzzi&first=Massimiliano&email=&pemail=&off=&tel=)
\* Upgrade Software co-Coordinator \[Concezio Bozzi\![\](./LHCbUpgrade
\_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Bozzi&first=Concezio&email=&pemail=&off=&tel=)
\* Upgrade Software co-Coordinator \[Vava Gligorov\![\](./LHCbUpgrade \_
LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Gligorov&first=Vladimir&email=&pemail=&off=&tel=)
\* Upgrade Resources Coordinator \[Andreas Schopper\![\](./LHCbUpgrade
\_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Schopper&first=Andreas&email=&pemail=&off=&tel=)
\* Upgrade Data Processing Coordinator \[Renaud Le
Gac\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=le+gac&first=Renaud&email=&pemail=&off=&tel=)
\* Upgrade Data Processing Coordinator \[Ken Wyllie\![\](./LHCbUpgrade
\_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Wyllie&first=Ken&email=&pemail=&off=&tel=)

Upgrade Detector

\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/upgrade-detector.jpg)

Upgrade Detector Coordinator

Take on responsibilities delegated by Tech Coordinator, including:

\* Monitor closely project progress and schedules \* Define & follow-up
milestones and review critical items \* Support detector groups in
organising EDRs and PRRs \* Report on these activities to TB

\[Upgrade Software Planning Group
(USPG)\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbComputingUpgrade)

\* The USPG coordinates all the upgrade software activities. The upgrade
software activities are organized through the existing projects and
working groups. \* The USPG is chaired by an Upgrade Software
Coordinator (USC) to ensure that the activities in the areas of
computing and trigger/reconstruction are properly harmonised and
represented. \* The USCs ensure coordination among all the projects and
working groups represented in the USPG in order to optimize effort and
resources. They also ensure and facilitate an effective connection
between the general software developments and the sub-detector
reconstruction software developments. The sub-detector reconstruction
software remains under the responsibility of the subdetector projects.

Upgrade Resources Coordinator

\* Chair Upgrade Resources Board \* Devise & oversee strategy for
matching of available financial & human resources to detector
requirements & national commitments \* Work closely with Technical and
Resources Coordinators

Upgrade Data Processing Coordinator

\* Monitor Upgrade activities on data acquisition and the related online
activities \* Work closely with Project Leaders in these areas and with
Technical Coordinator \* Report on these activities to TB

LHCb Upgrade Activities \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\*\*Wherever possible, the following list provides information on
upgrade twiki pages and contact persons for the various upgrade
activities:\*\*

\* \*\*General\*\* \* \[Infrastructure &
Integration\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCb-upgrade-infrastructure)
; contact: \[Eric Thomas\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Thomas&first=Eric&email=&pemail=&off=&tel=)
\* \[Electronics\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](http://lhcb-elec.web.cern.ch/lhcb-elec/html/upgrade.htm)
; contact: \[Ken Wyllie\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=wyllie&first=&email=&pemail=&off=&tel=)
\*
\[Simulation\](https://twiki.cern.ch/twiki/bin/view/LHCb/SimulationUpgrade)
; contact: \[Gloria Corti\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://phonebook.cern.ch/foundpub/Phonebook/#id=PE490507?id=PE382743)
\* \[Software &
Computing\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbComputingUpgrade)
; contacts: \[Concezio Bozzi\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://phonebook.cern.ch/foundpub/Phonebook/?id=PE377643)
and \[Vava Gligorov\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://phonebook.cern.ch/phonebook/#personDetails/?id=626174)
\*
\[Tracking\](https://twiki.cern.ch/twiki/bin/viewauth/LHCbPhysics/TrackingUpgrade)
; contact: \[Johannes Albrecht\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=%25Albrecht%25&first=&email=&pemail=&off=&tel=)
\* Readout Board \* Readout hardware (PCIe40) ; contact: \[Jean-Pierre
Cachemiche\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=cachemiche&first=&email=&pemail=&off=&tel=)
\* Readout firmware (PCIe40) ; contacts: \[Stephane
T\'Jampens\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=t%25jampens&first=&email=&pemail=&off=&tel=)
, \[Guillaume Vouters\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=vouters&first=&email=&pemail=&off=&tel=)
\* \*\*Detector\*\* \* \[VErtexLOcator\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://lbtwiki.cern.ch/bin/view/VELO/VELOUpgrade)
; contact: \[Paula Collins\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=collins&first=&email=&pemail=&off=&tel=)
\* \[Upstream Tracker
(New!!)\](https://twiki.cern.ch/twiki/bin/viewauth/LHCb/UpstreamTrackerUpgrade)
\[Upstream Tracker
(old)\](https://twiki.cern.ch/twiki/bin/view/LHCb/SiliconStripTracker) ;
contact: \[Marina Artuso\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Artuso&first=&email=&pemail=&off=&tel=)
\* \[SALT - Common Silicon Strip Readout
ASIC\](https://twiki.cern.ch/twiki/bin/view/LHCb/StripAsic) ; contacts:
\[Marek Idzik\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=%25IDZIK%25&first=&email=&pemail=&off=&tel=),
\[Tomasz Szumlak\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=%25SZUMLAK%25&first=&email=&pemail=&off=&tel=)
\* \[Scintillating Fibre
Tracker\](https://twiki.cern.ch/twiki/bin/view/LHCb/UpgradeSciFiTracker)
; contact: \[Ulrich Uwer\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Uwer&first=&email=&pemail=&off=&tel=)
\* \[Rich
Upgrade\](https://twiki.cern.ch/twiki/bin/view/LHCb/RichUpgrade) ;
contact: \[Carmelo d\'Ambrosio\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=D%27Ambrosio&first=Carmelo&email=&pemail=&off=&tel=)
\* \[Calorimeter
System\](https://twiki.cern.ch/twiki/bin/view/LHCb/CaloUpgrade) ;
contact: \[Frederic Machefert\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=machefert&first=&email=&pemail=&off=&tel=)
\* \[Muon
System\](https://twiki.cern.ch/twiki/bin/view/LHCb/MuonUpgradeElectronics)
; contacts: \[Alessandro Cardini\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Cardini&first=&email=&pemail=&off=&tel=)

\* \*\*Online\*\* \* DAQ ; contacts: \[Niko Neufeld\![\](./LHCbUpgrade
\_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=neufeld&first=niko&email=&pemail=&off=&tel=)
\* ECS ; contact: \[Clara Gaspar\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=Gaspar&first=Clara&email=&pemail=&off=&tel=)
\* TFC ; contacts: \[Federico Alessio\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=alessio&first=federico&email=&pemail=&off=&tel=)
\* \*\*Trigger\*\* \* \[Low Level Trigger
(LLT)\](https://twiki.cern.ch/twiki/bin/view/LHCb/LltUpgrade) ;
contacts: \[Patrick Robbe\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://found.cern.ch/found-cgi/exp?exp=LHCB&last=robbe&first=patrick&email=&pemail=&off=&tel=)
\* Trigger (until Jan 2019) ; \[Upgrade Physics and
Trigger\](https://twiki.cern.ch/twiki/bin/viewauth/LHCbPhysics/UpgradePhysicsAndTrigger)
\* Real-Time Analysis (post Jan 2019) ; \[RTA
Twiki\](https://twiki.cern.ch/twiki/bin/view/LHCb/RealTimeAnalysis)

Detector LHCb upgrade milestones, reported to LHCC
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/u-milestones-March_2018.jpg)

Paper on the LHCb Upgrade construction
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* The TOF can be found
\[here\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/upgrade_construction_paper\_(2).pdf)

Material for presentations
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

Pictures and plots for talks on upgrade can be found \[here (not yet
ready!)\](https://twiki.cern.ch/twiki/bin/view/LHCb/UpgradeMaterialForPresentations)

Detector TDRs for the LHCb Upgrade
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/VeLoPhalf1.jpg)
\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/PID_front.jpg)
\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/Tracker-TDR-A4-3-s.jpg)
\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/Trigger_and_Online-orange_A4-max.jpg)

\* The Trigger and Online TDR for the LHCb upgrade has been submitted to
the LHCC on 23 May 2014, available on CDS:
\[CERN-LHCC-2014-016\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](http://cds.cern.ch/record/1701361?ln=en)
\* The Tracker TDR for the LHCb upgrade has been submitted to the LHCC
on 21 February 2014, available on CDS:
\[CERN-LHCC-2014-001\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/1647400?ln=en)
\* The PID TDR for the LHCb Upgrade has been submitted to the LHCC on 29
November 2013, available on CDS: \[CERN-LHCC-2013-022\![\](./LHCbUpgrade
\_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/1624074?ln=en)
\* The VELO TDR for the LHCb Upgrade has been submitted to the LHCC on
29 November 2013, available on CDS:
\[CERN-LHCC-2013-021\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/1624070?ln=en)

Framework TDR (FTDR) for the LHCb Upgrade
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/FWTDR-final-front-A4.jpg)

\* The FTDR for the LHCb Upgrade has been submitted to the LHCC on 25
May 2012, available on CDS: \[CERN-LHCC-2012-007\![\](./LHCbUpgrade \_
LHCb \_
TWiki_files/external-link.gif)\](https://cdsweb.cern.ch/record/1443882?ln=en)
\* The tex source files are available on SVN (svn co
svn+ssh://svn.cern.ch/reps/lhcbdocs/Publications/TDR/Framew)

Letter of Intent (LoI) for the LHCb Upgrade
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/UPGRADE-LoI-10-only-front.jpg)

\* The LHCb Upgrade LoI has been submitted to the LHCC on 7 March 2011,
available on CDS: \[CERN-LHCC-2011-001\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/1333091?ln=en)
\* A final version
\[LoI.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/LOI.pdf)
with revised author list has been submitted to the LHCC on 29 March 2011
\* The tex source files can be found \[here\![\](./LHCbUpgrade \_ LHCb
\_
TWiki_files/external-link.gif)\](https://indico.cern.ch/conferenceDisplay.py?confId=104253)

Expression of Interest (EoI) for an LHCb Upgrade
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* The LHCb Upgrade EoI was submitted to the LHCC on 22 April 2008. \*
The submitted EoI is available on CDS:
\[CERN-LHCC-2008-007\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/search?id=1100545)
\* The EoI has also been made into a public LHCb note:
\[LHCb-2008-019\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/1102235?)
\* The EoI/LHCb upgrade plan was presented to the LHCC on Sept 23:
\[slides\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/external-link.gif)\](http://indico.cern.ch/materialDisplay.py?contribId=1&materialId=slides&confId=41446)

Meetings and Workshops \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\[\\\> Indico page of LHCb Upgrade meetings\![\](./LHCbUpgrade \_ LHCb
\_
TWiki_files/external-link.gif)\](https://indico.cern.ch/categoryDisplay.py?categId=1245)

\*
\[Hybrid\\\_Panel\\\_V2I5.rar\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/Hybrid_Panel_V2I5.rar):
Electrical Hybrid Panel
\[V2I5\](https://twiki.cern.ch/twiki/bin/edit/LHCb/V2I5?topicparent=LHCb.LHCbUpgrade;nowysiwyg=1
\"this topic does not yet exist; you can create it.\") and FR4 panel
\[V1I2\](https://twiki.cern.ch/twiki/bin/edit/LHCb/V1I2?topicparent=LHCb.LHCbUpgrade;nowysiwyg=1
\"this topic does not yet exist; you can create it.\") projects

\*
\[FR4\\\_PANEL\\\_V1I2.rar\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/FR4_PANEL_V1I2.rar):
Electrical Hybrid Panel
\[V2I5\](https://twiki.cern.ch/twiki/bin/edit/LHCb/V2I5?topicparent=LHCb.LHCbUpgrade;nowysiwyg=1
\"this topic does not yet exist; you can create it.\") and FR4 panel
\[V1I2\](https://twiki.cern.ch/twiki/bin/edit/LHCb/V1I2?topicparent=LHCb.LHCbUpgrade;nowysiwyg=1
\"this topic does not yet exist; you can create it.\") projects

\*
\[upgrade\\\_construction\\\_paper(1).pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/upgrade_construction_paper%281%29.pdf):
upgrade\\\_construction\\\_paper(1).pdf

\[\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/toggleopen.gif)Attachments\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#)
\[\![\](./LHCbUpgrade \_ LHCb \_
TWiki_files/toggleclose.gif)Attachments\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#)

Topic attachments

\[I\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?sortcol=0;table=1;up=0#sorted_table
\"Sort by this column\")

\[Attachment\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?sortcol=1;table=1;up=0#sorted_table
\"Sort by this column\")

\[History\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?sortcol=2;table=1;up=0#sorted_table
\"Sort by this column\")

\[Action\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?sortcol=3;table=1;up=0#sorted_table
\"Sort by this column\")

\[Size\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?sortcol=4;table=1;up=0#sorted_table
\"Sort by this column\")

\[Date\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?sortcol=5;table=1;up=0#sorted_table
\"Sort by this column\")

\[Who\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?sortcol=6;table=1;up=0#sorted_table
\"Sort by this column\")

\[Comment\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?sortcol=7;table=1;up=0#sorted_table
\"Sort by this column\")

\![Compressed Zip archive\](./LHCbUpgrade \_ LHCb \_ TWiki_files/zip.gif
\"Compressed Zip archive\")zip

\[Archive.zip\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/Archive.zip)

r2
\[r1\](https://twiki.cern.ch/twiki/bin/viewfile/LHCb/LHCbUpgrade?filename=Archive.zip;rev=1)

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade?filename=Archive.zip;revInfo=1
\"change, update, previous revisions, move, delete\...\")

19529.5 K

2011-01-20 - 15:24

\[GuyWilkinson\](https://twiki.cern.ch/twiki/bin/view/Main/GuyWilkinson)

Revised new draft of physics chapter from Tim and Guy

\![PDF\](./LHCbUpgrade \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LHCb-LHCC-Upgrade-710.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/LHCb-LHCC-Upgrade-710.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade?filename=LHCb-LHCC-Upgrade-710.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

2083.8 K

2010-07-06 - 18:10

\[SheldonStone\](https://twiki.cern.ch/twiki/bin/view/Main/SheldonStone)

Sheldon Stone\'s LHCC Presentation

\![PDF\](./LHCbUpgrade \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LOI-Intro.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/LOI-Intro.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade?filename=LOI-Intro.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

249.4 K

2011-02-14 - 17:52

\[SheldonStone\](https://twiki.cern.ch/twiki/bin/view/Main/SheldonStone)

Revised Introduction of Feb. 14

\![PDF\](./LHCbUpgrade \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LOI-Physics-2.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/LOI-Physics-2.pdf)

r2
\[r1\](https://twiki.cern.ch/twiki/bin/viewfile/LHCb/LHCbUpgrade?filename=LOI-Physics-2.pdf;rev=1)

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade?filename=LOI-Physics-2.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

2333.1 K

2010-12-27 - 21:29

\[SheldonStone\](https://twiki.cern.ch/twiki/bin/view/Main/SheldonStone)

Draft of LOI Physics section, Dec. 27, 2010

\![PDF\](./LHCbUpgrade \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LOI-Physics.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/LOI-Physics.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade?filename=LOI-Physics.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

2329.2 K

2010-12-25 - 19:29

\[SheldonStone\](https://twiki.cern.ch/twiki/bin/view/Main/SheldonStone)

2nd draft of LOI Physics section, Dec. 25, 2010

\![PDF\](./LHCbUpgrade \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[LOI.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/LOI.pdf)

r12
\[r11\](https://twiki.cern.ch/twiki/bin/viewfile/LHCb/LHCbUpgrade?filename=LOI.pdf;rev=11)
\[r10\](https://twiki.cern.ch/twiki/bin/viewfile/LHCb/LHCbUpgrade?filename=LOI.pdf;rev=10)
\[r9\](https://twiki.cern.ch/twiki/bin/viewfile/LHCb/LHCbUpgrade?filename=LOI.pdf;rev=9)
\[r8\](https://twiki.cern.ch/twiki/bin/viewfile/LHCb/LHCbUpgrade?filename=LOI.pdf;rev=8)

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade?filename=LOI.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

16568.6 K

2011-03-31 - 17:41

\[SheldonStone\](https://twiki.cern.ch/twiki/bin/view/Main/SheldonStone)

LOI v2 with corrected author list

\![PDF\](./LHCbUpgrade \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[Mandate.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/Mandate.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade?filename=Mandate.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

188.5 K

2011-11-03 - 12:09

\[AndreasSchopper\](https://twiki.cern.ch/twiki/bin/view/Main/AndreasSchopper)

Mandate of Upgrade Steering Panel

\![PDF\](./LHCbUpgrade \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[Tracking.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/Tracking.pdf)

r2
\[r1\](https://twiki.cern.ch/twiki/bin/viewfile/LHCb/LHCbUpgrade?filename=Tracking.pdf;rev=1)

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade?filename=Tracking.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

9557.2 K

2010-12-07 - 15:47

\[SheldonStone\](https://twiki.cern.ch/twiki/bin/view/Main/SheldonStone)

Updated integrated tracking section of Dec. 7

\![PDF\](./LHCbUpgrade \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[tt-upgrade.pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/tt-upgrade.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade?filename=tt-upgrade.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

593.4 K

2010-11-29 - 22:21

\[SheldonStone\](https://twiki.cern.ch/twiki/bin/view/Main/SheldonStone)

 

\![PDF\](./LHCbUpgrade \_ LHCb \_ TWiki_files/pdf.gif \"PDF\")pdf

\[upgrade\\\_construction\\\_paper\\\_(2).pdf\](https://twiki.cern.ch/twiki/pub/LHCb/LHCbUpgrade/upgrade_construction_paper\_%282%29.pdf)

r1

\[manage\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade?filename=upgrade_construction_paper\_%282%29.pdf;revInfo=1
\"change, update, previous revisions, move, delete\...\")

115.6 K

2020-11-16 - 16:02

\[RolfLindner\](https://twiki.cern.ch/twiki/bin/view/Main/RolfLindner)

 

\[\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/uweb-o14.gif)
Edit\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbUpgrade?t=1762217467;nowysiwyg=1
\"Edit this topic
text\") \| \[Attach\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbUpgrade
\"Attach an image or document to this topic\") \| \[Print
version\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?cover=print
\"Printable version of this
topic\") \| \[History\](https://twiki.cern.ch/twiki/bin/oops/LHCb/LHCbUpgrade?template=oopshistory
\"View total topic history\"):
r167 \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbUpgrade?rev1=167;rev2=166) \[r166\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?rev=166) \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbUpgrade?rev1=166;rev2=165) \[r165\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?rev=165) \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbUpgrade?rev1=165;rev2=164) \[r164\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?rev=164) \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbUpgrade?rev1=164;rev2=163) \[r163\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?rev=163) \| \[Backlinks\](https://twiki.cern.ch/twiki/bin/oops/LHCb/LHCbUpgrade?template=backlinksweb
\"Search the LHCb Web for topics that link to here\") \| \[Raw
View\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?raw=on
\"View raw text without
formatting\") \| \[WYSIWYG\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbUpgrade?t=1762217467;nowysiwyg=0
\"WYSIWYG editor\") \| \[More topic
actions\](https://twiki.cern.ch/twiki/bin/oops/LHCb/LHCbUpgrade?template=oopsmore&param1=167&param2=167
\"Delete or rename this topic; set parent topic; view and compare
revisions\")

Topic revision: r167 - 2020-11-16
\[\\-\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbUpgrade?t=1762217467;nowysiwyg=1)
\[RolfLindner\](https://twiki.cern.ch/twiki/bin/view/Main/RolfLindner)

\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/person.gif)
\[YagnaSwaroopDhurbhakula\](https://twiki.cern.ch/twiki/bin/edit/Main/YagnaSwaroopDhurbhakula?topicparent=LHCb.LHCbUpgrade;nowysiwyg=1
\"this topic does not yet exist; you can create it.\")
\![Lock\](./LHCbUpgrade \_ LHCb \_ TWiki_files/lock.gif \"Lock\") \[Log
Out\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade?logout=1)

\* \[\![Web background\](./LHCbUpgrade \_ LHCb \_
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

\[\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/toggleopen.gif)Public
webs\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#)
\[\![\](./LHCbUpgrade \_ LHCb \_ TWiki_files/toggleclose.gif)Public
webs\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbUpgrade#)

\* \[ABATBEA\](https://twiki.cern.ch/twiki/bin/view/ABATBEA/WebHome) \*
\[ACPP\](https://twiki.cern.ch/twiki/bin/view/ACPP/WebHome) \*
\[ADCgroup\](https://twiki.cern.ch/twiki/bin/view/ADCgroup/WebHome) \*
\[AEGIS\](https://twiki.cern.ch/twiki/bin/view/AEGIS/WebHome) \*
\[AfricaMap\](https://twiki.cern.ch/twiki/bin/view/AfricaMap/WebHome) \*
\[AgileInfrastructure\](https://twiki.cern.ch/twiki/bin/view/AgileInfrastructure/WebHome)
\* \[ALICE\](https://twiki.cern.ch/twiki/bin/view/ALICE/WebHome) \*
\[AliceEbyE\](https://twiki.cern.ch/twiki/bin/edit/AliceEbyE/WebHome?topicparent=LHCb.LHCbUpgrade;nowysiwyg=1
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

\[\![CERN\](./LHCbUpgrade \_ LHCb \_
TWiki_files/logo_lhcb.png)\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebHome)

\*   

\* \* \![TWiki Search Icon\](./LHCbUpgrade \_ LHCb \_
TWiki_files/twikisearchicon.gif) TWiki Search \* \![Google Search
Icon\](./LHCbUpgrade \_ LHCb \_ TWiki_files/googlesearchicon.png) Google
Search

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
platform\](./LHCbUpgrade \_ LHCb \_ TWiki_files/T-badge-88x31.gif \"This
site is powered by the TWiki collaboration
platform\")\](http://twiki.org/) \[\![Powered by Perl\](./LHCbUpgrade \_
LHCb \_ TWiki_files/perl-logo-88x31.gif \"Powered by
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
