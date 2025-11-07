WebHome \< VELO \< TWiki \@import
url(\'https://lbtwiki.cern.ch/pub/TWiki/TWikiTemplates/base.css\');
#patternTopBar, #patternClearHeaderCenter, #patternClearHeaderLeft,
#patternClearHeaderRight, #patternTopBarContentsOuter,
#patternTopBarContents { height:64px; /\\\* top bar height; make room
for header columns \\\*/ overflow:hidden; } #patternOuter {
margin-left:14em; } #patternLeftBar { width:14em; margin-left:-14em; }
\@import
url(\'https://lbtwiki.cern.ch/pub/TWiki/PatternSkin/layout.css\');
\@import
url(\'https://lbtwiki.cern.ch/pub/TWiki/PatternSkin/style.css\');
\@import
url(\'https://lbtwiki.cern.ch/pub/TWiki/PatternSkin/colors.css\'); /\\\*
Styles that are set using variables \\\*/ .patternBookView .twikiTopRow,
.patternWebIndicator a img, .patternWebIndicator a:hover img {
background-color:silver; } #patternTopBarContents {
background-image:url(https://lbtwiki.cern.ch/pub/TWiki/PatternSkin/TWiki\\\_header.gif);
background-repeat:no-repeat;} .patternBookView { border-color:silver; }
.patternPreviewPage #patternMain { /\\\* uncomment to set the preview
image \\\*/
/\\\*background-image:url(\"https://lbtwiki.cern.ch/pub/TWiki/PreviewBackground/preview2bg.gif\");\\\*/
} \@import
url(\"https://lbtwiki.cern.ch/pub/TWiki/PatternSkin/print.css\");
.twikiMakeVisible{display:inline;}.twikiMakeVisibleInline{display:inline;}.twikiMakeVisibleBlock{display:block;}.twikiMakeHidden{display:none;}
\@import
url(\"https://lbtwiki.cern.ch/pub/TWiki/TagMePlugin/tagme.css\");

\[TWiki\](https://lbtwiki.cern.ch/bin/view/Main/WebHome)\\\>\![\](./WebHome
\_ VELO \_ TWiki_files/web-bg-small.gif) \[VELO
Web\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome)\\\>\[WebHome\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome
\"Topic revision: 127 (2025-07-01 - 07:28:29)\") (2025-07-01,
\[efrodrig\](https://lbtwiki.cern.ch/bin/edit/Main/Efrodrig?topicparent=VELO.WebHome;nowysiwyg=0
\"efrodrig (this topic does not yet exist; you can create it)\"))
\[\![\](./WebHome \_ VELO \_ TWiki_files/uweb-o14.gif)
Edit\](https://lbtwiki.cern.ch/bin/edit/VELO/WebHome?t=1762215974;nowysiwyg=0
\"Edit this topic
text\")\[Attach\](https://lbtwiki.cern.ch/bin/attach/VELO/WebHome
\"Attach an image or document to this topic\")

Tags:

LinuxModification November
2014networkOnlineOfflineInstallMoverSoftwQuattorRunDatabaseServersVELOequalizationVirtualisation
//\<!\\\[CDATA\\\[ function createSelectBox(inText, inElemId) { var
selectBox = document.createElement(\'SELECT\'); selectBox.name =
\"tag\"; selectBox.className = \"twikiSelect\";
document.getElementById(inElemId).appendChild(selectBox); var items =
inText.split(\"#\"); var i, ilen = items.length; for (i=0; i\<ilen; ++i)
{ selectBox.options\\\[i\\\] = new Option(items\\\[i\\\],
items\\\[i\\\]); } } var text=\"#Linux#Modification November
2014#network#OnlineOfflineInstallMoverSoftw#Quattor#RunDatabaseServers#VELOequalization#Virtualisation\";
if (text.length \> 0) {createSelectBox(text, \"tagMeSelect7\");
document.getElementById(\"tagmeAddNewButton\").style.display=\"inline\";}
//\\\]\\\]\>

\[tag this
topic\](https://lbtwiki.cern.ch/bin/viewauth/VELO/WebHome?tagmode=nojavascript)

\[create new
tag\](https://lbtwiki.cern.ch/bin/viewauth/TWiki/TagMeCreateNewTag?from=VELO.WebHome)

\[view all
tags\](https://lbtwiki.cern.ch/bin/view/TWiki/TagMeViewAllTags)

Welcome to the LHCb VELO Upgrade Twiki pages
============================================

mailing list: \[lhcb-velo@cern.ch\](mailto:lhcb-velo@cern.ch)

\![VeloLogo.gif\](./WebHome \_ VELO \_ TWiki_files/VeloLogo.gif)

The \[upgraded LHCb
VELO\](https://lbtwiki.cern.ch/bin/view/VELO/VELOUpgrade) silicon vertex
detector is a lightweight hybrid pixel detector capable data driven
readout at a luminosity of 2 x 1033 cm\\-2 s\\-1 at the bunch crossing
rate of 30 MHz.

The track reconstruction speed and precision is enhanced relative to the
first VELO detector even at the high multiplicity conditions of the
upgrade, due to the pixel geometry and a closest distance of approach to
the LHC beams of just 5.1 mm for the first sensitive element.

Cooling is provided by evaporative CO2 circulating microchannel cooling
substrates. The whole detector contains 41 million 55 �m by 55 �m
pixels. Each detector assembly is read out by three custom developed
\[VeloPix\](https://lbtwiki.cern.ch/bin/edit/VELO/VeloPix?topicparent=VELO.WebHome;nowysiwyg=0
\"VeloPix (this topic does not yet exist; you can create it)\") front
end ASICs. Each ASIC is designed to cope with almost 1 billion hits per
second.

The VELO upgrade has been described in the \[Technical Design
Report\![\](./WebHome \_ VELO \_
TWiki_files/external-link.gif)\](https://cds.cern.ch/record/1624070?ln=en) \![External
link mark\](./WebHome \_ VELO \_ TWiki_files/external.gif), submitted in
November 2013 which lays out the planned construction and installation,
and gives an overview of the expected detector performance. Some key
figures and diagrams related to the VELO Upgrade can be found on our
collection at \[Material for
Presentations\](https://lbtwiki.cern.ch/bin/view/VELO/VeloUpgradePresentationMaterial).

\* \* \*

\[VELO Project
Organisation\](https://lbtwiki.cern.ch/bin/view/VELO/VeloOrganisation)
===================================================================================

\* \* \*

The Velo Project operates under the responsibility of the VELO Project
leader \[Victor Coco\](mailto:victor.coco@cern.ch) and deputy project
leaders \[Stefano de Capua\](mailto:stefano.de.capua@cern.ch) (Run 3)
and \[Kazu Akiba\](mailto:Kazu.Akiba@cern.ch) (Upgrade 2).

The project is organised into workpackages covering the critical
elements of the detector.

The complete organogram and the contact persons for each of the
workpackages can be found at \[Velo
Organisation\](https://lbtwiki.cern.ch/bin/view/VELO/VeloOrganisation)

\* \* \*

Links for shifters: ===================

\* Piquet training information:
\[https://codimd.web.cern.ch/s/UV-2VgIVe\![\](./WebHome \_ VELO \_
TWiki_files/external-link.gif)\](https://codimd.web.cern.ch/s/UV-2VgIVe)
\* Daily checklist:
\[VELOUpgradeShifterChecklist\](https://lbtwiki.cern.ch/bin/view/VELO/VELOUpgradeShifterChecklist)
\* \[VELO Operating
Manuals\](https://lbtwiki.cern.ch/bin/view/VELO/VELOOperatingManuals)

Links to main topics: =====================

\* \#### \[VELO
Testbeams\](https://lbtwiki.cern.ch/bin/view/VELO/Testbeam \"VELO
Testbeams\")

Quick Links: ============

\* \[Velo Contacts
Page\](https://lbtwiki.cern.ch/bin/edit/VELO/VeloContacts?topicparent=VELO.WebHome;nowysiwyg=0
\"Velo Contacts Page (this topic does not yet exist; you can create
it)\")

\[List Of Conferences And
Speakers\](https://lbtwiki.cern.ch/bin/view/VELO/ConferenceTalks)

\[Material for
presentations\](https://lbtwiki.cern.ch/bin/view/VELO/VeloUpgradePresentationMaterial)
\[Publications\](https://lbtwiki.cern.ch/bin/view/VELO/VELOPublications)

\* Old pages can be found at
\[here\](https://lbtwiki.cern.ch/bin/view/VELO/VeloU1Main_legacy) \* The
old Velo Twiki can be found here: \[Obsolete Velo
Twiki\](https://lbtwiki.cern.ch/bin/view/VELO/VeloObsoleteTwiki)

\[\![\](./WebHome \_ VELO \_ TWiki_files/uweb-o14.gif)
Edit\](https://lbtwiki.cern.ch/bin/edit/VELO/WebHome?t=1762215974;nowysiwyg=0
\"Edit this topic
text\") \| \[Attach\](https://lbtwiki.cern.ch/bin/attach/VELO/WebHome
\"Attach an image or document to this topic\") \| \[Watch\![\](./WebHome
\_ VELO \_
TWiki_files/external-link.gif)\](https://lbtwiki.cern.ch/bin/viewauth/VELO/WebHome?watchlist_action=togglewatch;watchlist_topic=VELO.WebHome) \![External
link mark\](./WebHome \_ VELO \_ TWiki_files/external.gif)  \| \[Print
version\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome?cover=print
\"Printable version of this
topic\") \| \[History\](https://lbtwiki.cern.ch/bin/rdiff/VELO/WebHome?type=history
\"View total topic history\"):
r127 \[\<\](https://lbtwiki.cern.ch/bin/rdiff/VELO/WebHome?rev1=127;rev2=126) \[r126\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome?rev=126) \[\<\](https://lbtwiki.cern.ch/bin/rdiff/VELO/WebHome?rev1=126;rev2=125) \[r125\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome?rev=125) \[\<\](https://lbtwiki.cern.ch/bin/rdiff/VELO/WebHome?rev1=125;rev2=124) \[r124\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome?rev=124) \[\<\](https://lbtwiki.cern.ch/bin/rdiff/VELO/WebHome?rev1=124;rev2=123) \[r123\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome?rev=123) \| \[Backlinks\](https://lbtwiki.cern.ch/bin/oops/VELO/WebHome?template=backlinksweb
\"Search the VELO Web for topics that link to here\") \| \[Raw
View\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome?raw=on \"View raw
text without formatting\") \| \[Raw
edit\](https://lbtwiki.cern.ch/bin/edit/VELO/WebHome?t=1762215974;nowysiwyg=1
\"Raw Edit this topic text\") \| \[More topic
actions\](https://lbtwiki.cern.ch/bin/oops/VELO/WebHome?template=oopsmore&param1=127&param2=127
\"Delete or rename this topic; set parent topic; view and compare
revisions\")

Topic revision: r127 - 2025-07-01 \[\\-\![\](./WebHome \_ VELO \_
TWiki_files/external-link.gif)\](https://lbtwiki.cern.ch/bin/edit/VELO/WebHome?t=1762215974;nowysiwyg=1) \![External
link mark\](./WebHome \_ VELO \_ TWiki_files/external.gif)
\[efrodrig\](https://lbtwiki.cern.ch/bin/edit/Main/Efrodrig?topicparent=VELO.WebHome;nowysiwyg=0
\"efrodrig (this topic does not yet exist; you can create it)\")

\* \[\![Web background\](./WebHome \_ VELO \_
TWiki_files/web-bg-small.gif \"Web background\")
VELO\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome)

Hello
\[ydhurbha\](https://lbtwiki.cern.ch/bin/edit/Main/Ydhurbha?topicparent=VELO.WebHome;nowysiwyg=0
\"ydhurbha (this topic does not yet exist; you can create it)\")

\* \[Create personal
sidebar\](https://lbtwiki.cern.ch/bin/edit/Main/ydhurbhaLeftBar?templatetopic=TWiki.WebLeftBarPersonalTemplate&topicparent=ydhurbha)

\* \*\*\[\![Home\](./WebHome \_ VELO \_ TWiki_files/home.gif \"Home\")
VELO Web\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome)\*\* \*
\[\![New topic\](./WebHome \_ VELO \_ TWiki_files/newtopic.gif \"New
topic\") Create New Topic\![\](./WebHome \_ VELO \_
TWiki_files/external-link.gif)\](https://lbtwiki.cern.ch/bin/view/VELO/WebCreateNewTopic?parent=WebHome) \![External
link mark\](./WebHome \_ VELO \_ TWiki_files/external.gif) \*
\[\![Index\](./WebHome \_ VELO \_ TWiki_files/index.gif \"Index\")
Index\](https://lbtwiki.cern.ch/bin/view/VELO/WebTopicList) \*
\[\![Search topic\](./WebHome \_ VELO \_ TWiki_files/searchtopic.gif
\"Search topic\")
Search\](https://lbtwiki.cern.ch/bin/view/VELO/WebSearch) \*
\[\![Changes\](./WebHome \_ VELO \_ TWiki_files/changes.gif \"Changes\")
Changes\](https://lbtwiki.cern.ch/bin/view/VELO/WebChanges) \*
\[\![Notify\](./WebHome \_ VELO \_ TWiki_files/notify.gif \"Notify\")
Notifications\](https://lbtwiki.cern.ch/bin/view/VELO/WebNotify) \*
\[\![RSS feed, rounded corners\](./WebHome \_ VELO \_
TWiki_files/feed.gif \"RSS feed, rounded corners\") RSS
Feed\](https://lbtwiki.cern.ch/bin/view/VELO/WebRss) \*
\[\![Statistics\](./WebHome \_ VELO \_ TWiki_files/statistics.gif
\"Statistics\")
Statistics\](https://lbtwiki.cern.ch/bin/view/VELO/WebStatistics) \*
\[\![Wrench, tools\](./WebHome \_ VELO \_ TWiki_files/wrench.gif
\"Wrench, tools\")
Preferences\](https://lbtwiki.cern.ch/bin/view/VELO/WebPreferences)

\* \* \*

\* \*\*Webs\*\* \*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) CALO\](https://lbtwiki.cern.ch/bin/view/CALO/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) Computing\](https://lbtwiki.cern.ch/bin/view/Computing/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) DemoWebsite\](https://lbtwiki.cern.ch/bin/view/DemoWebsite/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) HLT\](https://lbtwiki.cern.ch/bin/view/HLT/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) L0\](https://lbtwiki.cern.ch/bin/view/L0/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) MUON\](https://lbtwiki.cern.ch/bin/view/MUON/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) Main\](https://lbtwiki.cern.ch/bin/view/Main/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) OT\](https://lbtwiki.cern.ch/bin/view/OT/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) Online\](https://lbtwiki.cern.ch/bin/view/Online/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) Operation\](https://lbtwiki.cern.ch/bin/view/Operation/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) RICH\](https://lbtwiki.cern.ch/bin/view/RICH/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) RP\](https://lbtwiki.cern.ch/bin/view/RP/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) ST\](https://lbtwiki.cern.ch/bin/view/ST/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) Sandbox\](https://lbtwiki.cern.ch/bin/view/Sandbox/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) SciFi\](https://lbtwiki.cern.ch/bin/view/SciFi/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) TWiki\](https://lbtwiki.cern.ch/bin/view/TWiki/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) Testbeam\](https://lbtwiki.cern.ch/bin/view/Testbeam/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) UT\](https://lbtwiki.cern.ch/bin/view/UT/WebHome)
\*  \[\![\](./WebHome \_ VELO \_
TWiki_files/web-bg.gif) VELO\](https://lbtwiki.cern.ch/bin/view/VELO/WebHome)

\[\![Home - this site is powered by TWiki(R)\](./WebHome \_ VELO \_
TWiki_files/T-logo-140x40-t.gif)\](https://lbtwiki.cern.ch/bin/view/Main/WebHome)

\*   

\*   

\[\![This site is powered by the TWiki collaboration
platform\](./WebHome \_ VELO \_ TWiki_files/T-badge-88x31.gif \"This
site is powered by the TWiki collaboration
platform\")\](https://twiki.org/) \[\![Powered by Perl\](./WebHome \_
VELO \_ TWiki_files/perl-logo-88x31.gif \"Powered by
Perl\")\](https://www.perl.org/)Copyright � 2008-2025 by the
contributing authors. All material on this collaboration platform is the
property of the contributing authors. Ideas, requests, problems
regarding TWiki? \[Send
feedback\](mailto:?subject=TWiki%20Feedback%20on%20VELO.WebHome)
