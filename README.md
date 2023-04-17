# Viewquery: A script for a glimpse of an overview by Entrez query

## 1. Introduct

This script helps find the newest paper on [Pubmed][1] by query and count the cited of each article. The result is a html table. This is its [web app version](https://truongphi20-viewquery-main-streamlit-bj23dz.streamlit.app/)

## 2. Usage

For installing:
```
git clone https://github.com/Truongphi20/viewquery
```

For testing:
```
 python .\viewquery.py -h
```
```
usage: viewquery.py [-h] [-q QUERY] [-v] [-g GET]

optional arguments:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        query for Pubmed search
  -v, --version         show version
  -g GET, --get GET     Number of newest papers get.
```

## 3. Example

Suppose, we need to find the following query on Pubmed:

`(microorganism[Title/Abstract]) AND (Genetic Engineering[Title/Abstract])`

And we do the following command:

```
python .\viewquery.py -q "(microorganism[Title/Abstract]) AND (Genetic Engineering[Title/Abstract])" -g 100
```
**Note: `-g` tag stand for number of newest paper we want to get, default value is 100. The larger this value, the lower our progress.**

An example of the output can be seen in `example_table.html`.

$$Score = \frac{Cited}{Year_{now} - Year}$$

![Example_output][2]

[1]: https://pubmed.ncbi.nlm.nih.gov/advanced/
[2]: https://user-images.githubusercontent.com/96680644/225033123-17065333-cf80-4a9f-8ef1-7808d6a0a4cd.png

