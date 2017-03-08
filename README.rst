rel2tree
========
Convert relational data to tree-like structure (JSON). Aggregate, filter your
data, make custom computation.

What is this?
-------------
Let's suppose you run a business where clients can hold money and can have
approved credits in diffrent currencies. You may want to generate
a ``/balance`` api endpoint that outputs the following result:

.. code:: json
  {
    "balances": [
      {
        "clientID": 111,
        "free": [
          {
            "currencyID": "EUR",
            "amount": 125
          }
        ],
        "credit": [
          {
            "currencyID": "EUR",
            "amount": 50
          }
        ],
        "currencies": [
          "EUR"
        ]
      },
      {
        "clientID": 333,
        "free": [
          {
            "currencyID": "EUR",
            "amount": 123
          },
          {
            "currencyID": "GBP",
            "amount": 200
          }
        ],
        "credit": [],
        "currencies": [
          "EUR",
          "GBP"
        ]
      }
    ],
    "clientDetails": [
      {
        "clientID": 222,
        "clientCode": "00222"
      },
      {
        "clientID": 111,
        "clientCode": "00111"
      }
    ]
  }

Install
-------
TODO

Usage
-----
TODO
