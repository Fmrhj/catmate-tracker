# Catmate-tracker ![Heroku](http://heroku-badge.herokuapp.com/?app=catmate-tracker&root=projects.html)
My cats take their meals really seriously. I have been obligued to create a tracker to be 100% sure they get their food.


## Further notes 

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
