% iitbthesis.cls
% LaTeX Style file for the Indian Institute of Bombay Thesis Format
%   by Amey Karkare 2007/06/20
%   according to the guidelines given on the webpage
%   http://gymkhana.iitb.ac.in/~rsf/old/formatthesis.htm
%
% Many commands copied from withesis.cls from
% http://www.ctan.org/tex-archive/macros/latex/contrib/withesis/
%
% Revisions:
% 18/09/2007: Support for  ``External Guide'' added.
%             The changes submitted by: Anil Nair <talk2anil [AT] gmail.com>
%=============================================================================
% Licensed under the Perl Artistic License.
% see: http://www.ctan.org/tex-archive/help/Catalogue/licenses.artistic.html
% for more info...
%=============================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{iitbthesis}[2007/06/25 IIT Bombay Thesis Format]
\typeout{Document Class `iitbthesis' v0.95beta <18 Sept 07>}


%=============================================================================
% TBD: We need options to switch between Annual Progress Report,
%      Presynopsis, Synopsis and final thesis, and between different
%      types of reports.
%=============================================================================
%\DeclareOption{aps}{}
%\DeclareOption{presynopsis}{}
%\DeclareOption{synopsis}{}
%\DeclareOption{thesis}{}
%\DeclareOption{dissertation}{}
%\DeclareOption{project}{}

%=============================================================================
% Pass the options to report class
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}

% Defaults ...
\ProcessOptions

%=============================================================================
% a4paper: thesis must be printed on a4 size paper.
% 12pt:    font size must be 12 pt
%
% As iitbthesis class is a simple extension of report class, we simply
% pass default options to report class.
% =============================================================================
\PassOptionsToClass{12pt,a4paper}{report}
\LoadClass{report}

% who is advisor?
\def\@advisorname{None}
\newcommand{\setguide}[1]{\def\@advisorname{#1}}

% and coadvisor? (initialized to empty)
\global\let\@coadvisorname\@empty
\newcommand{\setcoguide}[1]{\def\@coadvisorname{#1}}
\let\coguide\setcoguide %
\newcommand{\show@coguide}{\@coadvisorname}

% and exadvisor? (initialized to empty)
\global\let\@exadvisorname\@empty
\newcommand{\setexguide}[1]{\def\@exadvisorname{#1}}
\let\exguide\setexguide %
\newcommand{\show@exguide}{\@exadvisorname}

%=============================================================================
% TITLE PAGE
%   - define \title{} \author{} \date{}
%   - The default degree is ``Unknown Degree''
%     Degree can be changed using the command \iitbdegree{}
%   - The default department is ``Unknown Department''
%     The department can be changed using the command \department{}
%   - The default document type is ``A preliminary report''
%     The document type can be changed using the command \reporttype{}
%     There are some short-cuts for \reporttype{}:
%      * for a PhD thesis, specify \thesis
%      * for a M.Tech./M.Phil./M.Des./M.S. dissertation, specify \dissertation
%      * for a DIIT/B.Tech./M.Sc.project report, specify \project
%      * for a preliminary report, specify \prelim
%   - once the above are defined, use \maketitle to generate the titlepage
%=============================================================================
\newcommand\@thesistitlemedskip{0.25in}
\newcommand\@thesistitlebigskip{0.6in}
\newcommand{\rollnum}[1]{\gdef\@rollnum{#1}}
\newcommand{\iitbdegree}[1]{\gdef\@iitbdegree{#1}}
\newcommand{\department}[1]{\gdef\@department{#1}}
\newcommand{\reporttype}[1]{\gdef\@doctype{#1}}
\newcommand{\approvaltype}[1]{\gdef\@approvaltype{#1}}

\newcommand{\thesis}{\reporttype{thesis}\approvaltype{Thesis}}
\newcommand{\dissertation}{\reporttype{dissertation}\approvaltype{Dissertation}}
\newcommand{\project}{\reporttype{project report}\approvaltype{Report}}
\newcommand{\prelim}{\reporttype{preliminary report}\approvaltype{Report}}

\gdef\@rollnum{Unknown 00000000}    % Default is Unknown 00000000
\gdef\@iitbdegree{Unknown Degree}    % Default is Unknown Degree
\gdef\@doctype{preliminary report}  % Default is a preliminary report
\gdef\@department{(Unknown Department)} % Default is Unknown

\renewcommand{\maketitle}{%
  \begin{titlepage}
%-----------------------------------------------------------------------------
% -- The thesis office doesn't like thanks on title page.  Put it in
% -- the acknowledgments.  This is here so you don't have to change
% -- your titlepage when converting from report style. -> from Purdue, but I
%        left it here since it seems compatible with UW-Madison, Eric -
%    Amey - I also left it here as IITB does not say anything about it.
%-----------------------------------------------------------------------------
    \def\thanks##1{\typeout{Warning: `thanks' deleted from thesis titlepage.}}
    \let\footnotesize\small \let\footnoterule\relax \setcounter{page}{1}
    \vspace*{0.1in}
    \begin{center}
      \mbox{}\\
      {\bf\expandafter\uppercase\expandafter{\LARGE\@title}} \\[\@thesistitlebigskip]
%      {\large A \@doctype\ submitted in partial fulfillment of} \\
%      {\large the requirements for the degree of}\\[\@thesistitlemedskip]
      {\large Submitted in partial fulfillment of the requirements} \\
      {\large for the degree of}\\[\@thesistitlemedskip]
      {\large \@iitbdegree} \\[\@thesistitlemedskip]
      {\large by} \\[\@thesistitlemedskip]
      {\large \bf \@author} \\
      {\large \bf (Roll No. \@rollnum)} \\[\@thesistitlebigskip]
      {\large Supervisor }  \\
      {\large \bf \@advisorname} \\
      \ifx\@coadvisorname\@empty
         \ifx\@exadvisorname\@empty
             \mbox{}\\[\@thesistitlebigskip]
	 \else
	     {\large and } \\
	     {\large \bf \@exadvisorname} \\[\@thesistitlemedskip]
	 \fi %
      \else
          \ifx\@exadvisorname\@empty
	      {\large and } \\
	      {\large \bf \@coadvisorname} \\[\@thesistitlemedskip]
	  \else
	      {\large \bf \@coadvisorname} \\%[\@thesistitlemedskip]
	      {\large and } \\
	      {\large \bf \@exadvisorname} \\[\@thesistitlemedskip]
	  \fi %
      \fi %
      \includegraphics[width=1.5in]{logo} \\[\@thesistitlemedskip]
      {\large \uppercase{\@department}} \\%[\@thesistitlemedskip]
      {\large INDIAN INSTITUTE OF TECHNOLOGY BOMBAY}\\%[\@thesistitlemedskip]
      {\large \@date}
    \end{center}
  \end{titlepage}
  \setcounter{footnote}{0}
  \setcounter{page}{1} %title page is NOT counted
}

%=============================================================================
% DEDICATION
%=============================================================================
% The dedication environment must do the following:
% - start a new page
% - center the text vertically
% - include the text in a center environment
%=============================================================================
\def\dedication{
  \newpage
  \thispagestyle{empty}    % No page number
  \setcounter{page}{0}
  % \addtocounter{page}{-1}
  \chapter*{}            % Required for \vfill to work
  \thispagestyle{empty}    % No page number
  \null\vfil
  \begin{center}}
\def\enddedication{\end{center}\par\vfil\newpage}

%=============================================================================
% APPROVAL SHEET
% - start a new page. page
% - center the text vertically
%=============================================================================
\newcommand\@thesisapprovalmedskip{0.2in}
\newcommand\@thesisapprovalbigskip{0.5in}
\newcommand{\makeapproval}{
  %\setcounter{page}{2}
  \cleardoublepage
  \thispagestyle{empty}
  
\begin{center}
{\LARGE \bf \@approvaltype\ Approval}\\[\@thesisapprovalbigskip]
%{\LARGE \bf Approval Sheet}\\[\@thesisapprovalbigskip]
\end{center}
    This \@doctype\ entitled {\bf \@title} by {\@author} (\@rollnum) is approved for the degree of \@iitbdegree\ from the Indian Institute of Technology Bombay. \\[\@thesisapprovalbigskip]
%    {\large The \@doctype\ entitled}\\[\@thesisapprovalmedskip]
%    {\bf\expandafter\uppercase\expandafter{\LARGE\@title}}\\[\@thesisapprovalmedskip]
%    {\large by}\\[\@thesisapprovalmedskip]
%    {\Large \bf \@author }\\
%    {\Large (Roll No. \@rollnum)}\\[\@thesisapprovalmedskip]
%    {\large is approved for the degree of} \\[\@thesisapprovalmedskip]
%    {\large \@iitbdegree } \\[\@thesisapprovalbigskip]
  \begin{center}
    \ifx\@coadvisorname\@empty
    \ifx\@exadvisorname\@empty % no co-advisor/external advisor
    \begin{tabular}{ccc}
      \rule{6cm}{1sp}                &\rule{10mm}{0pt}& \rule{6cm}{1sp} \\
      {\Large Examiner}              && {\Large Examiner} \\[\@thesisapprovalmedskip]\\
      \rule{6cm}{1sp}                && \rule{6cm}{1sp} \\
      {\Large Guide}                 && {\Large Chairman} \\[\@thesisapprovalmedskip]\\
      {\Large Date:} \rule{4cm}{1sp} && \\ && \\
      {\Large Place:} \rule{4cm}{1sp}&&
    \end{tabular}
    \else % only external advisor
    \begin{tabular}{ccc}
      \rule{6cm}{1sp}                & \rule{10mm}{0pt} & \rule{6cm}{1sp} \\
      {\Large Examiner}              && {\Large Examiner} \\[\@thesisapprovalbigskip]\\
      \rule{6cm}{1sp}                && \rule{6cm}{1sp} \\
      {\Large Guide}                 && {\Large External Guide} \\[\@thesisapprovalbigskip]\\
      \multicolumn{3}{c}{\rule{6cm}{1sp}} \\
      \multicolumn{3}{c}{\Large Chairman} \\[\@thesisapprovalbigskip]
      {\Large Date:} \rule{4cm}{1sp} && \\ && \\
      {\Large Place: Mumbai} \rule{4cm}{1sp}&&
    \end{tabular}
    \fi %
    \else % coadvisor
    \ifx\@exadvisorname\@empty % but no external advisor
%    \begin{tabular}{ccc}
%      \rule{6cm}{1sp}                &\rule{10mm}{0pt}& \rule{6cm}{1sp} \\
%      {\Large Examiner}              && {\Large Examiner} \\[\@thesisapprovalmedskip]\\
%      \rule{6cm}{1sp}                && \rule{6cm}{1sp} \\
%      {\Large Guide}                 && {\Large Co Guide} \\[\@thesisapprovalbigskip]\\
%      \multicolumn{3}{c}{\rule{6cm}{1sp}} \\
%      \multicolumn{3}{c}{\Large Chairman} \\[\@thesisapprovalbigskip]
%      {\Large Date:} \rule{4cm}{1sp} && \\ && \\
%      {\Large Place:} \rule{4cm}{1sp}&&
%    \end{tabular}
\begin{tabular}{lll}
      \rule{6cm}{1sp}                &\rule{10mm}{0pt}& \rule{6cm}{1sp} \\
      {Prof. Ashish R. Hota}			&& {Prof. Navin Khaneja }\\
	  {Dept. of Electrical Engg.}		&& {Centre for Systems and Control}\\
	  {IIT Kharagpur}				&& {IIT Bombay}\\
	  {\bf (External Examiner)}			&& {\bf (Internal Examiner)}\\[\@thesisapprovalmedskip]\\
      \rule{6cm}{1sp}                && \rule{6cm}{1sp} \\
      {Prof. Debasish Chatterjee}		&& {Prof. Ravi N. Banavar}\\
	  {Centre for Systems and Control}	&& {Centre for Systems and Control}\\
	  {IIT Bombay}					&& {IIT Bombay}\\
	  {\bf (Supervisor)}						&& {\bf (Co Supervisor)}\\[\@thesisapprovalmedskip]\\
      \multicolumn{3}{l}{\rule{6cm}{1sp}} \\
      \multicolumn{3}{l}{Prof. D. Manjunath}\\%Prof. D. Manjunath}\\
      \multicolumn{3}{l}{Dept. of Electrical Engg.}\\%Dept. of Electrical Engg.}\\
      \multicolumn{3}{l}{IIT Bombay}\\
      \multicolumn{3}{l}{\bf (Chairman)} \\[\@thesisapprovalbigskip]
      {Date:} \rule{4cm}{1sp} && \\ && \\
      {Place:} \rule{4cm}{1sp}&&
    \end{tabular}
    \else % both co-advisor and external advisor
    \begin{tabular}{ccc}
      \rule{6cm}{1sp}                & \rule{10mm}{0pt} & \rule{6cm}{1sp} \\
      {\Large Examiner}              && {\Large Examiner} \\[\@thesisapprovalbigskip]\\
      \rule{6cm}{1sp}                && \rule{6cm}{1sp} \\
      {\Large Guide}                 && {\Large External Guide} \\[\@thesisapprovalbigskip]\\
      \rule{6cm}{1sp}                && \rule{6cm}{1sp} \\
      {\Large Co Guide}              && {\Large Chairman} \\[\@thesisapprovalbigskip]\\
      {\Large Date:} \rule{4cm}{1sp} && \\ && \\
      {\Large Place:} \rule{4cm}{1sp}&&
    \end{tabular}
    \fi %exadvisor empty
    \fi %coadvisor empty

%change ends

  \end{center}
  \let\thanks\relax
  \let\maketitle\relax \let\iitbdegree\relax \let\project\relax \let\prelim\relax
  \let\department\relax
  \gdef\@thanks{}\gdef\@iitbdegree{}\gdef\@doctype{}
  \gdef\@department{}
}

%=============================================================================
% DECLARATION SHEET
% - start a new page. page
% - center the text vertically
%=============================================================================
%\newcommand\@thesisapprovalmedskip{0.2in}
%\newcommand\@thesisapprovalbigskip{0.5in}
\newcommand{\makedeclaration}{
  %\setcounter{page}{3}
  \cleardoublepage
  \thispagestyle{empty}
  \begin{center}
  {\LARGE \bf Declaration}\\[\@thesisapprovalbigskip]
  \end{center}
I declare that this written submission represents my ideas in my own words and where others' ideas or words have been included, I have adequately cited and referenced the original sources. AI-based tools were used strictly for copy editing, language refinement, and assistance with coding for simulations. All outputs generated by such tools were carefully reviewed and verified by the author. I also declare that I have adhered to all principles of academic honesty and integrity and have not misrepresented or fabricated or falsified any idea/data/fact/source in my submission. I understand that any violation of the above will be cause for disciplinary action by the Institute and can also evoke penal action from the sources which have thus not been properly cited or from whom proper permission has not been taken when needed.\\
\vskip 2cm
  \noindent{\hfill \rule{6cm}{1sp}}
\vskip 0cm
  \noindent{\hfill\@author\rule{1cm}{0pt}}\\
% \vskip -1cm
  \indent{\hfill(Roll No. \@rollnum)\rule{1cm}{0pt}}\\
  \noindent{Date : \rule{3cm}{1sp}}\\
%\vskip -1cm
  \noindent{Place : \rule{3cm}{1sp}}\\

  \let\thanks\relax
  \let\maketitle\relax \let\iitbdegree\relax \let\project\relax \let\prelim\relax
  \let\department\relax
  \gdef\@thanks{}\gdef\@iitbdegree{}\gdef\@doctype{}
  \gdef\@department{}
}

%=============================================================================
% CERTIFICATE OF COURSE WORK
%=============================================================================
% joining date is required for certificate of course work
\newcommand{\joiningdate}[1]{\gdef\@joindate{#1}}
\gdef\@joindate{``Unknown''}
%   - define counters for course numbers & credits, initialize to 0
\newcounter{@course}\setcounter{@course}{0}
\newcounter{@credits}\setcounter{@credits}{0}

%   - command to add a course. it accepts 3 arguments:
%     Course ID, Course Name, and Course Credits.
\newcommand{\addcourse}[3]{%
  \addtocounter{@course}{1}
  \the@course & #1 & #2 & #3
  \addtocounter{@credits}{#3} \\\hline}
\newcommand{\addppcourse}[3]{%
  \addtocounter{@course}{1}
  \the@course & #1 & #2 & #3
  \\\hline}

%  - finally the environment to print course list in tabular form
\newenvironment{coursecertificate}{
  \newpage
  %\setcounter{page}{0}
  \cleardoublepage
  \thispagestyle{empty}
  \begin{center}
    {\Large INDIAN INSTITUTE OF TECHNOLOGY BOMBAY, INDIA}\\
    \vspace{.3in}
    {\Large \bf CERTIFICATE OF COURSE WORK}\\
    %\vspace{.3in}
  \end{center}
  {\large This is to certify that {\bf \@author} (Roll No. \@rollnum)
    was admitted to the candidacy of M.Tech. + Ph.D. Dual Degree on \@joindate,
    after successfully completing all the courses required for the M.Tech. + Ph.D. Dual Degree programme. The details of the course work done are given
    below.}\\
  \vspace{.3in}\\
  \begin{tabular}{|r|l|p{10cm}|r|}
    \hline
    {\bf S.No} & {\bf Course Code} & {\bf Course Name} & {\bf Credits}\\
    \hline\hline}% Begining of environment
  {
    \hline
    & & {\bf Total Credits} & {\bf \the@credits} \\ \hline
  \end{tabular}

  \vfill
  {\large
  \begin{tabular}{lp{2.2in}r}
    IIT Bombay &&\\
    Date: & &Dy. Registrar (Academic)
  \end{tabular}} % End of Course Certificate
}


%=============================================================================
% ABSTRACT
%=============================================================================
% The abstract should begin with two single-spaced lines describing
% the author and title in a standard format.  After these lines comes
% the standard abstract.
%=============================================================================
\def\abstract{
  \chapter*{Abstract}
  \addcontentsline{toc}{chapter}{Abstract}
  \relax\markboth{ABSTRACT}{ABSTRACT}}
\def\endabstract{\par\newpage}

%=============================================================================
% COPYRIGHTPAGE
% The copyright must do the following:
% - start a new page with no number
% - place the copyright text centered at the bottom.
%=============================================================================
\def\copyrightpage{
  \newpage
  \thispagestyle{empty}    % No page number
  \setcounter{page}{0}
  % \addtocounter{page}{-1}
  \chapter*{}            % Required for \vfill to work
  \begin{center}
   \vfill
   \copyright\ Copyright by \@author\ \@date\\
   All Rights Reserved
  \end{center}}


%=============================================================================
% GLOSSARY
%=============================================================================
% The glossary environment must do the following:
% - produce the table of contents entry for the glossary
% - start a new page with GLOSSARY centered two inches from the top
%=============================================================================
\def\glossary{
  \chapter*{Glossary}
  \addcontentsline{toc}{chapter}{Glossary}}
\def\endglossary{\par\newpage}

%=============================================================================
% NOMENCLATURE
%=============================================================================
% The nomenclature environment must do the following:
% - produce the table of contents entry for the nomenclature section
% - start a new page with NOMENCLATURE centered two inches from the top
%=============================================================================
\def\nomenclature{
  \chapter*{Nomenclature}
  \addcontentsline{toc}{chapter}{Nomenclature}}
\def\endnomenclature{\par\newpage}

%=============================================================================
% LIST OF SYMBOLS
%=============================================================================
% The list of symbols environment must do the following:
% - produce the table of contents entry for the list of symbols section
% - start a new page with LIST OF SYMBOLS centered two inches from the top
%=============================================================================
\def\listofsymbols{
  \cleardoublepage\phantomsection
  \chapter*{List of Symbols}
  \addcontentsline{toc}{chapter}{List of Symbols}}
\def\endlistofsymbols{\par\newpage}

\def\listofabbrevations{
	\cleardoublepage\phantomsection
	\chapter*{Abbreviations}
	\addcontentsline{toc}{chapter}{Abbreviations}}
\def\endlistofabbrevations{\par\newpage}

%=============================================================================
% VITA
%=============================================================================
% The vita environment must do the following:
% - produce a separator page with the word vita centered
% - produce the table of contents entry for the vita
% - start a new page with VITA centered two inches from the top
%=============================================================================
\def\vita{
  \chapter*{Vita}
  \addcontentsline{toc}{chapter}{Vita}}
\def\endvita{\par\newpage}

%=============================================================================
% ACKNOWLEDGMENTS
%=============================================================================
% The acknowledgments environment must do the following:
% - start a new page with ACKNOWLEDGMENTS centered two inches from the top
%=============================================================================
\def\acknowledgments{
  \chapter*{Acknowledgments}
  \markboth{Acknowledgments}{Acknowledgments}
  \thispagestyle{empty}
  \doublespace}
\def\endacknowledgments{%
  \vskip 2cm
  \noindent{Date: \rule{4cm}{1sp}\hfill\@author\rule{1cm}{0pt}}
  \par\newpage}

%=============================================================================
% \@makecaption{NUMBER}{TEXT} : Macro to make a figure or table caption.
%      NUMBER : Figure or table number--e.g., 'Figure 3.2'
%      TEXT   : The caption text.
%  Macro should be called inside a \parbox of right width, with \normalsize.
%=============================================================================
\long\def\@makecaption#1#2{%
  \vskip\abovecaptionskip
  \sbox\@tempboxa{#1: #2}%
  \ifdim \wd\@tempboxa >\hsize
    \singlespace#1: #2\par
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip}

%=============================================================================
% LIST OF FIGURES; LIST OF TABLES
%  These macros from report.cls have been modified to add entry in the
%  Contents table
%=============================================================================
\renewcommand\listoffigures{%
    \if@twocolumn
      \@restonecoltrue\onecolumn
    \else
      \@restonecolfalse
    \fi
    \cleardoublepage\phantomsection
    \chapter*{\listfigurename}%
    \addcontentsline{toc}{chapter}{\listfigurename}%
      \@mkboth{\MakeUppercase\listfigurename}%
              {\MakeUppercase\listfigurename}%
    \@starttoc{lof}%
    \if@restonecol\twocolumn\fi
    }
\renewcommand\listoftables{%
    \if@twocolumn
      \@restonecoltrue\onecolumn
    \else
      \@restonecolfalse
    \fi
    \cleardoublepage\phantomsection
    \chapter*{\listtablename}%
    \addcontentsline{toc}{chapter}{\listtablename}%
      \@mkboth{%
          \MakeUppercase\listtablename}%
         {\MakeUppercase\listtablename}%
    \@starttoc{lot}%
    \if@restonecol\twocolumn\fi
    }
%=============================================================================
% These commands can be used in the thesis to switch between single
% and double spacing.  This is needed, for instance, in the abstract.
%=============================================================================
\newcommand{\oneskip}{1.0}
\newcommand{\twoskip}{1.5}
\newcommand{\singlespace}
  {\renewcommand{\baselinestretch}{\oneskip}\Large\normalsize}
\newcommand{\doublespace}
  {\renewcommand{\baselinestretch}{\twoskip}\Large\normalsize}

%=============================================================================
% Finally set the various lengths/margins as required by IITB format
% Check out LaTeX Companion for more details.
%=============================================================================
% Paper height & width (A4 paper) - set by a4paper option to report
%\setlength{\paperheight}{297mm}
%\setlength{\paperwidth}{210mm}
% total text area: height & width
\setlength{\textheight}{245mm}
\setlength{\textwidth}{160mm}

\setlength{\headheight}{3mm}
\setlength{\headsep}{12mm}
\setlength{\topmargin}{15mm}
%\setlength{\bottommargin}{15mm}
% left side empty space on odd- & even-numbered pages
\if@twoside
  \typeout{Two side is true}
  \setlength{\oddsidemargin}{30mm}  % for two side printing
  \setlength{\evensidemargin}{20mm}
\else
  \typeout{Two side is false}
  \setlength{\oddsidemargin}{30mm}  % for one side printing
  \setlength{\evensidemargin}{30mm} % odd side margin = even side margin
\fi
\setlength{\hoffset}{-1in} % already accounted for in the margins
\setlength{\voffset}{-1in} % already accounted for in the margins
% line, paragraphs indent & spacing
\setlength{\parindent}{5ex} % indentation 5 characters approx.

\doublespace
%==================================================
% The below formatting was added by Priyadrashan H
%==================================================


%====================================================================
%
% chapter and section heading on each page
%
%====================================================================
\usepackage{fancyhdr}
\pagestyle{fancy}
% with this we ensure that the chapter and section
% headings are in lowercase.
\renewcommand{\chaptermark}[1]{\markboth{#1}{}}
\renewcommand{\sectionmark}[1]{\markright{\thesection\ #1}}
\fancyhf{} % delete current setting for header and footer


\if@twoside
  \fancyhead[LE,RO]{\bfseries\thepage}
  \fancyhead[LO,RE]{\bfseries\leftmark}
\else
  \fancyhead[R]{\bfseries\thepage}
  \fancyhead[L]{\bfseries\leftmark}
\fi
\renewcommand{\headrulewidth}{0.5pt}
\renewcommand{\footrulewidth}{0pt}
\addtolength{\headheight}{0.5pt} % make space for the rule


\fancypagestyle{plain}{%
   \fancyhead{} % get rid of headers on plain pages
   \renewcommand{\headrulewidth}{0pt} % and the line
   \fancyfoot[C]{\thepage}
}


% In the book class when the openany option is not given or in the report class when the openright
% option is given, chapters start at odd-numbered pages, half of the time causing a blank page to be
% inserted. Some people prefer this page to be completely empty, i.e. without headers and footers.
% This cannot be done with \thispagestyle as this command would have to be issued on the
% previous page.
\makeatletter
\def\cleardoublepage{\clearpage\if@twoside \ifodd\c@page\else
  \hbox{}
  \vspace*{\fill}
%   \begin{center}
%     This page intentionally contains only this sentence.
%   \end{center}
  \vspace{\fill}
  \thispagestyle{empty}
  \newpage
  \if@twocolumn\hbox{}\newpage\fi\fi\fi}
\makeatother

%%=====================================================================
%%Note that the hyperlink colours have all been set to black for consistent printing. Should you want to distribute your thesis over the web, then it would be advisable to set these colours to red or something similarly vibrant and exciting.
%
%\usepackage[ps2pdf=true,colorlinks]{hyperref}
%\usepackage[figure,table]{hypcap} % Correct a problem with hyperref
%\hypersetup{
%   bookmarksnumbered,
%   pdfstartview={FitH},
%   citecolor={black},
%   linkcolor={black},
%   urlcolor={black},
%   pdfpagemode={UseOutlines}
%}
%
%%Things get a little messy now as a hack is required to ensure the hyperlinks actually jump to the right place.
\makeatletter
%\newcommand\org@hypertarget{}
%\let\org@hypertarget\hypertarget
%\renewcommand\hypertarget[2]{%
%\Hy@raisedlink{\org@hypertarget{#1}{}}#2%
%} 
\makeatother


%====================================================================
% symbolic footnotes: the symbols * and ** have been removed to avoid
% confusion with the maximal subspaces
% this removal is thesis spacific, others may want to include it
%====================================================================

\makeatletter
\def\@fnsymbol#1{\ensuremath{\ifcase#1\or  \dagger\or \ddagger\or
   \mathsection\or \mathparagraph\or \|\or  \dagger\dagger
   \or \ddagger\ddagger\or \mathsection\mathsection
   \or \mathparagraph\mathparagraph \or \|\|\else\@ctrerr\fi}}
\renewcommand{\thefootnote}{\fnsymbol{footnote}}
\makeatother




%=============================
% Set header height to eliminate fancyhdr warnings
%============================
\setlength{\headheight}{28pt}
\addtolength{\topmargin}{-13pt}

%=============================================================================
% My Publications
%=============================================================================
% The mypubs environment must do the following:
% - start a new page with PUBLICATIONS centered two inches from the top
%=============================================================================
\def\mypubs{
  \chapter*{Publications}
  \markboth{Publications}{Publications}
  \thispagestyle{empty}
  \doublespace}
\def\endmypubs{%
\section*{Journal}
\begin{enumerate}[label={[\arabic*]}, leftmargin=*]
\setcounter{enumi}{0}

\item S. Das, A. Aravind, A. Cherukuri, and D. Chatterjee. ``Near-optimal solutions of convex semi-infinite programs via targeted sampling,'' Annals of Operation Research, vol. \(318\), pp. \(129 \text{-} 146\), July \(2022\).
\newblock DOI: \url{https://doi.org/10.1007/s10479-022-04810-4}.


\item A. Aravind, D. Chatterjee, and A. Cherukuri. `` Cross apprenticeship learning framework: Properties and solution approaches'', IEEE Open Journal of Control Systems, vol.\(2\), pp. \(36\text{-}48\), 2023.
\newblock DOI: \url{https://doi.org/10.1109/OJCSYS.2023.3235248}.

\item A. Aravind, D. Chatterjee, and A. Cherukuri. ``Distributed alternating gradient descent for convex semi-infinite programs over a network,'' IEEE Transactions on Automatic Control, vol. 71, no. 2, pp. \(1008\text{-}1021\), Feb 2026.
\newblock DOI: \url{https://doi.org/10.1109/TAC.2025.3607099}.

\item S. Ganguly, A. Aravind, S. Das, M. Nagahara and D. Chatterjee. ``Sparse robust optimal control in continuous-time: a computationally viable approach''.
\newblock \emph{Submitted to IEEE Transactions of Automatic Control}.
\end{enumerate}

\section*{Conference}
\begin{enumerate}[label={[\arabic*]}, leftmargin=*]
\setcounter{enumi}{0}

\item S. Das, S. Ganguly, A. Aravind, and D. Chatterjee, ``Data-driven distributionally robust MPC via semi-infinite semidefinite programming: an application to finance'', Proc. \(26\text{th}\) International Symposium on Mathematical Theory of Networks \& Systems (MTNS), pp. \(73\text{-}78\), August \(2024\).


\item A. Aravind,  M. T. Toghani, and C. Uribe. ``A Moreau envelope approach for LQR meta-policy estimation,'' Proc. IEEE \(63\text{nd}\) Conference on Decision and Control (CDC), pp.\(415\text{-}420\), December \(2024\).


\end{enumerate}

\vspace{-7mm}

\section*{Patents}
\begin{enumerate}[label={[\arabic*]}, leftmargin=*]
\setcounter{enumi}{0}

\item S. Das, A. Aravind, A. Cherukuri, and D. Chatterjee. ``A global optimization approach to exact solutions of convex semi-infinite programs,'' Granted patent no. \(512296\), Application no. \(202121061723\), March \(2024\).
\end{enumerate}

\vskip 5cm
\par\newpage}


%---------------------------------------------------------------------


%=============================================================================
% END FILE
%=============================================================================
