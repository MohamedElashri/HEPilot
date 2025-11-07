LHCbDetectorAlignment \< LHCb \< TWiki \@import
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
\@import
url(\"https://twiki.cern.ch/twiki/pub/TWiki/TwistyContrib/twist.css\");
// \<!\\\[CDATA\\\[ var styleText = \'\<style type=\"text/css\"
media=\"all\"\>.twikiMakeVisible{display:inline;}.twikiMakeVisibleInline{display:inline;}.twikiMakeVisibleBlock{display:block;}.twikiMakeHidden{display:none;}\</style\>\';
document.write(styleText); // \\\]\\\]\>
.twikiMakeVisible{display:inline;}.twikiMakeVisibleInline{display:inline;}.twikiMakeVisibleBlock{display:block;}.twikiMakeHidden{display:none;}

\[TWiki\](https://twiki.cern.ch/twiki/bin/view/Main/WebHome)\\\>\![\](./LHCbDetectorAlignment
\_ LHCb \_ TWiki_files/web-bg-small.gif) \[LHCb
Web\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebHome)\\\>\[LHCbComputing\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbComputing)\\\>\[LHCbDetectorAlignment\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment
\"Topic revision: 78 (2019-06-06 - 11:55:30)\") (2019-06-06,
\[MichaelAlexander\](https://twiki.cern.ch/twiki/bin/view/Main/MichaelAlexander))
\[\![\](./LHCbDetectorAlignment \_ LHCb \_ TWiki_files/uweb-o14.gif)
Edit\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbDetectorAlignment?t=1762216739;nowysiwyg=1
\"Edit this topic
text\")\[Attach\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbDetectorAlignment
\"Attach an image or document to this
topic\")\[PDF\](https://twiki.cern.ch/twiki/bin/genpdf/LHCb/LHCbDetectorAlignment
\"Create a PDF file for the topic\")

Welcome to the LHCb Alignment Web Page
======================================

\* \[Alignment
Subtasks\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Alignment_Subtasks)
\* \[Tools for
Alignment\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Tools_for_Alignment)
\* \[How
To:\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#How_To)
\* \[Alignment
versions\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Alignment_versions)
\* \[Data sets for
tests\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Data_sets_for_tests)
\*
\[Activities\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Activities)
\* \[Open
tasks\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Open_tasks)
\* \[Useful Detector
Information\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Useful_Detector_Information)
\* \[Hardware Alignment
Systems\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Hardware_Alignment_Systems)
\* \[LHCb Tracking & Alignment Workshops and Other Relevant
Meetings\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#LHCb_Tracking_Alignment_Workshop)
\* \[LHC Detector Alignment
Workshops\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#LHC_Detector_Alignment_Workshops)
\* \[Presentations and
Proceedings\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Presentations_and_Proceedings)
\* \[Publications, public
notes\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Publications_public_notes)
\* \[Subset of relevant non-lhcb
references\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Subset_of_relevant_non_lhcb_refe)
\* \[Tracking and Alignment Plots for
Conference\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Tracking_and_Alignment_Plots_for)
\* \[Old
stuff\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#Old_stuff)

\*\*Alignment Subtasks\*\* \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* Former conveners: Lucia Grillo, Agnieszka Dziurda, Francesco Polci,
Giulio Dujany \* Alignment software: Wouter Hulsbergen, Maurizio
Martinelli \* \[VELO alignment\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://ppewww.ph.gla.ac.uk/LHCb/VeloAlign/):
Silvia Borghi, Giulio Dujany \* \[Tracker
alignment\](https://twiki.cern.ch/twiki/bin/view/LHCb/TAlignmentManual):
Francesca Dordei, Lucia Grillo and Maurizio Martinelli \* TT alignment:
Elena Graverini and Maurizio Martinelli \* IT alignment: Zhirui Xu,
Maxime Schubiger and Maurizio Martinelli \* \[OT
alignment\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbTStationAlignment),
\[OTMonoLayerAlignment\](https://twiki.cern.ch/twiki/bin/view/LHCb/OTMonoLayerAlignment):
Wouter Hulsbergen \* Muon alignment: Stefania Vecchi \* \[RICH Mirror
Alignment\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbRichMirrorAlign):
Paras Naik, Claire Prouve, Anatoly Solomin \*
\[AlignmentMonitoring\](https://twiki.cern.ch/twiki/bin/view/LHCb/AlignmentMonitoring)
\* \[Open Alignment
Tasks\](https://twiki.cern.ch/twiki/bin/view/LHCb/TrackingTaskList) \*
\[Alignment problems database\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://lbproblems.cern.ch/search/?system=36)

\*\*Tools for Alignment\*\*
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* \[Introduction to running the
Alignment\](https://twiki.cern.ch/twiki/bin/view/LHCb/AlignmentIntro) \*
\[Alignment DB Monitoring
Tools\](https://twiki.cern.ch/twiki/bin/view/LHCb/DBVisualisationTool)
\* \[Manual for alignment framework
(\'Kalman\')\](https://twiki.cern.ch/twiki/bin/view/LHCb/TAlignmentManual)
\* \[Geometry
Framework\](https://twiki.cern.ch/twiki/bin/view/LHCb/GeometryFramework)
\* \[Protocol for uploading new calibration and alignment constants from
CAF
jobs\](https://twiki.cern.ch/twiki/bin/view/LHCb/CalibrationUploadProtocol)

\*\*How To:\*\* \-\-\-\-\-\-\-\-\-\--

\* \[How to run the online alignment
(2015+)\](https://twiki.cern.ch/twiki/bin/view/LHCb/OnlineAlignmentHowTo)
\* \[\*\*Alignment piquet\'s reference:\*\* how to solve most common
problems with automatic VELO and tracker
alignment\](https://twiki.cern.ch/twiki/bin/view/LHCb/AlignmentPiquetInstruction)
\* \[Check consistency between conditions used online and
offline.\](https://twiki.cern.ch/twiki/bin/view/LHCb/CheckOnlineOfflineConditions)

\* \[Test the online alignment
procedure.\](https://twiki.cern.ch/twiki/bin/view/LHCb/HowToRunAlignmentTestOnline)
\* \[Time table for using of the HLT farm in 2017 Winter
Shutdown\](https://twiki.cern.ch/twiki/bin/view/LHCb/TimeTableOnlineAlignFarm2017)

\* \[How to develop Alignment
software\](https://twiki.cern.ch/twiki/bin/view/LHCb/AlignmentDevelopment)

\* \[Various How To\'s with the Conditions
Database\](https://twiki.cern.ch/twiki/bin/view/LHCb/CondDBHowTo) \*
\[HowToCreateCondDB\](https://twiki.cern.ch/twiki/bin/view/LHCb/HowToCreateCondDB):
How to Create a local copy of the Conditions Database \*
\[HowToBrowseCondDB\](https://twiki.cern.ch/twiki/bin/view/LHCb/HowToBrowseCondDB):
How to Browse the Conditions Database (LHCBCOND.db) \* \[How to create a
misaligned Conditions
DB\](https://twiki.cern.ch/twiki/bin/view/LHCb/MisAlignedCond) \*
\[Access bookkeeping DB
(fast)\](https://twiki.cern.ch/twiki/bin/view/LHCb/AccessBKDatabase)

\* How to access the \[energy deposit in the
calorimeters\](https://twiki.cern.ch/twiki/bin/view/LHCb/EnergyDepositInCalorimeters)
(e.g. to get a momentum estimate for magnet-off runs) \* \[Solve warning
and errors from the
nightlies\](https://twiki.cern.ch/twiki/bin/view/LHCb/HowToSolveWarningAndErrorsNightlies)
\* \[Check
QMTests\](https://twiki.cern.ch/twiki/bin/view/LHCb/HowToCheckQMT) \*
\[Add histograms to the online monitoring
presenter\](https://twiki.cern.ch/twiki/bin/view/LHCb/OnlinePresenter)

\*\*Alignment versions\*\* \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* \[CondDB and Alignment version used in the
HLT\](https://twiki.cern.ch/twiki/bin/view/LHCb/Hltalignment).

\* List of 2010 alignment versions:
\[link\](https://twiki.cern.ch/twiki/bin/view/LHCb/2010alignment).

\* List of 2011 alignment versions:
\[link\](https://twiki.cern.ch/twiki/bin/view/LHCb/2011alignment). List
and time range of the fill: \[link\![\](./LHCbDetectorAlignment \_ LHCb
\_
TWiki_files/external-link.gif)\](http://lhcb-operationsplots.web.cern.ch/lhcb-operationsplots/index_files/2011OperationsDashboard.htm)

\* List of 2012 alignment versions:
\[link\](https://twiki.cern.ch/twiki/bin/view/LHCb/2012alignment). List
and time range of the fill: \[link\![\](./LHCbDetectorAlignment \_ LHCb
\_
TWiki_files/external-link.gif)\](http://lhcb-operationsplots.web.cern.ch/lhcb-operationsplots/index_files/2012OperationsDashboard.htm)

\* List of 2015 alignment versions:
\[link\](https://twiki.cern.ch/twiki/bin/view/LHCb/2015alignment). List
and time range of the fill: \[link\![\](./LHCbDetectorAlignment \_ LHCb
\_
TWiki_files/external-link.gif)\](https://lbgroups.cern.ch/online/OperationsPlots/2015OperationsDashboard.htm)

\* Late 2015 and 2016 on: The automatic update of the constants was
switched on the 23/10/2015 for the VELO and the 3/11/2015 for the
Tracker, more information and monitoring plots can be found in the
\[logbook\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://lblogbook.cern.ch/Alignment+monitoring/)
. List and time range of the fill: \[link\![\](./LHCbDetectorAlignment
\_ LHCb \_
TWiki_files/external-link.gif)\](https://lbgroups.cern.ch/online/OperationsPlots/2016OperationsDashboard.htm)

\*\*Data sets for tests\*\*
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

Here are a few data sets available for testing:

\* \*\*Data 2011\*\*: \$ESCHEROPTS/COLLISION11.py \* \*\*Data 2012\*\*:
\$ESCHEROPTS/COLLISION12.py \* \*\*Data 2015\*\*:
/afs/cern.ch/user/m/mamartin/public/forWouter/r166277\\\_Calibration.py

\*\*Activities\*\* \-\-\-\-\-\-\-\-\-\-\-\-\--

See link to the \[Activities
List\](https://twiki.cern.ch/twiki/bin/view/LHCb/TrackingActivitiesList).

\*\*Open tasks\*\* \-\-\-\-\-\-\-\-\-\-\-\-\--

See link to the \[Open tracking and alignment
tasks\](https://twiki.cern.ch/twiki/bin/view/LHCb/TrackingTaskList).

\*\*Useful Detector Information\*\*
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* \[Tracker Turicensis\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/317459/contribution/0/material/slides/1.pdf)
\* \[Inner Tracker\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/280296/contribution/0/material/slides/0.pdf)
\* \[Outer Tracker\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/317507/contribution/3/material/slides/1.pdf)

\*\*Hardware Alignment Systems\*\*
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* \*\*RASNIK system\*\*: \* \[RASNIK System for Outer Tracker, June
2007 (LHCb password
required)\](http://phy.syr.edu/\~lhcb/restricted/alignment/Docs/RASNIKnote.pdf)
\* \[CDS Notes\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/) \* \*\*RICH
Laser Alignment System\*\* \* \[Ph.D. Thesis by Andres
Macgregor\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://ppewww.physics.gla.ac.uk/\~lcarson/MacGregorThesis.ps)
\* \*\*IT BCAM\*\*: \* \[IT monitoring using BCAM
intersections\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/363159/contribution/0/material/slides/1.pdf)
\* \[BCAM results with both polarity\![\](./LHCbDetectorAlignment \_
LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/event/317507/contribution/1/material/slides/0.pdf)

\*\*LHCb Tracking & Alignment Workshops and Other Relevant Meetings\*\*
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* All the meetings can be found at this
\[page\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](https://indico.cern.ch/categoryDisplay.py?categId=2l60)
\* \[Jun 3-4 2010: Tracking and Alignment Workshop @
CERN\](https://indico.cern.ch/conferenceDisplay.py?confId=93325) \*
\[Jan 28-29 2010: Tracking and Alignment Workshop @
CERN\](https://indico.cern.ch/conferenceDisplay.py?confId=74689) \*
\[Jul 10 2009: Tracking and Alignment Workshop @
CERN\](https://indico.cern.ch/conferenceDisplay.py?confId=62985) \*
\[Feb 16-18 2009: Tracking and Alignment Workshop @
Heidelberg\](https://indico.cern.ch/conferenceDisplay.py?confId=50859)
\* \[Jun 10-12 2008: Tracking and Alignment Workshop @
CERN\](https://indico.cern.ch/conferenceDisplay.py?confId=33862) \*
\[April 7-11, 2008: Alignment working week 3 @
CERN\](http://indico.cern.ch/conferenceDisplay.py?confId=30486) \* \[Feb
27-29, 2008: Tracking & Alignment Workshop @
Ferarra\](http://indico.cern.ch/conferenceDisplay.py?confId=26985) \*
\[Feb 11-15, 2008: Alignment Working Week 2 @
CERN\](http://indico.cern.ch/conferenceDisplay.py?confId=28916%20target%20=)
\* \[Jan 7-11, 2008: Alignment Working Week 1 @
CERN\](http://indico.cern.ch/conferenceDisplay.py?confId=26265%20target%20=)
\* \[Aug 29-31, 2007: Tracking & Alignment Workshop @
Amsterdam\](http://indico.cern.ch/conferenceDisplay.py?confId=19148) \*
\[Aug 3, 2007: Alignment Meeting @
CERN\](http://indico.cern.ch/conferenceDisplay.py?confId=12738) \* \[Feb
22-23, 2007: Tracking & Alignment Workshop @
Heidelberg\](http://indico.cern.ch/conferenceDisplay.py?confId=12233) \*
\[Nov 8-9, 2006: Tracking & Alignment Workshop @
Lausanne\](http://indico.cern.ch/conferenceDisplay.py?confId=6850) \*
\[July 13-14, 2006: Tracking Workshop @
Zurich\](http://indico.cern.ch/conferenceDisplay.py?confId=3642) \*
\[Jan 12-13, 2006: @ Alignment Workshop @
Cambridge\](http://indico.cern.ch/conferenceDisplay.py?confId=a058473)
\* \[Oct 31-Nov 1, 2005: Tracking & Alignment Workshop @
Glasgow\](http://indico.cern.ch/conferenceDisplay.py?confId=a054721)

\*\*LHC Detector Alignment Workshops\*\*
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* \[LHC Detector Alignment Workshop - 3, Sept 15-16
2009\](http://indico.cern.ch/conferenceDisplay.py?confId=50502/) \*
\[LHC Detector Alignment Workshop - 2, June 25-26,
2007\](http://physics.syr.edu/\~lhcb/public/alignment/LHCAlignmentWorkshop/)
\* \[LHC Detector Alignment Workshop - 1, Sept 4-6
2006\](http://physics.syr.edu/\~lhcb/public/alignment/LHCAlignmentWorkshop1/)

\*\*Presentations and Proceedings\*\*
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* Survey Task Force Reports, May 2007 Software Week
\[slides\](http://indico.cern.ch/conferenceDisplay.py?confId=10728) \*
J. Palacios Local-to-global transformations, and Marco Clemencic, on
implementation of Survey data into Geom DB or Cond DB, presented at
T-REC Meeting
\[slides\](http://indico.cern.ch/conferenceDisplay.py?confId=10161) \*
W. Hulsbergen on alignment with Kalman filter tracks in the LHC
alignment workshop
\[slides\](http://indico.cern.ch/getFile.py/access?contribId=28&sessionId=10&resId=1&materialId=slides&confId=13681)
\* L. Nicolas, Tracking stations alignment with Kalman tracks at LHCb,
presented at : 2008 IEEE, 2008
\[slides\](https://cdsweb.cern.ch/record/1293646/files/louis_dresden%5B1%5D.pdf)
\* M. Gersabeck, Alignment of the LHCb VErtex LOcator, presented at :
10th International Conference on Instrumentation for Colliding Beam
Physics,
2008\[slides\](https://cdsweb.cern.ch/record/1293582/files/gersabeck_velo_alignment.pdf)
\[slides\](http://cdsweb.cern.ch/record/1314528/files/VERTEX%202010_014.pdf%3Eproceeding%3C/a%3E%3C/li%3E%20%3Cli%3E%20W.%20Hulsbergen,%20Rigorous%20integration%20of%20Kalman%20filter%20track%20fit%20into%20alignment,%20presented%20at%203rd%20LHC%20Detector%20Alignment%20Workshop%202009,%20%3Ca%20href%20=)
\* E. Rodrigues, Impact of misalignment on beauty physics at LHCb,
presented at 3rd LHC Detector Alignment Workshop 2009
\[slides\](http://indico.cern.ch/getFile.py/access?contribId=20&sessionId=5&resId=0&materialId=slides&confId=50502)
\* J. Blouw, The LHCb alignment and alignment monitoring framework,
presented at 3rd LHC Detector Alignment Workshop 2009
\[slides\](http://indico.cern.ch/getFile.py/access?contribId=24&sessionId=6&resId=0&materialId=slides&confId=50502)
\* C. Salzmann, LHCb silicon detector alignment with first LHC beam
induced track, presented at 3rd LHC Detector Alignment Workshop 2009
\[slides\](http://indico.cern.ch/getFile.py/access?contribId=11&sessionId=2&resId=0&materialId=slides&confId=50502)
\* M. Deissenroth, LHCb T-station detectors alignment with cosmics,
presented at 3rd LHC Detector Alignment Workshop 2009
\[slides\](http://indico.cern.ch/getFile.py/access?contribId=12&sessionId=2&resId=0&materialId=slides&confId=50502)
\* S. Pozzi, LHCb Muon detector alignment with cosmics, presented at 3rd
LHC Detector Alignment Workshop 2009
\[slides\](http://indico.cern.ch/getFile.py/access?contribId=13&sessionId=3&resId=0&materialId=slides&confId=50502)
\* F. Maciuc, Tracking and Alignment in LHCb, presented at Physics at
the LHC2010, 2010
\[slides\](https://cdsweb.cern.ch/record/1272411/files/LHCb-TALK-2010-065.pdf)
\* S. Borghi, Tracking and alignment performance of LHCb silicon
detectors, presented at International Workshop on Vertex Detectors, 2011
\[slides\](https://cdsweb.cern.ch/record/1364610/files/LHCb-TALK-2011-129.pdf)
\[proceeding\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/1404194/files/LHCb-PROC-2011-086.pdf)
\* F. Dupertuis, A Novel Alignment Procedure and Results for the LHCb
Silicon Tracker Detector, presented at 2011 IEEE Nuclear Science
Symposium and Medical Imaging Conference, 2011
\[slides\](https://cdsweb.cern.ch/record/1399543/files/LHCb-TALK-2011-229.pdf)
\[proceeding\](http://cdsweb.cern.ch/record/1401794/files/LHCb-PROC-2011-081.pdf)
\* R. M�rki, Alignment of the LHCb tracking system presented at 13th
ICATPP Conference on Astroparticle, Particle, Space Physics and
Detectors for Physics Applications, 2011
\[slides\](https://cdsweb.cern.ch/record/1414760/files/LHCb-TALK-2011-255.pdf)
\[proceeding\](http://cdsweb.cern.ch/record/1414763/files/LHCb-PROC-2012-002.pdf)

More recents talks and proceeding are at
\[link\](https://twiki.cern.ch/twiki/bin/view/LHCb/PreviousTalks)

\*\*Publications, public notes\*\*
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* J. Amoraal et al., \"Application of vertex and mass constraints in
track-based alignment\", \[Nuclear Inst. and Methods in Physics
Research, A 712 (2013), pp. 48-55\![\](./LHCbDetectorAlignment \_ LHCb
\_
TWiki_files/external-link.gif)\](http://www.sciencedirect.com/science/article/pii/S0168900213001861),
doi:10.1016/j.nima.2012.11.192
\[arXiv:1207.4756\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://arxiv.org/abs/1207.4756) \* S.
Borghi et al., \"First spatial alignment of the LHCb VELO and analysis
of beam absorber collision data\", Nucl. Instrum. Methods Phys. Res., A
618 (2010) 108-120, \[PDF\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/1352722/files/TedArtOnline.pdf)
\* M. Needham, \"First alignment of the Inner Tracker using data from
the TI-8 sector test\", \[LHCb-2009-030 ; CERN-LHCb-2009-030 ;
LPHE-Note-2009-02\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/1163364?ln=en)
\* L. Nicolas et al, \"Alignment of LHCb tracking stations with tracks
fitted with a Kalman filter\", \[LHCb-2008-066 ;
CERN-LHCb-2008-066\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/1142717?ln=en)
\* L. Nicolas et al, \"First studies of T-station alignment with
simulated data\", \[LHCb-2008-065 ;
CERN-LHCb-2008-065\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/1142716?ln=en)
\* J. Amoraal, \"Alignment of the LHCb detector with Kalman filter
fitted tracks.\" LHCb-CONF-2009-026; CERN-LHCb-CONF-2009-026 \* M.
Deissenroth, \"Experience with LHCb alignment software on first data\"
LHCb-CONF-2009-009; CERN-LHCb-CONF-2009-009 \* A. Hicheur, M. Needham,
L. Nicolas, , J. Amoraal, W. Hulsbergen, G. Raven, , \"First studies of
T-station alignment with simulated data.\", CERN-LHCB-2008-065, Mar
2009. 35pp. \* L. Nicolas, A. Hicheur, M. Needham, J. Amoraal, W.
Hulsbergen, G. Raven, \"Alignment of LHCb tracking stations with tracks
fitted with a Kalman filter\", CERN-LHCB-2008-066, LPHE-2008-14, Dec
2008. 6pp. \* W. Hulsbergen, \"The Global covariance matrix of tracks
fitted with a Kalman filter and an application in detector alignment.\",
\[Nucl.Instrum.Meth.A600:471-477,2009\![\](./LHCbDetectorAlignment \_
LHCb \_
TWiki_files/external-link.gif)\](http://www.sciencedirect.com/science/article/pii/S0168900208017567).
doi:10.1016/j.nima.2008.11.094,
\[arXiv:0810.2241\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://arxiv.org/abs/0810.2241)
\\\[physics.ins-det\\\] \* S. Viret, C. Parkes, M. Gersabeck,
\"Alignment procedure of the LHCb Vertex Detector\", \[Nucl. Instr. and
Meth. A596 (2008) 157-163\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://www.sciencedirect.com/science/article/pii/S0168900208011212),
doi:10.1016/j.nima.2008.07.153
\[arXiv:0807.5067\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://arxiv.org/abs/0807.5067) \* M.
Gersabeck et al., \"Performance of the LHCb Vertex Detector Alignment
Algorithm determined with Beam Test Data\", \[Nucl. Instr. and Meth.
A596 (2008) 164-171\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://www.sciencedirect.com/science/article/pii/S0168900208011224),
doi:10.1016/j.nima.2008.07.154
\[arXiv:0807.5069\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://arxiv.org/abs/0807.5069)

\*\*Subset of relevant non-lhcb references\*\*
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\* \[V. Blobel, \"Software alignment for tracking detectors\"
(2006)\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://www.slac.stanford.edu/spires/find/hep/www?j=NUIMA,A566,5).
Publication for millepede \* \[V. Blobel, \"Alignment algorithms\"
(2007)\](http://www.slac.stanford.edu/spires/find/hep/www?key=7543093):
Overview of different alignment algorithms for the LHC alignment
workshop \* \[P. Bruckman, A. Hicheur and S.J. Haywood, \"Global chi2
apprach to the alignment of the ATLAS silicon tracking
detectors\"\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/835270) :
another formulation of the closed form alignment approach \* \[A. Bocci
and W. Hulsbergen, \"TRT Alignment For SR1 Cosmics and Beyond\"
(2007)\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/external-link.gif)\](http://cdsweb.cern.ch/record/1039585):
alternative (short) formulation of the closed-form alignment approach.

\*\*Tracking and Alignment Plots for Conference\*\*
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--

\[https://twiki.cern.ch/twiki/bin/view/LHCb/ConferencePlots\](https://twiki.cern.ch/twiki/bin/view/LHCb/ConferencePlots)

\*\*Old stuff\*\* \-\-\-\-\-\-\-\-\-\-\-\--

\* 2010
\[AlignmentOpenIssues\](https://twiki.cern.ch/twiki/bin/view/LHCb/AlignmentOpenIssues)
\* Old Data sets \* \[Alignment
Samples\](https://twiki.cern.ch/twiki/bin/view/LHCb/AlignmentSamples) \*
\[Special Data Sets for
Alignment\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignmentDataSets)
\* \[Bookkeeping
Database\](http://lhcbbk.cern.ch/BkkWeb/Bkk/welcome.htm) \* \[Alignment
databases\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignmentDatabases)
\* \[How to use the GUI for the Offline Alignment
Monitoring\](https://twiki.cern.ch/twiki/bin/view/LHCb/HowToUseTheGUIForTheOfflineAlignmentMonitoring)

\\\--
\[StevenBlusk\](https://twiki.cern.ch/twiki/bin/view/Main/StevenBlusk) -
13 Nov 2006

\[\![\](./LHCbDetectorAlignment \_ LHCb \_ TWiki_files/uweb-o14.gif)
Edit\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbDetectorAlignment?t=1762216739;nowysiwyg=1
\"Edit this topic
text\") \| \[Attach\](https://twiki.cern.ch/twiki/bin/attach/LHCb/LHCbDetectorAlignment
\"Attach an image or document to this topic\") \| \[Print
version\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment?cover=print
\"Printable version of this
topic\") \| \[History\](https://twiki.cern.ch/twiki/bin/oops/LHCb/LHCbDetectorAlignment?template=oopshistory
\"View total topic history\"):
r78 \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbDetectorAlignment?rev1=78;rev2=77) \[r77\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment?rev=77) \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbDetectorAlignment?rev1=77;rev2=76) \[r76\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment?rev=76) \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbDetectorAlignment?rev1=76;rev2=75) \[r75\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment?rev=75) \[\<\](https://twiki.cern.ch/twiki/bin/rdiff/LHCb/LHCbDetectorAlignment?rev1=75;rev2=74) \[r74\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment?rev=74) \| \[Backlinks\](https://twiki.cern.ch/twiki/bin/oops/LHCb/LHCbDetectorAlignment?template=backlinksweb
\"Search the LHCb Web for topics that link to here\") \| \[Raw
View\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment?raw=on
\"View raw text without
formatting\") \| \[WYSIWYG\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbDetectorAlignment?t=1762216739;nowysiwyg=0
\"WYSIWYG editor\") \| \[More topic
actions\](https://twiki.cern.ch/twiki/bin/oops/LHCb/LHCbDetectorAlignment?template=oopsmore&param1=78&param2=78
\"Delete or rename this topic; set parent topic; view and compare
revisions\")

Topic revision: r78 - 2019-06-06
\[\\-\](https://twiki.cern.ch/twiki/bin/edit/LHCb/LHCbDetectorAlignment?t=1762216739;nowysiwyg=1)
\[MichaelAlexander\](https://twiki.cern.ch/twiki/bin/view/Main/MichaelAlexander)

\![\](./LHCbDetectorAlignment \_ LHCb \_ TWiki_files/person.gif)
\[YagnaSwaroopDhurbhakula\](https://twiki.cern.ch/twiki/bin/edit/Main/YagnaSwaroopDhurbhakula?topicparent=LHCb.LHCbDetectorAlignment;nowysiwyg=1
\"this topic does not yet exist; you can create it.\")
\![Lock\](./LHCbDetectorAlignment \_ LHCb \_ TWiki_files/lock.gif
\"Lock\") \[Log
Out\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment?logout=1)

\* \[\![Web background\](./LHCbDetectorAlignment \_ LHCb \_
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

\[\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/toggleopen.gif)Public
webs\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#)
\[\![\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/toggleclose.gif)Public
webs\](https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbDetectorAlignment#)

\* \[ABATBEA\](https://twiki.cern.ch/twiki/bin/view/ABATBEA/WebHome) \*
\[ACPP\](https://twiki.cern.ch/twiki/bin/view/ACPP/WebHome) \*
\[ADCgroup\](https://twiki.cern.ch/twiki/bin/view/ADCgroup/WebHome) \*
\[AEGIS\](https://twiki.cern.ch/twiki/bin/view/AEGIS/WebHome) \*
\[AfricaMap\](https://twiki.cern.ch/twiki/bin/view/AfricaMap/WebHome) \*
\[AgileInfrastructure\](https://twiki.cern.ch/twiki/bin/view/AgileInfrastructure/WebHome)
\* \[ALICE\](https://twiki.cern.ch/twiki/bin/view/ALICE/WebHome) \*
\[AliceEbyE\](https://twiki.cern.ch/twiki/bin/edit/AliceEbyE/WebHome?topicparent=LHCb.LHCbDetectorAlignment;nowysiwyg=1
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

\[\![CERN\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/logo_lhcb.png)\](https://twiki.cern.ch/twiki/bin/view/LHCb/WebHome)

\*   

\* \* \![TWiki Search Icon\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/twikisearchicon.gif) TWiki Search \* \![Google Search
Icon\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/googlesearchicon.png) Google Search

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
platform\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/T-badge-88x31.gif \"This site is powered by the TWiki
collaboration platform\")\](http://twiki.org/) \[\![Powered by
Perl\](./LHCbDetectorAlignment \_ LHCb \_
TWiki_files/perl-logo-88x31.gif \"Powered by
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
