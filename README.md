![header](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=300&section=header&text=%20PAD&fontSize=90&animation=fadeIn&fontAlignY=38&desc=Corolețchi%20Ana%20FAF%20203)

## Instructions

1. Clone the project
2. Pull images from `https://hub.docker.com/u/gumball7`
3. Use gateway URL for making requests : `http:localhost:4000`
 
Endpoints :

1. Create order `POST`
- /orders
```json
{
    "customer_id": 123,
    "restaurant_id": 456,
    "items": [
        {
            "item_id": 789,
            "quantity": 2
        },
        {
            "item_id": 101,
            "quantity": 1
        }
    ]
}
```

2. Get order `GET`
- /orders/{order_id}
3. Get order items `GET`
- /orders/{order_id}/items
4. Get all restaurants `GET`
- /restaurants
5. Get a restaurant `GET`
- /restaurants/{restaurant_id}

 
## Description

:trollface:  This repository contains laboratory works for **PAD**.

:exclamation:  Teacher [Voloșenco Maxim](https://github.com/maximvolosenco).

## Labs

[:white_check_mark: Checkpoint 1](https://github.com/Gumball007/PAD_LAB1/tree/main/checkpoint1)

## Contact

:mailbox:  My email: `ana.coroletchi@isa.utm.md`
