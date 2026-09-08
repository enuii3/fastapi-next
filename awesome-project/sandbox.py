data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}

## dict
print(data)
# {
#   'isbn-9781529046137': "The Hitchhiker's Guide to the Galaxy",
#   'imdb-tt0371724': "The Hitchhiker's Guide to the Galaxy",
#   'isbn-9781439512982': "Isaac Asimov: The Complete Stories, Vol. 2"
# }

print(type(data))
# <class 'dict'>

for value in data:
    print(value)
# Output: (dicだとkey valueのセットで出力できない?)
# isbn-9781529046137
# imdb-tt0371724
# isbn-9781439512982

## dict_items
print(data.items())
# dict_items([
#   ('isbn-9781529046137', "The Hitchhiker's Guide to the Galaxy"),
#   ('imdb-tt0371724', "The Hitchhiker's Guide to the Galaxy"),
#   ('isbn-9781439512982', "Isaac Asimov: The Complete Stories, Vol. 2")
# ])

print(type(data.items()))
# <class 'dict_items'>

for key, value in data.items():
    print(key, value)
# Output:
# isbn-9781529046137 The Hitchhiker's Guide to the Galaxy
# imdb-tt0371724 The Hitchhiker's Guide to the Galaxy
# isbn-9781439512982 Isaac Asimov: The Complete Stories, Vol. 2

## list
print(list(data.items()))
# [
#   ('isbn-9781529046137', "The Hitchhiker's Guide to the Galaxy"),
#   ('imdb-tt0371724', "The Hitchhiker's Guide to the Galaxy"),
#   ('isbn-9781439512982', "Isaac Asimov: The Complete Stories, Vol. 2")
# ]

print(type(list(data.items())))
# <class 'list'>

for key, value in list(data.items()):
    print(key, value)
# Output:
# isbn-9781529046137 The Hitchhiker's Guide to the Galaxy
# imdb-tt0371724 The Hitchhiker's Guide to the Galaxy
# isbn-9781439512982 Isaac Asimov: The Complete Stories, Vol. 2