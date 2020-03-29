# [Catmate-tracker](https://catmate-tracker.herokuapp.com/)
My cats take their meals really seriously. I have been obligued to create a tracker to be 100% sure they get their food.

## Stack 
To build this simple application, I used:

- [Dash](https://dash.plot.ly/): Python framework written on top of flask for fast web development and simple applications.
- [Plotly](https://plot.ly/): plotting API with interfaces for Python and R. 
- [SQLAlchemy](https://www.sqlalchemy.org/): orm and connection manager for Python. Originally I thought using a simple [SQLlite](https://www.sqlite.org/index.html) database in the backend. See this [link](https://devcenter.heroku.com/articles/sqlite3) to find out why that is actually a bad idea. TLDR: Heroku runs an ephemeral filesystem, i.e. no matter what files you store or read, these will be cleared periodically (every 24 hours). A better solution is to use the [Heroku Postgresql add-on](https://elements.heroku.com/addons/heroku-postgresql). Read below further setup information. 
- [GitHub](www.github.com): source code management
- [Heroku](http://www.heroku.com/): to deploy the app 

## Further notes 

### Heroku Postgres DB hosting 
Setting up a postgresql in Heroku is straightforward. You just need to activate the [Heroku Postgress](https://www.heroku.com/postgres) add-on at your application dashboard. The database instance is hosted in [AWS](https://aws.amazon.com/).

After activating the add-on, Heroku will add an extra global variable `DATABASE_URL` in `Config Vars`. These variables can be retrieved in your application as any other environmental variable:   

```Python
# Get the db URL from the Heroku config file 
db_uri = os.getenv('DATABASE_URL')

# Open a pool of connections with sqlalchemy
engine = db.create_engine(db_uri, echo=False, pool_pre_ping=True)
```

### Hosting images with Dash
The dash application can render images stored in the ```assets``` directory. To call and render them you can use the ```html.Img``` command:

```Python
# html.Img wrapped in a html.Div 
 html.Div(html.Img(src=app.get_asset_url("img_cat_stick_erich.jpg"), style={"width": "100%"})
```

### JS date format

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

### Setting Heroku's application time zone 

Since we rely on the local date to update the application, we need to set the cloud service to be configured at a specific time zone. In Heroku we can achieve this by setting a global variable `TZ` in `Config Vars`as explained in this [post](https://dev.to/paulasantamaria/change-the-timezone-on-a-heroku-app-2b4). In the Heroku CLI:

```bash
heroku config:add TZ="Europe/Berlin"
```
