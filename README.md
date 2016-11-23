# Adopt.me()

### Installing
`pip install -r requirements.txt`

### Running
`python adopt.py`

### Troubleshooting

Drop the database by doing the following:
```
$ python
>>> import adopt
>>> adopt.db.reflect()
>>> adopt.db.drop_all()
```