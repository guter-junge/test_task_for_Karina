import pandas as pd

def combine_csv(data_paths, reports_paths):
    data_df = pd.concat([pd.read_csv(data_file, header=0) for data_file in data_paths], ignore_index=True)
    data_df.to_csv('combined_data.csv', index=False)
    data_df = pd.read_csv('combined_data.csv')

    reports_df = pd.concat([pd.read_csv(report_file, header=[0, 1]) for report_file in reports_paths], ignore_index=True)
    reports_df.to_csv('combined_reports.csv', index=False)
    reports_df = pd.read_csv('combined_reports.csv')

    with pd.ExcelWriter('combined.xlsx', engine='openpyxl') as writer:
        data_df.to_excel(writer, sheet_name='Data', index=False)
        reports_df.to_excel(writer, sheet_name='Report', index=False)

    combined_read = pd.read_excel('combined.xlsx')
    return combined_read

def fraud_by_source():
    combined_data = pd.read_excel('combined.xlsx', sheet_name='Data', header=0)
    combined_reports = pd.read_excel('combined.xlsx', sheet_name='Report', header=[0, 1])

    media_source_count = combined_data['Media Source'].value_counts().reset_index()
    media_source_count.columns = ['Media Source', 'Total installs']

    total_fraudulent_attribution = combined_reports.iloc[:, 2].str.replace(r'\D', '', regex=True).astype(int)
    reports_media_source = combined_reports.iloc[:, 0]
    reports_df = pd.DataFrame({'Media Source': reports_media_source, 'Total fraudulent attribution': total_fraudulent_attribution})
    reports_df = reports_df.groupby('Media Source', as_index=False).sum()

    fraud_by_source = pd.merge(media_source_count, reports_df, how='left', left_on='Media Source', right_on='Media Source')
    fraud_by_source['Fraud percentage'] = (fraud_by_source['Total fraudulent attribution'] / fraud_by_source['Total installs']) * 100
    return fraud_by_source

def fraud_percentage(fraud_by_source):
    fraud_percentage_by_source = fraud_by_source[['Media Source', 'Fraud percentage']]
    return f'Процентное содержание фрода по источникам\n{fraud_percentage_by_source}\n'

def top_5_fraud_sources(fraud_by_source):
    sorted_by_fraud_attribution = fraud_by_source.sort_values(by='Total fraudulent attribution', ascending=False).head(10)
    top_5 = sorted_by_fraud_attribution.nlargest(5, 'Fraud percentage')[['Media Source', 'Total fraudulent attribution', 'Fraud percentage']]
    bottom_5 = sorted_by_fraud_attribution.nsmallest(5, 'Fraud percentage')[['Media Source', 'Total fraudulent attribution', 'Fraud percentage']]

    return f'Топ-5 источников по количеству фрода с самым высоким процентом фрода \n{top_5}\n' \
          f'\nТоп-5 источников по количеству фрода с самым низким процентом фрода \n{bottom_5}\n'

def profits_top_5_fraud_sources(fraud_by_source):
    sorted_by_fraud_attribution = fraud_by_source.sort_values(by='Total fraudulent attribution', ascending=False)[['Media Source', 'Total fraudulent attribution']]

    total_fraud = (sorted_by_fraud_attribution['Total fraudulent attribution'].sum())

    top_5_sorted_by_fraud_attribution = sorted_by_fraud_attribution.head(5)
    top_5_total_fraud = top_5_sorted_by_fraud_attribution['Total fraudulent attribution'].sum()
    top_5_fraud_losses = top_5_total_fraud * 0.2

    top_5_fraud_percentage = round((top_5_total_fraud / total_fraud) * 100, 2)
    return f'Топ-5 источников с самым высоким содержанием фрода \n{top_5_sorted_by_fraud_attribution}' \
           f'\nЭтот фрод составляет {top_5_fraud_percentage}% от всего фрода\n' \
           f'Он обошелся в {top_5_fraud_losses}$\n'

def overall_profit(fraud_by_source):
    fraud_by_source['Actual installs'] = (fraud_by_source['Total installs'] - fraud_by_source['Total fraudulent attribution'])
    profit = fraud_by_source['Actual installs'].sum() * 0.5
    losses = fraud_by_source['Total fraudulent attribution'].sum() * 0.2
    overall_profit = profit - losses
    return f'Прибыль с установок составила {profit}$\n' \
           f'Вычет за фрод составил {losses}$\n' \
           f'Итоговая прибыль - {overall_profit}$\n'

if __name__ == '__main__':
    data_paths = ['id1072084799_installs_2024-01-15_2024-01-31_Asia_Nicosia.csv', 'id1072084799_installs_2024-02-01_2024-02-05_Asia_Nicosia.csv']
    reports_paths = ['protect360_report.csv', 'protect360_report-3.csv']
    combine = combine_csv(data_paths, reports_paths)
    fraud_by_source = fraud_by_source()
    print(fraud_percentage(fraud_by_source))
    print(top_5_fraud_sources(fraud_by_source))
    print(overall_profit(fraud_by_source))
    print(profits_top_5_fraud_sources(fraud_by_source))
