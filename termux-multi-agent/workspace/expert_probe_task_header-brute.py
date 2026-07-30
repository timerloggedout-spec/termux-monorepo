[32m""[0m"
Investigation task: Find the correct version header to unlockpython Expert model.
Strateg
[32m""[0m"
ies:
  -Investigation task header-brute: Find the correct: brute-force common version header to unlock version patterns
  Expert model.
Strateg - js-exties:
  -ract: parse header-brute the web JS: brute-force bundle for version common version patterns strings
 
  - wasm-re - js-extractverse: extract version: parse the gate from deepseek web JS bundle for.wasm via strings version strings
 
  - mit - wasm-rem-sniffverse: capture: extract real version gate from deepseek browser headers [1m([0mneeds mitmproxy working[1m)[0m
Success criterion.wasm via strings:
 chat  - mitm-sniff: capture real_completion returns non browser headers [1m([0mne-"Update toeds mitmproxy working[1m)[0m
Success criterion: chat_com latest version" response.
[32m""[0m"
TASK =pletion "ex returns nonpert-"_version_unlockUpdate to latest version"

import" response.
[32m""[0m"
 reTASK = "expert_version_unlock"

import itertools
import requests

import json
import requests
fromfrom path typing importlib import Path Dict,
from Optional typing import, Optional List
, List, Dictfrom dat, Any


aclasses import datdef extractaclass
from_ concurrentversions_from_.futures importjs[1m([0m ThreadPoolExecutor,js_content as_completed

: str[1m)[0m@dataclass -> List[1m[[0mstr
class Br[1m][0m:
    [32m""[0m"uteResultExtract version:
    version strings: str from JavaScript
    success content: bool
   .[32m""[0m"
    patterns response_pre = [1m[[0m
        rview': str

classversion[1m[[0m" Expert\'[1m][0mVersionBr?\s*[1m[[0m:ute=[1m][0m\s*Forcer[1m[[0m"\'[1m][0m:
    [32m""[0m"
[1m([0m[1m[[0m\    Brd.ute-force version[1m][0m+[1m)[0m[1m[[0m"\'[1m][0m headers',
        r to'[1m[[0m" unlock Expert model\'[1m][0mv?[1m([0m\.
d+   \.\ Uses common patternsd+\.\ and knownd+[1m)[0m[1m[[0m"\ version'[1m][0m',
        r strings'client.
   Version [32m""[0m"
    
    COMM[1m[[0m"ON_V\'[1m][0m?\s*[1m[[0m:ERSIONS = [1m[[0m
        "[1;36m202[0m=[1m][0m\s[1;36m5[0m*[1m[[0m"\'[1m][0m-[1;36m01[0m[1m([0m[1m[[0m\d.[1m][0m+-[1;36m01[0m[1m)[0m[1m[[0m"\'[1m][0m",
',
        r'        "[1;36m202[0m[1;36m5[0mapi-[1;36m02[0mVersion[1m[[0m"-[1;36m15[0m\'[1m][0m?\s",
*[1m[[0m:=[1m][0m\        "[1;36m202[0m[1;36m5[0ms-*[1;36m03[0m-[1m[[0m"[1;36m01[0m\'[1m][0m[1m([0m[1m[[0m\d",
        "[1;36m202[0m.[1m][0m+[1m)[0m[1m[[0m"[1;36m4[0m-[1;36m12[0m\'[1m][0m',
        r'[1m[[0m"\'[1m][0m[1m([0m\-[1;36m25[0m",
        "d[1;36m202[0m+\.[1;36m5[0m-[1;36m04[0m-[1;36m01[0m\d+\.",
        "[1;36m202[0m\d+[1;36m5[0m-[1;36m05[0m\.-[1;36m01[0m",
       \ "[1;36m202[0m[1;36m5[0md+[1m)[0m[1m[[0m"\-[1;36m06[0m-[1;36m01[0m'[1m][0m',
    [1m][0m
",
        "[1;36m202[0m    
    versions =[1;36m4[0m-[1;36m11[0m set[1m([0m[1m)[0m
    for-[1;36m01[0m pattern in patterns:
",
        "[1;36m202[0m        matches[1;36m5[0m-[1;36m07[0m = re.findall-[1;36m01[0m",
        "[1m([0mpattern[1;36m202[0m, js[1;36m5[0m-_content[1m)[0m
       [1;36m08[0m-[1;36m01[0m",
 versions.update[1m([0mmatches[1m)[0m
    
    return sorted[1m([0mversions,    [1m][0m
    
    VERSION_PATTERNS = [1m[[0m
        " key=lambda vv:[1m{[0m [1m[[0mint[1m([0mx[1m}[0m.[1m)[0m for x in[1m{[0m[1m}[0m v.split[1m([0m'.",
        "[1m{[0m[1m}[0m.[1m{[0m[1m}[0m",
        "[1m{[0m'[1m)[0m[1m][0m, reverse=[3;92mTrue[0m[1m)[0m


def fetch_[1m}[0m.js[1m{[0m_b[1m}[0m.[1m{[0m[1m}[0mundle[1m([0murl: str[1m)[0m ->",
        "v Optional[1m[[0mstr[1m][0m:
   [1m{[0m [32m""[0m"Fetch JavaScript[1m}[0m.[1m{[0m bundle from[1m}[0m.[1m{[0m[1m}[0m given",
        " URL.[32m""[0m"
    try[1m{[0m[1m}[0m:
        response =",
 requests   .get[1m([0murl, [1m][0m
 timeout    
=    C[1;36m10[0m[1m)[0m
AND        response.raise_for_status[1m([0m[1m)[0m
       IDATE return response.text_SU
FF    exceptIXES Exception = [1m[[0m
        [32m""[0m,
        "- as e:
        print[1m([0mf"Failedstable to fetch [1m{[0m",
        "-betaurl[1m}[0m: [1m{[0me",
        "-rc[1m}[0m"[1m)[0m
        return [3;35mNone[0m",
        "-latest


def scan",
        "-ex_localpert",
        "-_jspro_files",
       [1m([0md "-finalirectory: Path[1m)[0m",
    [1m][0m
    
 -> Dict    def __init[1;35m__[0m[1m([0mself, base_url: str[1m[[0mstr =, List[1m[[0mstr[1m][0m[1m][0m:
    [32m""[0m" "httpsScan local:[35m/[0m[35m/[0mchat.deepseek.com[35m/[0m[95mapi[0m .js[35m/[0m files forchat version strings.[32m""[0m"
", timeout    results = [1m{[0m[1m}[0m
   : int = [1;36m5[0m[1m)[0m:
        for self js_file in directory.base.r_url = baseglob[1m([0m"*._url
        selfjs"[1m)[0m:
        try.timeout = timeout:
            content =
        self.session js_file.read_text = requests.Session[1m([0mencoding='utf[1m([0m[1m)[0m
        self-.session[1;36m8[0m',.headers errors.update='[1m([0m[1m{[0m
           ignore'[1m)[0m
 "User-Agent            versions = extract": "Mozilla_versions_from_[35m/[0m[1;36m5[0m.[1;36m0[0mjs[1m([0mcontent[1m)[0m
            [1m([0mWindows NT  if versions:
               [1;36m10[0m.[1;36m0[0m; results[1m[[0mstr Win[1;36m64[0m; x[1m([0mjs_file[1m)[0m[1m][0m[1;36m64[0m[1m)[0m AppleWeb = versions
       Kit[35m/[0m[1;36m537[0m. except Exception[1;36m36[0m",
            " as e:
           Accept": "application print[1m([0mf"Error[35m/[0m[95mjson[0m",
            " reading [1m{[0mjs_fileContent-Type": "[1m}[0m: [1m{[0me[1m}[0m"[1m)[0m
application[35m/[0m[95mjson[0m",
           return results


 [1m}[0m[1m)[0m
    
    defdef extract generate_version_from_c_htmlandidates[1m([0mself[1m)[0m[1m([0m -> List[1m[[0mstr[1m][0m:
       html_content [32m""[0m"Generate all: str[1m)[0m -> plausible List[1m[[0mstr[1m][0m:
    version header [32m""[0m"Extract version candidates.[32m""[0m"
        candidates info = set from HTML[1m([0m[1m)[0m
        
        # script tags Add common versions directly.[32m""[0m"
    script
        candidates_pattern =.update[1m([0mself.CO r'<scriptMMON_VERS[1m[[0m^>[1m][0m*IONS[1m)[0m
        
       src=[1m[[0m"\ # Generate from patterns'[1m][0m[1m([0m[1m[[0m^"\'[1m][0m+
        for\.js major in range[1m)[0m[1m[[0m[1m([0m^>[1;36m202[0m[1m][0m*>'
    scripts[1;36m4[0m, [1;36m202[0m = re[1;36m6[0m.find[1m)[0m:
            forall[1m([0mscript_pattern minor in range[1m([0m, html_content[1m)[0m
[1;36m1[0m, [1;36m13[0m    
    versions[1m)[0m:
                candidates = [1m[[0m[1m][0m
    for.add[1m([0mf script_url in scripts:
       "[1m{[0mmajor[1m}[0m-[1m{[0mminor:[1;36m02[0m if script_url.startd[1m}[0m-swith[1m([0m'http[1;36m01[0m"[1m)[0m
                candidates'[1m)[0m:
            js.add[1m([0mf"v[1m{[0mm_content = fetch_js_bundle[1m([0major[1m}[0m-[1m{[0mminor:[1;36m02[0md[1m}[0m-script_url[1m)[0m
        else:
            #[1;36m01[0m"[1m)[0m
                candidates Handle.add[1m([0mf"[1m{[0mmajor[1m}[0m. relative[1m{[0mminor URLs:[1;36m02[0md as[1m}[0m"[1m)[0m
 needed
                           candidates.add[1m([0mf continue
        
"v[1m{[0mmajor[1m}[0m.[1m{[0mminor:        if js_content:
            versions.extend[1;36m02[0md[1m}[0m"[1m)[0m
                
[1m([0mextract_                forversions_from_js day in range[1m([0mjs_content[1m([0m[1m)[0m[1m)[0m
[1;36m1[0m,     
    return list[1;36m29[0m, [1;36m7[0m[1m)[0m:
                    candidates.add[1m([0mf"[1m{[0mmajor[1m}[0m-[1m{[0mminor:[1;36m02[0md[1m}[0m-[1m{[0m[1m([0msetday[1m([0mversions:[1;36m02[0m[1m)[0m[1m)[0m


defd js_extract_task[1m([0mtarget[1m}[0m"[1m)[0m
_url                   : str = [3;35mNone[0m, candidates.add[1m([0mf" local_dir: Pathv[1m{[0mmajor[1m}[0m. =[1m{[0mminor [3;35mNone[0m:[1m)[0m ->[1;36m02[0md[1m}[0m.[1m{[0mday: Dict[1m[[0mstr, Any[1m][0m:
    [32m""[0m"
    Main JS[1;36m02[0md[1m}[0m"[1m)[0m
        
        # extraction Add semantic versions
        for major task.
    
 in    Args range:
[1m([0m        target[1;36m1[0m,_url: URL [1;36m5[0m[1m)[0m:
            for minor in of range the[1m([0m web[1;36m0[0m, [1;36m10[0m app[1m)[0m:
                candidates.add[1m([0mf"[1m{[0m [1m([0mmajor[1m}[0m.[1m{[0mminoroptional[1m}[0m"[1m)[0m
                candidates[1m)[0m
        local_dir.add[1m([0mf"v[1m{[0mmajor[1m}[0m.: Local directory to[1m{[0mminor[1m}[0m"[1m)[0m
                scan for for patch JS in range[1m([0m[1;36m0[0m files [1m([0moptional[1m)[0m
,    
     Returns[1;36m5[0m:
[1m)[0m:
                    candidates.add        Dictionary[1m([0mf"[1m{[0mmajor[1m}[0m. with extracted[1m{[0mminor[1m}[0m.[1m{[0m versions andpatch[1m}[0m"[1m)[0m
                    candidates metadata.add[1m([0mf"
v    [32m""[0m"
   [1m{[0mmajor[1m}[0m.[1m{[0m resultsminor[1m}[0m.[1m{[0mpatch = [1m{[0m
        "[1m}[0m"[1m)[0m
        
        #task Add suffix variations": TASK,

        base       _ "versions_fversions = listound":[1m([0mc [1m[[0m[1m][0m,
andidates.copy       [1m([0m[1m)[0m[1m)[0m
        for version in base_ "versionssources": [1m{[0m[1m}[0m,
        "success:
":            for suffix in [3;91mFalse[0m
    [1m}[0m
 self.CANDIDATE_SUFFIXES:
                if    
    # Scan local JS files suffix
:
    if                    candidates.add[1m([0mf local_dir and local"[1m{[0mversion[1m}[0m[1m{[0ms_dir.exists[1m([0m[1m)[0m:
       uffix[1m}[0m"[1m)[0m
        
 local_results        return list = scan_local_js_files[1m([0mcandidates[1m)[0m
    
    def try[1m([0mlocal_dir[1m)[0m
_version        if[1m([0mself, version local_results:
           : results str[1m)[0m[1m[[0m" ->sources[32m"[0m[32m][0m[32m[[0m[32m"[0mlocal Br"[1m][0muteResult:
 =        local_results [32m""[0m"
Test a            specific version all_versions = set header.[32m""[0m"
[1m([0m[1m)[0m
            for versions        headers in local = [1m{[0m
_results.values[1m([0m[1m)[0m:
                           "x all_versions.update-de[1m([0mversions[1m)[0m
           epseek-version": version,
            "x results[1m[[0m"versions_found"[1m][0m.extend[1m([0msorted[1m([0mall_versions-api[1m)[0m[1m)[0m
    
    #-version": version Fetch,
 from            "x URL-client-version": if version provided
    if target,
        [1m}[0m
        
_url:
        html        payload_content = [1m{[0m
            " = fetch_messages":js_bundle[1m([0mtarget [1m[[0m[1m{[0m"role": "_url[1m)[0m
        ifuser", "content": " htmlHello_content:
            versions = extract_from_html[1m([0mhtml_content[1m)[0m
            if versions:
                results[1m[[0m"sources[32m"[0m[32m][0m[32m[[0m[32m"[0mremote"[1m}[0m[1m][0m,
            "stream": [3;91mFalse[0m
        [1m}[0m
        
        try:
"[1m][0m            response = versions =
 self.session.post[1m([0m
                results               [1m[[0m"versions self.base_url,
                json=payload,
                headers=headers,
                timeout=self.time_found"[1m][0m.extend[1m([0mversions[1m)[0m
out    

    #            [1m)[0m
 Deduplicate            
            response versions_text = response.text
    results[1m[[0m"[1m[[0m:[1;36m200[0mversions_found"[1m][0m = list[1m([0mset[1m][0m  # Preview[1m([0mresults[1m[[0m"
            
versions_f            #ound Success"[1m][0m[1m)[0m[1m)[0m
    results[1m[[0m"success if"[1m][0m = len not blocked by version check
            success = "update[1m([0mresults[1m[[0m"versions_f toound"[1m][0m[1m)[0m > latest  version"[1;36m0[0m
    
    return results


 notif __ in responsename_text__ == "__main__":
    # Example usage
    import sys.lower[1m([0m[1m)[0m
            
           
    
 return BruteResult    #[1m([0mversion= Scanversion, success current=success, response_preview= directoryresponse and sub_text[1m)[0m
            
       direct exceptories for Exception as e JS files
    current_dir = Path[1m([0m__file__[1m)[0m.parent
    result:
            return BruteResult =[1m([0mversion js_ext=ractversion, success=[3;91mFalse[0m, response_preview=f"_taskError[1m([0ml: [1m{[0mocal_dirstr[1m([0me[1m)[0m[1m[[0m:[1;36m100[0m[1m][0m=[1m}[0m"[1m)[0m
current_dir    
    def[1m)[0m
 brute_force[1m([0mself,    
 max    if_ resultworkers:[1m[[0m"success"[1m][0m int:
 = [1;36m10[0m        print,[1m([0mf" stop_onFound [1m{[0mlen[1m([0mresult_s[1m[[0m'uccessversions_f: boolound = [3;92mTrue[0m[1m)[0m'[1m][0m ->[1m)[0m[1m}[0m version Optional[1m([0ms[1m[[0mBruteResult[1m][0m:
        [32m""[0m"[1m)[0m:"[1m)[0m
        forExecute brute version force attack in result[1m[[0m"versions on_found"[1m][0m:
 version headers            print[1m([0mf".[32m""[0m"
         candidates - = [1m{[0mversion self.generate_version[1m}[0m"[1m)[0m
    else:
_candidates       [1m([0m[1m)[0m
        print[1m([0m"No print[1m([0mf versions extracted"[1m[[0m*[1m][0m from JS Generated [1m{[0m files"[1m)[0m
len