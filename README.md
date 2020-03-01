# Catmate-tracker ![Heroku](http://heroku-badge.herokuapp.com/?app=catmate-tracker&root=projects.html)
My cats take their meals really seriously. I have been obligued to create a tracker to be 100% sure they get their food.

## Stack 
To build this simple application, I used:

- [Dash](https://dash.plot.ly/): Python framework written on top of flask for fast web development and simple applications.
- [Plotly](https://plot.ly/): API with interfaces for Python and R. 
- [SQLAlchemy](https://www.sqlalchemy.org/): database and connection manager for Python. I use a simple [SQLlite](https://www.sqlite.org/index.html) database in the backend.  
- [GitHub](www.github.com): source code management
- [Heroku](http://www.heroku.com/): to deploy the app 

## Further notes 

### Hosting images with Dash
The dash application can render images saved in the ```/assets``` directory. To call you can use the command:

```Python
 html.Div(html.Img(src=app.get_asset_url("img_cat_stick_erich.jpg"), style={"width": "100%"})
```

### JS date formats

Use the native JS format to filter date times. As mentioned in [this comment](https://stackoverflow.com/a/15952652) the correct JS date/time format is:

```bash
2012-04-23T18:25:43.511Z
```

which makes the conditional highlighting of the ```dash_table.DataTable```class as follows:

```python
style_data_conditional=[{
                    "if": {'column_id': str(x),
                           # create the filter query JS + python. Really important: use the JS time format
                           'filter_query': '{next_meals} > ' + datetime.now().strftime("%Y-%m-%d") +
                                           'T' + datetime.now().strftime("%H:%M:%S")
                           },
                    "backgroundColor": colors['general'],
                    'color': 'white'} for x in sql_DF.columns
                ]
```
