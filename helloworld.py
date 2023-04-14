import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import plotly.figure_factory as ff
import scipy


with st.echo(code_location='below'):
    election = open('voting_data_eng.csv')
    election_csv = pd.read_csv(election)
    el2 = election_csv.assign(Turnout=lambda x: x.Number_of_valid_ballot_papers / x.Number_of_voters_enlisted * 100)
    el3 = el2.assign(Percentage_for_Putin=
                     lambda x: x.Putin_Vladimir_Vladimirovich / x.Number_of_valid_ballot_papers * 100)
    rg = el3['region_name']
    regions = rg.drop_duplicates()
    regions.iloc[0] = 'All regions'
    st.title('Визуализация аномалий на президентских выборах в России 2018')
    st.write('Данный генератор гистограмм и диаграмм рассеивания позволяет увидеть статистические аномалии на '
             'президентских выборах 2018. Существуют '
             '[исследования](https://link.springer.com/article/10.1140/epjb/e2010-00151-1) о том, '
             'что результаты выборов, в частности явка и процент голосов, распределяются в примерном соответствии с '
             'гауссовым распределением. Другой показатель аномалий - увеличение процента голосов за победителя с '
             'увеличением явки, что с большой вероятностью свидетельствует о вбросах. Единого мнения по поводу '
             'существования значительных фальсификаций на этих выборах не сложилось, подробности и разные мнения можно '
             'почитать, например, [здесь](https://meduza.io/feature/2018/07/03/tak-skolko-golosov-ukrali-na-prezidentskih-vyborah-sotni-tysyach-ili-milliony).')
    region = st.selectbox('Выберите регион', regions)
    el3 = el3.dropna()
    st.write(el3)
    plottype = st.radio('Выберите тип диаграммы', ['Распределение явки', 'Распределение явки с аппроксимированным распределением', 'Распределение голосов за В.В.Путина', 'Распределение голосов за В.В.Путина с аппроксимированным распределением',
                                          'Scatter-plot со значениями явки и процента голосов за В.В.Путина',
                                                   'Таблица с результатами'])
    color = st.color_picker(label='Выберите цвет', value='#8B0000')
    if region == 'All regions':
        regresult = el3
    else:
        regresult = el3[el3['region_name'] == region]
    if plottype == 'Распределение явки':
        bandwidth = st.slider(label='Выберите ширину столбца для вычисления плотности', min_value=0.1, max_value=5.0)
        d = alt.Chart(regresult).transform_density('Turnout', as_=['Turnout', 'density'],
                                                   bandwidth=bandwidth).mark_area(color=color).encode(
            x=alt.X("Turnout:Q", axis=alt.Axis(title='Процент явки')),
            y=alt.Y('density:Q', axis=alt.Axis(title='Плотность распределения')))
        st.altair_chart(d, use_container_width=True)
    if plottype == 'Распределение явки с аппроксимированным распределением':
        bandwidth = st.slider(label='Выберите ширину столбца для вычисления плотности', min_value=0.1, max_value=5.0)
        fig1 = ff.create_distplot([regresult['Turnout']],
                          ['Turnout'], colors=['#63F5EF'], bin_size=bandwidth)
        fig1.update_layout(title={
            'text': "Явка",
            'y': 0.9,
            'x': 0.4,
            'xanchor': 'center',
            'yanchor': 'top'})

        st.write(fig1)        
    if plottype == 'Распределение голосов за В.В.Путина':
        bandwidth = st.slider(label='Выберите ширину столбца для вычисления плотности', min_value=0.1, max_value=5.0)
        d = alt.Chart(regresult).transform_density('Percentage_for_Putin', as_=['Percentage_for_Putin', 'density'],
                                                   bandwidth=bandwidth).mark_area(color=color).encode(
            x=alt.X("Percentage_for_Putin:Q", axis=alt.Axis(title='Процент голосов за Путина')),
            y=alt.Y('density:Q', axis=alt.Axis(title='Плотность распределения')))
        st.altair_chart(d, use_container_width=True)
    if plottype == 'Распределение голосов за В.В.Путина с аппроксимированным распределением':
        bandwidth = st.slider(label='Выберите ширину столбца для вычисления плотности', min_value=0.1, max_value=5.0)        
        
        fig1 = ff.create_distplot([el3['Percentage_for_Putin']],
                          ['Percentage of votes'], colors=['#A6ACEC'], bin_size=bandwidth)
        fig1.update_layout(title={
            'text': "Процент голосов за Путина",
            'y': 0.9,
            'x': 0.4,
            'xanchor': 'center',
            'yanchor': 'top'})

        st.write(fig1)
    if plottype == 'Scatter-plot со значениями явки и процента голосов за В.В.Путина':
        c = alt.Chart(regresult).mark_circle(size=1, color=color).encode(
            x=alt.X('Turnout', axis=alt.Axis(title='Явка (%)')), y=alt.Y('Percentage_for_Putin',
                                                                         axis=alt.Axis(
                                                                             title='Путин (%)'))).configure_mark(
            opacity=0.2)
        st.altair_chart(c, use_container_width=True)
    if plottype == 'Таблица с результатами':
        regresult.rename(columns={'ps_id': 'Номер УИК', 'Turnout': 'Явка (%)', 'Percentage_for_Putin':
            'Процент голосов за Путина'},
                         inplace=True)
        st.write(regresult[['Номер УИК', 'Явка (%)', 'Процент голосов за Путина']])
