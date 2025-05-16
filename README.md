# scrappy-tr-api
Code for Scrappy the Rooster fan project for the unreleased game ARC Raiders.



## data
Originally sourced from Tech Test 2 doc shared by reddit user
https://docs.google.com/document/d/1LPpXIYuTH54o3bWDx3Q7ClRDGLGNpIuNvisK-HwOwjk/edit?usp=sharing

Google doc then uploaded to ChatGPT, prompted into a DynamoDB / JSON format, and uploaded to DyanmoDB

## services

![diagram](/docs/Scrappy%20the%20Rooster.drawio.png)


## sample usage
Using an HTTP client (or just visit directly in browser)

`GET` `https://api.scrappytherooster.com/loot/Damaged%20Rocketeer%20Part`
```json
{
  "craftable": false,
  "description": "",
  "sell_value": 0,
  "recycles_into": [
    {
      "amount": 7,
      "loot_name": "ARC Alloys"
    }
  ],
  "loot_name": "Damaged Rocketeer Part",
  "rarity": "Grey"
}
```

`GET` `https://api.scrappytherooster.com/loot/Wires`
```json
{
    "used_for_crafting": [
        "Electrical Components",
        "Utility Bench Level\u00a0II",
        "Refiner Level\u00a0II"
    ],
    "recycles_into": [
        {
            "amount": 2,
            "loot_name": "Rubber Parts"
        }
    ],
    "rarity": "Green",
    "craftable": false,
    "description": "",
    "sell_value": 0,
    "loot_name": "Wires"
}
```

## license
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

All game content, including but not limited to game mechanics, items, names, and imagery, is copyright © Embark Studios AB. This repository is a community resource and is not affiliated with or endorsed by Embark Studios AB.
