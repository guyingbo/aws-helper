# aws-helper
Let you manage your aws resources easier.

## Setup

~~~
$ pipenv install
$ pipenv shell
~~~

## Introduction

EC2 managment:

When you run `$ python3 helper.py ec2 show`, you can get some output like this (example values already randomized):

~~~
lifecycle                  emr-on-demand  emr-spot  on-demand  spot  reserved
region         type
ap-northeast-1 c3.large               39        35         29        21    38
               c3.xlarge               0        16          2         2     7
               c4.2xlarge             32         1         12        10    38
               c4.large               11        22         34        33    12
               c4.xlarge              28        37         23         6     7
ap-northeast-2 c4.large               28        21          7         2    15
ap-south-1     c4.large               21        17         15        10    32
               c4.xlarge               8        20         12        26    24
ap-southeast-1 c3.large               13        27         35        28    29
               c4.large               22        14          8        17    19
               c4.xlarge              18        33         25         9     5
ap-southeast-2 c3.large               34         9         37        22    35
               c4.large               31        39         21        27    28
               c4.xlarge              34        39         30        27    37
eu-central-1   c4.large                5         5         33        25    19
eu-west-1      c3.large               14        13          7        21    11
eu-west-2      c4.large               37         4         32        12     0
sa-east-1      c3.large               34        21         40        32    22
               c4.large               40        20         20        34     2
               c4.xlarge              22        10         29         8     9
us-east-1      c3.large               29        18         34        26    38
               c4.large                7         9         19        36    14
               c4.xlarge               5        11          0        32    32
us-west-1      c3.2xlarge              2         5         30        11    37
               c3.large               39        20         36         2    33
               c3.xlarge               6        13         36        13    27
us-west-2      c3.2xlarge             12        11         36         1    14
               c3.large               12         6         17        26     6
~~~
