import streamlit as st
import pandas as pd
import locale
import plotly.express as px

#df inicial
df_complete = pd.read_csv('data.csv')

cols_to_date = ['arrival_date', 'departure_date', 'snap_date', 'reservation_date']
date_default = "%d/%m/%Y"

for col in cols_to_date:
    df_complete[col] = pd.to_datetime(df_complete[col])#.dt.strftime(date_default)


df = df_complete[df_complete['snap_date'] == df_complete['snap_date'].max()]

#Funções de formatação
def to_money(value, currency_symbol='R$'):
    formatted_value = '{:,.2f}'.format(value)
    return f'{currency_symbol}{formatted_value}'


def plot_format(valor):
    numero_arredondado = round(valor)
    numero_formatado = "{:,.0f}".format(numero_arredondado).replace(',', '.')
    return numero_formatado

def table_format(numero):
    numero_str = '{:,.2f}'.format(numero)
    return numero_str


############### SIDEBAR

st.set_page_config(layout="wide")
st.sidebar.title("Filtros - Opens Folio")
hotel = st.sidebar.selectbox("Hotel", ["Atrio"] + sorted(df['hotel_name'].unique()))
checkout = st.sidebar.date_input("Checkout até",format="DD/MM/YYYY")
estornos = st.sidebar.checkbox("Filtrar por Positivos", value=False, key=None, help=None, on_change=None, disabled=False, label_visibility="visible")


################## APLICANDO FILTROS NO DF
df_filtered = df

if hotel != "Atrio":
    df_filtered = df[df['hotel_name'] == hotel]

df_filtered = df_filtered[df_filtered['departure_date'] < pd.to_datetime(checkout)]

if estornos:
    df_filtered = df_filtered[df['total_balance'] > 0]


################## TITULO
st.title("Contas em Aberto - " +  hotel)

################## PRIMEIRO DATAFRAME
df_to_show = df_filtered[['reservation_conf', 'hotel_id', 'total_balance', 'guest_first_name', 'guest_surname', 'arrival_date', 'departure_date', 'reservation_date']]
for col in ['arrival_date', 'departure_date', 'reservation_date']:
    df_to_show[col] = pd.to_datetime(df_to_show[col]).dt.strftime(date_default)

df_to_show['reservation_conf'] = df_to_show['reservation_conf'].apply(lambda x: str(x).replace(',', ''))
df_to_show['total_balance'] = df_to_show['total_balance'].apply(table_format)
st.dataframe(df_to_show, hide_index=True)

################## ROTULO ABAIXO
st.warning(f"Total filtrado: {to_money(df_filtered['total_balance'].sum())}")


################## CALCULA RESUMO
if hotel != "Atrio" :
    df_results = df[df['hotel_name'] == hotel]
else:
    df_results = df

total_contas_abertas = df_results['total_balance'].count()
total_valor_contas_abertas = df_results['total_balance'].sum()
total_contas_positivas = df_results[df_results['total_balance'] > 0]['total_balance'].count()
total_valor_contas_positivas = df_results[df_results['total_balance'] > 0]['total_balance'].sum()
total_contas_negativas = df_results[df_results['total_balance'] < 0]['total_balance'].count()
total_valor_contas_negativas = df_results[df_results['total_balance'] < 0]['total_balance'].sum()

################## MOSTRA RESUMO
st.title("Resumo")
with st.container(height=150):
    st.write(f"{'{:,}'.format(total_contas_abertas).replace(',','.')} contas abertas: {to_money(total_valor_contas_abertas)}")
    st.write(f"{'{:,}'.format(total_contas_positivas).replace(',','.')} contas positivas: {to_money(total_valor_contas_positivas)}")
    st.write(f"{'{:,}'.format(total_contas_negativas).replace(',','.')} contas negativas: {to_money(total_valor_contas_negativas)}")

################## MOSTRA EVOLUÇÃO

st.title("Evolução últimos 30 dias")
if hotel != 'Atrio':
    df_evolution = df_complete.groupby(["hotel_name", "snap_date"])['total_balance'].sum().reset_index().sort_values(by=['snap_date'])
    fig = px.line(df_evolution[df_evolution['hotel_name'] == hotel], x="snap_date", y="total_balance", text=df_evolution[df_evolution['hotel_name'] == hotel]['total_balance'].apply(plot_format))
    st.plotly_chart(fig)

else:
    df_evolution = df_complete.groupby("snap_date")['total_balance'].sum().reset_index().sort_values(by=['snap_date'])
    fig = px.line(df_evolution, x="snap_date", y="total_balance", text=df_evolution['total_balance'].apply(plot_format))
    st.plotly_chart(fig)

################## AGRUPA
total_por_hotel = df.groupby("hotel_name")["total_balance"].sum().reset_index().sort_values(by=['total_balance'],ascending=False)
################## GRAFICO AGRUPADO 10 MAIS
fig_date = px.bar(total_por_hotel.head(10), x="total_balance", y="hotel_name" ,title="10 maiores",text=total_por_hotel.head(10)['total_balance'].apply(plot_format))
fig_date.update_yaxes(visible=True)
st.plotly_chart(fig_date, use_container_width=True)

################## DATAFRAME AGRUPADO
st.write("Total Hoteis")
total_por_hotel['total_balance'] = total_por_hotel['total_balance'].apply(table_format)
st.dataframe(total_por_hotel, use_container_width=True, hide_index=True)

