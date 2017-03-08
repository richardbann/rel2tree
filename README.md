# rel2tree
Convert relational data to tree-like structure like `JSON`. Aggregate, filter your
data, make custom computation.

## What is this?
Let's suppose you run a business where clients can hold money and can have
approved credits in diffrent currencies. You may want to generate
a `/balance` api endpoint that outputs the following result:

```JSON
  {
    "balances": [
      {
        "clientID": 111,
        "available": [
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
        "available": [
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
```

## Install
```
pip install rel2tree
```

## Usage
TODO
