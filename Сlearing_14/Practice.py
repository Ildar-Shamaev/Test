import pandas as pd
from IPython.display import display
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

diabetes_data = pd.read_csv('E:\VS\Сlearing_14\diabetes_data.csv')
#print(diabetes_data.info())  

dupl_columns = list(diabetes_data.columns)
mask = diabetes_data.duplicated(subset=diabetes_data)
diabetes_data_duplicates = diabetes_data[mask]
print(f'Число найденных дубликатов: {diabetes_data_duplicates.shape[0]}')
df = diabetes_data.drop_duplicates(subset=dupl_columns)
print(f'Результирующее число записей: {df.shape[0]}')

#список неинформативных признаков
low_information_cols = [] 

#цикл по всем столбцам
for col in diabetes_data.columns:
    #наибольшая относительная частота в признаке
    top_freq = diabetes_data[col].value_counts(normalize=True).max()
    #доля уникальных значений от размера признака
    nunique_ratio = diabetes_data[col].nunique() / diabetes_data[col].count()
    # сравниваем наибольшую частоту с порогом
    if top_freq > 0.95:
        low_information_cols.append(col)
        print(f'{col}: {round(top_freq*100, 2)}% одинаковых значений')
    # сравниваем долю уникальных значений с порогом
    if nunique_ratio > 0.95:
        low_information_cols.append(col)
        print(f'{col}: {round(nunique_ratio*100, 2)}% уникальных значений')
        
information_sber_data = df.drop(low_information_cols, axis=1)
print(f'Результирующее число признаков: {information_sber_data.shape[1]}')

#print(information_sber_data.info())  
#print(information_sber_data.isnull())  

def nan_function(x):
    return np.nan if x == 0 else x

information_sber_data["Glucose"] = information_sber_data["Glucose"].apply(nan_function)
information_sber_data["BloodPressure"] = information_sber_data["BloodPressure"].apply(nan_function) 
information_sber_data["SkinThickness"] = information_sber_data["SkinThickness"].apply(nan_function) 
information_sber_data["Insulin"] = information_sber_data["Insulin"].apply(nan_function)
information_sber_data["BMI"] = information_sber_data["BMI"].apply(nan_function) 
information_sber_data.isnull().mean().round(2).sort_values(ascending=False)

#Удаление признаков, где число пропусков составляет более 30 %
thresh = information_sber_data.shape[0]*0.7
diabetes = information_sber_data.dropna(thresh=thresh, axis=1)
print(diabetes.shape[1])
#print(diabetes.info())

#отбрасываем строки с числом пропусков более 2 в строке
m = diabetes.shape[1]
diabetes = diabetes.dropna(thresh=m-2, axis=0)
print(diabetes.shape[0])

#В оставшихся записях заменияем пропуски на медианы
#создаем словарь имя столбца: число(признак) на который надо заменить пропуски
values = {
    'Pregnancies': diabetes['Pregnancies'].median(),
    'Glucose': diabetes['Glucose'].median(),
    'BloodPressure': diabetes['BloodPressure'].median(),
    'SkinThickness': diabetes['SkinThickness'].median(),
    'BMI': diabetes['BMI'].median(),
    'DiabetesPedigreeFunction': diabetes['DiabetesPedigreeFunction'].median(),
    'Age': diabetes['Age'].median(),
    'Outcome': diabetes['Outcome'].median(),
}
#заполняем пропуски в соответствии с заявленным словарем
diabetes = diabetes.fillna(values)
#выводим результирующую долю пропусков
diabetes.isnull().mean()
print(diabetes['SkinThickness'].mean().round(1))



#Выбросы найдёт классический метод межквартильного размаха в признаке SkinThickness
def outliers_iqr_mod(data, feature, left=1.5, right=1.5, log_scale=False):
    if log_scale:
        x = np.log(data[feature])
    else:
        x= data[feature]
    quartile_1, quartile_3 = x.quantile(0.25), x.quantile(0.75),
    iqr = quartile_3 - quartile_1
    lower_bound = quartile_1 - (iqr * left)
    upper_bound = quartile_3 + (iqr * right)
    outliers = data[(x < lower_bound) | (x > upper_bound)]
    cleaned = data[(x >= lower_bound) & (x <= upper_bound)]
    return outliers, cleaned
outliers, _ = outliers_iqr_mod(diabetes, 'SkinThickness')
print(f'Число выбросов по методу Тьюки: {outliers.shape[0]}')

#Выбросы найдёт классический метод z-отклонения в признаке SkinThickness
def outliers_z_score_mod(data, feature, log_scale=False, left=3, right=3):
    if log_scale:
        x = np.log(data[feature]+1)
    else:
        x = data[feature]
    mu = x.mean()
    sigma = x.std()
    lower_bound = mu - left * sigma
    upper_bound = mu + right * sigma
    outliers = data[(x < lower_bound) | (x > upper_bound)]
    cleaned = data[(x >= lower_bound) & (x <= upper_bound)]
    return outliers, cleaned
outliers, _ = outliers_z_score_mod(diabetes, 'SkinThickness')
print(f'Число выбросов по методу Тьюки: {outliers.shape[0]}')


#Выбросы найдёт классический метод межквартильного размаха в признаке DiabetesPedigreeFunction 
def outliers_iqr_mod(data, feature, left=1.5, right=1.5, log_scale=False):
    if log_scale:
        x = np.log(data[feature])
    else:
        x= data[feature]
    quartile_1, quartile_3 = x.quantile(0.25), x.quantile(0.75),
    iqr = quartile_3 - quartile_1
    lower_bound = quartile_1 - (iqr * left)
    upper_bound = quartile_3 + (iqr * right)
    outliers = data[(x < lower_bound) | (x > upper_bound)]
    cleaned = data[(x >= lower_bound) & (x <= upper_bound)]
    return outliers, cleaned
outliers, _ = outliers_iqr_mod(diabetes, 'DiabetesPedigreeFunction')
outliers_log, _ = outliers_iqr_mod(diabetes, 'DiabetesPedigreeFunction', log_scale=True)
print(outliers.shape[0] - outliers_log.shape[0])