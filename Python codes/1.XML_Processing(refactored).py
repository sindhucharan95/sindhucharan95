
# Import relevant packages

from distutils.filelist import findall
import xml.etree.ElementTree as ET
import pandas as pd
import os
import datetime as dt


#Input path for the file
xml_file = "/Users/filepath/input.xml"
filename_lst = os.path.split(xml_file)
filename_str = filename_lst[len(filename_lst) - 1]
file_str = open(xml_file, 'r')
ind_start,ind_end,xml_list,xml_entry = [], [], [],[]

#Identify xml head's version and encoding
xml_head = '<?xml version="1.0" encoding="UTF-8"?>\n'

#Create a iterator in order to identify the child elements of the input xml file
def xml_input():
    global xml_entry
    for count, line in enumerate(file_str.readlines()):
        my_line = line.strip()
        if my_line == '</Ntry>':
            ind_end.append(count + 1)
        elif my_line == '<Ntry>':
            ind_start.append(count)
        xml_list.append(my_line)
    for entry in range(len(ind_start)):
        ntry = xml_head + '\n'.join(xml_list[ind_start[entry]:ind_end[entry]])
        xml_entry.append(ntry)
xml_input()

# Input mapping to identify the relevant columns(Tags) in XML  file
refe = 'NtryRef'
dc = 'CdtDbtInd'
nmc = 'NtryDtls/TxDtls/RltdPties/Cdtr/Nm'
nmd = 'NtryDtls/TxDtls/RltdPties/Dbtr/Nm'
amntdetails = 'NtryDtls/TxDtls/AmtDtls/TxAmt/Amt'
amntdoc = './/RfrdDocAmt/RmtdAmt'



#Assign the input  data frame 
entry_df = pd.DataFrame()

# function to search for XML child elements using the mapping provided above for  the input xml file
def xml_conv():
    global entry_df
    for item in xml_entry:
        my_root = ET.fromstring(item)
        a, b, c, d, e, f, g = [], [], [], [], [], [], []
        # Doc Reference
        a.extend(i.text for i in my_root.findall(refe))
        # DebitCredit Indicator
        b.extend(i.text for i in my_root.findall(dc))
        # Name on credit
        c.extend(i.text for i in my_root.findall(nmc))
        # Name on debit
        d.extend(i.text for i in my_root.findall(nmd))
        # Amount details
        e.extend(i.text for i in my_root.findall(amntdetails))
        # Amount documents
        f.extend(i.text for i in my_root.findall(amntdoc))
        max_len = max(len(b), len(c), len(d), len(e), len(f), len(g))
        a = [a[0]] * max_len
        b = [b[0]] * max_len
        g = [filename_str] * max_len
        data = {'ref': a, 'dcind': b, 'nmc': c, 'nmd': d, 'amtdet': e, 'amtdoc': f, 'fnm': g}
        df = pd.DataFrame.from_dict(data, orient='index').transpose()
        entry_df = pd.concat([entry_df, df])
xml_conv()

#Appends the time and date info to the exported file
def date_nm():
    return dt.datetime.now().strftime('%Y') + dt.datetime.now().strftime('%m') + dt.datetime.now().strftime('%d') + dt.datetime.now().strftime('%H') + dt.datetime.now().strftime('%M') + dt.datetime.now().strftime('%S')
date_nm = date_nm()

#Data export path
save_path = "/output path"

#Exporting the processed XML file into pipe delimited file
entry_df.to_csv(f'{save_path}/XML_Export' + date_nm + '.txt', sep="|", index=False)