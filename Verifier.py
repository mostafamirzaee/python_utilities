import pandas as pd
import openpyxl as pyxl
import numpy as np
import glob

def readFiles():
    path = r'E:\data\marketing_exports_4\raw files'
    print('Reading input files in the path ' + path + ' ...')
    all_files = glob.glob(path + "/*.csv")

    print('Found these files in the path ', all_files)

    dfListRawFiles = []

    for filename in all_files:
        print('Reading ', filename , ' ...')
        df = pd.read_csv(filename, low_memory=False, skiprows=1, thousands=r',',index_col=None, header=0)
        dfListRawFiles.append(df)

    print('All Read, now Concatenating them...')
    df_big = pd.concat(dfListRawFiles, axis=0, ignore_index=True)
    print('Concatenated successfully...')

    return df_big

# verification functions ##################################################################

def check_count(df:pd.DataFrame):
    df_group_by = df.pivot_table(values='SITE', index='Time', aggfunc=pd.Series.nunique)
    df_count_check = df_group_by[df_group_by['SITE'] <= 12600]

    return df_count_check

def check_thrput(df:pd.DataFrame, kpi_dict):
    throughput_kpi = kpi_dict['thrput']
    payload_kpi = kpi_dict['payload']
    avail_kpi = kpi_dict['avail']

    df_check_thrput = df[((df[throughput_kpi].isna())
                             | (df[throughput_kpi] <= 0))
                            &
                            ((df[payload_kpi] > 0)
                             | (pd.to_numeric(df[avail_kpi], errors='coerce') > 0))
                            ]
    df_check_thrput = df_check_thrput.reset_index(drop=True)

    return df_check_thrput

def check_payload(df:pd.DataFrame, kpi_dict):
    throughput_kpi = kpi_dict['thrput']
    payload_kpi = kpi_dict['payload']
    avail_kpi = kpi_dict['avail']

    df_check_payload = df[((df[payload_kpi].isna())
                              | (df[payload_kpi] <= 0))
                             &
                             ((df[throughput_kpi] > 0)
                             | (pd.to_numeric(df[avail_kpi], errors='coerce') > 0))
                             ]
    df_check_payload = df_check_payload.reset_index(drop=True)
    return df_check_payload

def check_avail(df:pd.DataFrame, kpi_dict):
    throughput_kpi = kpi_dict['thrput']
    payload_kpi = kpi_dict['payload']
    avail_kpi = kpi_dict['avail']

    df_check_avail = df[((df[avail_kpi].isna())
                              | (pd.to_numeric(df[avail_kpi], errors='coerce') <= 0))
                             &
                             ((df[throughput_kpi] > 0)
                             | (df[payload_kpi] > 0))
                             ]

    df_check_avail = df_check_avail.reset_index(drop=True)
    return df_check_avail

def check_all_KPIs(df:pd.DataFrame, kpi_dict):
    throughput_kpi = kpi_dict['thrput']
    payload_kpi = kpi_dict['payload']
    avail_kpi = kpi_dict['avail']

    df_check_all_KPIs = df[((df[avail_kpi].isna())
                              | (pd.to_numeric(df[avail_kpi], errors='coerce') <= 0))
                             &
                              ((df[throughput_kpi].isna())
                               | (df[throughput_kpi] <= 0))
                             &
                              ((df[payload_kpi].isna())
                              | (df[payload_kpi] <= 0))
                             ]

    df_check_all_KPIs = df_check_all_KPIs.reset_index(drop=True)
    return df_check_all_KPIs


#2G first
kpi_dict = { '2g_kpis': {
                        'thrput': '2G_EGPRS_LLC_THROUGHPUT_IR(Kbps)'
                        ,'payload' : '2G_PAYLOAD_LLC_TOTAL_MBYTE_IR(MB)'
                        ,'avail': '2G_TCH_AVAILABILITY_IR(%)'
                },
             '3g_kpis': {
                        'thrput': '3G_Throughput_HS_SC_NodeB_kbps_IR(Kbps)'
                        ,'payload': '3G_PAYLOAD_TOTAL_3G_MBYTE_IR(Mb)'
                        ,'avail': '3G Cell_Avail_Sys_IR(%)'
                },
             '4g_kpis': {
                        'thrput': '4G_Throughput_UE_DL_kbps_IR(Kbps)'
                        ,'payload': '4G_PAYLOAD_TOTAL_MBYTE_IR(MB)'
                        ,'avail': '4G_CELL_AVAIL_SYS_IR'
                }
        }



#start here




writer = pd.ExcelWriter(r'E:\data\marketing_exports_4\verification_report.xlsx')

df = readFiles()

print('Now verifying data...')

total_rows = len(df.index)

arr_result_summary_data= []

print('Total rows: ', total_rows)
arr_result_summary_data.append(['Total Rows',total_rows])

df_result_summary = pd.DataFrame()
df_result_summary.to_excel(writer, sheet_name='Test Result Summary')

# 1) site count issues
df_count_check = check_count(df)
rowsWithCountIssue = len(df_count_check.index)
print('Rows with count issue: ', rowsWithCountIssue)
df_count_check.to_excel(writer, sheet_name='Count check - less than 12600')
arr_result_summary_data.append(['Rows with count issue',rowsWithCountIssue])


# 2) per KPI and per technology
for i in range(2,5):
    print('Verifying ' +  str(i) + 'G KPIs...' )
    tech_label = str(i) + 'g_kpis'
    tech_kpi_dict = kpi_dict[tech_label]

    df_check_thrput = check_thrput(df, tech_kpi_dict)
    df_check_payload = check_payload(df, tech_kpi_dict)
    df_check_avail = check_avail(df, tech_kpi_dict)
    df_check_all_KPIs = check_all_KPIs(df, tech_kpi_dict)

    rowsWithThroughputIssue = len(df_check_thrput.index)
    rowsWithPayloadIssue = len(df_check_payload.index)
    rowsWithAvailIssue = len(df_check_avail.index)
    rowsWithAllKPIsIssue = len(df_check_all_KPIs.index)

    testThrput = 'Rows with ' + str(i) + 'g throughput issue: '
    testPayload = 'Rows with ' + str(i) + 'g payload issue: '
    testAvail = 'Rows with ' + str(i) + 'g availability issue: '
    testAllKpis = 'Rows with all ' + str(i) + 'g KPIs issue: '

    print(testThrput , rowsWithThroughputIssue)
    print(testPayload, rowsWithPayloadIssue)
    print(testAvail, rowsWithAvailIssue)
    print(testAllKpis, rowsWithAllKPIsIssue)

    arr_result_summary_data.append([testThrput, rowsWithThroughputIssue])
    arr_result_summary_data.append([testPayload, rowsWithPayloadIssue])
    arr_result_summary_data.append([testAvail, rowsWithAvailIssue])
    arr_result_summary_data.append([testAllKpis, rowsWithAllKPIsIssue])

    print('Exporting into excel report for ' + tech_label + '...')
    df_check_thrput.to_excel(writer, sheet_name='Throughput ' + str(i) + 'g issues')
    df_check_payload.to_excel(writer, sheet_name='Payload ' + str(i) + 'g issues')
    df_check_avail.to_excel(writer, sheet_name='Availability ' + str(i) + 'g issues')
    df_check_all_KPIs.to_excel(writer, sheet_name='All ' + str(i) + 'g KPIs issues')

df_result_summary = pd.DataFrame(data=arr_result_summary_data, columns=['Test', 'Result'])
df_result_summary.to_excel(writer, sheet_name='Test Result Summary')

writer.save()

print('All Completed.')

