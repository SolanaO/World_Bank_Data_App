import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import plotly.colors
from collections import OrderedDict
import requests

#default list of all countries of interest
country_default = OrderedDict([('Canada', 'CAN'), ('United States', 'USA'),
  ('Mexico', 'MEX'), ('Brazil', 'BRA'),
  ('France', 'FRA'), ('Italy', 'ITA'), ('Germany', 'DEU'),
  ('United Kingdom', 'GBR')])

# World Bank indicators of interest for pulling data
indicators = ['AG.LND.AGRI.ZS', 'AG.LND.FRST.ZS',
  'ER.PTD.TOTL.ZS', 'EN.ATM.CO2E.PC', 'EG.USE.ELEC.KH.PC',
  'EG.FEC.RNEW.ZS', 'SP.URB.TOTL.IN.ZS']

def return_figures(countries=country_default):
    """
    Creates a list of six dataframes using the World Bank API.
    Example of the World Bank API endpoint:
    - agricultural land for the United States and Brazil from 1991 to 2018
    http://api.worldbank.org/v2/countries/usa;bra/indicators/AG.LND.AGRI.ZS?date=1991:2018&per_page=1000&format=json
    Args:
        country_default (dict): list of countries for filtering the data
    Returns:
        list (dataframes): list containing the six dataframes
    """

    # when the countries variable is empty, use the country_default dictionary
    if not bool(countries):
        countries = country_default

   # prepare filter data for World Bank API
   # the API uses ISO-3 country codes separated by ;
    country_filter = list(countries.values())
    country_filter = [x.lower() for x in country_filter]
    country_filter = ';'.join(country_filter)

   # stores the data frames with the indicator data of interest
    data_frames = []
   # url endpoints for the World Bank API
    urls = []

  # pull data from World Bank API and clean the resulting json
  # results stored in data_frames variable
    for indicator in indicators:
        url = 'http://api.worldbank.org/v2/countries/' + country_filter +\
        '/indicators/' + indicator + '?date=1991:2018&per_page=1000&format=json'
        urls.append(url)
        try:
            r = requests.get(url)
            data = r.json()[1]
        except:
            print('Could not load data. ', indicator)

        for i, value in enumerate(data):
            value['indicator'] = value['indicator']['value']
            value['country'] = value['country']['value']
        data_frames.append(data)


    # plot agricultural land (% of land area) from 1991 to 2018
    graph_one = []
    df_one = pd.DataFrame(data_frames[0])

    # filter and sort values for the visualization
    # filtering plots the countries in decreasing order by their values
    df_one.sort_values('value', ascending=False, inplace=True)
    df_one.sort_values('date', ascending=True, inplace=True)

    # this  country list is re-used by all the charts to ensure legends have
    # the same order and color
    countrylist = df_one.country.unique().tolist()

    for country in countrylist:
        x_val = df_one[df_one['country'] == country].date.tolist()
        y_val =  df_one[df_one['country'] == country].value.tolist()
        graph_one.append(
            go.Scatter(
                x = x_val,
                y = y_val,
                mode='lines',
                name=country
           )
        )

    layout_one = dict(title = 'Agricultural Land (% of land area)',
                  xaxis = dict(title = 'Year',
                            autotick=False, tick0=1991, dtick=9),
                  yaxis = dict(title = 'Percent of land area'),
                 )


    # plot forest area (% of land area) from 1990 to 2021 in the 12 economies
    graph_two = []
    df_two = pd.DataFrame(data_frames[1])

    df_two.sort_values('value', ascending=False, inplace=True)
    df_two.sort_values('date', ascending=True, inplace=True)

    for country in countrylist:
        x_val = df_two[df_two['country'] == country].date.tolist()
        y_val =  df_two[df_two['country'] == country].value.tolist()
        graph_two.append(
            go.Scatter(
                x = x_val,
                y = y_val,
                mode='markers',
                name=country
            )
        )

    layout_two = dict(title = 'Forest Area (% of land area)',
                  xaxis = dict(title = 'Year',
                               autotick=False, tick0=1991, dtick=9),
                  yaxis = dict(title = 'Percent of land area'),
                  hovermode="x unified"
                 )
    #fig.update_layout(hovermode="x unified")


    # third chart plots terrestrial and marine protected areas in 2018
    graph_three = []
    df_three = pd.DataFrame(data_frames[2])

    df_three.sort_values('value', ascending=False, inplace=True)
    df_three = df_three[df_three['date'] == '2018']

    graph_three.append(
                go.Bar(
                x = df_three.country.tolist(),
                y = df_three.value.tolist(),
            )
        )

    layout_three = dict(title = 'Terrestrial and Marine Protected Areas in 2018',
                    xaxis = dict(title = 'Country'),
                    yaxis = dict(title = 'Percent of total territorial area'),
                    hovertemplate='<extra></extra>',
                    showlegend=False
                   )


    # fourth chart shows CO2 emissions per capita in 1991 and 2018
    graph_four = []
    years_list = ['1991', '2000', '2009', '2018']
    df_four= pd.DataFrame(data_frames[3])
    df_four = df_four[df_four['date'].isin(years_list)]

    for country in countrylist:
        x_val = df_four[df_four['country'] == country].date.tolist()
        y_val =  df_four[df_four['country'] == country].value.tolist()
        graph_four.append(
            go.Scatter(
                x = x_val,
                y = y_val,
                mode='markers',
                name=country,
                marker=dict(size=[12, 12, 12, 12])
            )
        )


    layout_four = dict(title = 'CO2 Emissions per Capita', xaxis = dict(title = 'Year', autotick=False, tick0=1991, dtick=9),
              yaxis = dict(title = 'Metric tons per capita'),
             )

    # fifth chart plots electric power consumption vs  urban population
    graph_five = []
    df_five_a = pd.DataFrame(data_frames[6])
    df_five_a = df_five_a[['country', 'date', 'value']]

    df_five_b = pd.DataFrame(data_frames[4])
    df_five_b = df_five_b[['country', 'date', 'value']]

    df_five = df_five_a.merge(df_five_b, on=['country', 'date'])
    df_five = df_five[df_five['date'].isin(years_list)]
    df_five.sort_values('date', ascending=True, inplace=True)

    plotly_default_colors = plotly.colors.DEFAULT_PLOTLY_COLORS

    for i, country in enumerate(countrylist):

        current_color = []

        x_val = df_five[df_five['country'] == country].value_x.tolist()
        y_val = df_five[df_five['country'] == country].value_y.tolist()
        years = df_five[df_five['country'] == country].date.tolist()
        country_label = df_five[df_five['country'] == country].country.tolist()

        text = []
        for country, year in zip(country_label, years):
            text.append(str(country) + ' ' + str(year))

        graph_five.append(
            go.Scatter(
            x = x_val,
            y = y_val,
            mode = 'lines+markers',
            text = text,
            name = country,
            textposition = 'top center'
          )
      )

    layout_five = dict(title = 'Electric Power Consumption vs Percent of Urban Population',
                xaxis = dict(title = 'Urban population (% of total population)', range=[60,90], dtick=5),
                yaxis = dict(title = 'Electric power consumption (kWh per capita)'),
                )

    # sixth chart plots CO2 emissions vs renewable energy consumption
    graph_six = []
    df_six_a = pd.DataFrame(data_frames[3])
    df_six_a = df_six_a[['country', 'date', 'value']]

    df_six_b = pd.DataFrame(data_frames[5])
    df_six_b = df_six_b[['country', 'date', 'value']]

    df_six = df_six_a.merge(df_six_b, on=['country', 'date'])
    df_six = df_six[df_six['date'].isin(years_list)]
    df_six.sort_values('date', ascending=True, inplace=True)

    plotly_default_colors = plotly.colors.DEFAULT_PLOTLY_COLORS

    for i, country in enumerate(countrylist):

        current_color = []

        x_val = df_six[df_six['country'] == country].value_x.tolist()
        y_val = df_six[df_six['country'] == country].value_y.tolist()
        years = df_six[df_six['country'] == country].date.tolist()
        country_label = df_six[df_six['country'] == country].country.tolist()

        text = []
        for country, year in zip(country_label, years):
            text.append(str(country) + ' ' + str(year))

        graph_six.append(
            go.Scatter(
            x = x_val,
            y = y_val,
            mode = 'markers',
            text = text,
            name = country,
            textposition = 'top center',
            marker=dict(size=8)
          )
      )

    layout_six = dict(title = 'Renewable Energy Consumption vs CO2 Emissions in 2000',
                xaxis = dict(title = 'CO2 emissions (metric tons per capita)'),
                yaxis = dict(title = 'Renewable energy (% of total energy consumption)'),
                )


    # append all charts
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_four, layout=layout_four))
    figures.append(dict(data=graph_five, layout=layout_five))
    figures.append(dict(data=graph_six, layout=layout_six))
    return figures
