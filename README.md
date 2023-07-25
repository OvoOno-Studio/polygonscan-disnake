# PolygonScan Web Scraper Discord bot
A Discord bot that uses the [Polygonscan API](https://polygonscan.com/apis) and [Disnake](https://docs.disnake.dev/en/stable/) library to provide access to various blockchain data and functionality, such as querying the state of a contract, retrieving transaction history, or submitting transactions. 

PolygonScan Web Scraper Discord does not require any administrative privileges neither store any data.

Website[Website](https://polygonscan-scrapper.ovoono.studio/) 
Top.GG Profile[Top.GG Profile](https://top.gg/bot/1041454438595965049)

### Scopes
- bot
- applications.commands

### Bot Permissions
- Send Messages
- Embed Links
- Attach Files

## Setup
 

Bot has additional features such as monitoring crypto wallets for incoming transaction and price changes alert. To properly setup run next commands:

- ``` ps-set_wallet_address <wallet>``` Set set crypto wallet to monitor for new changes
- ``` ps-set_transaction_channel <your_transaction_channel_id``` Set channel to get incoming transaction as message.
- ``` ps-set_price_alert_channel <your_price_alert_channel_id``` Set channel to get alerts for new price changes.

Full features can be unlocked by one-time donation payment through PayPal. Donations is giving OvoSupportes much upgradable functionalities, such as return CSV files, scrapping up to the 1000 transaction and much more. To checkout more information run:

```ps-donate```

## Commands

Prefix command: ```ps-```

- ```ps-ping```  Return bot latency. 
- ```ps-help``` List all commands
- ```ps-help <command>``` More info on a command
- ```ps-donate``` Display how to donate information
- ```ps-creator``` Returns a contract's deployer address and transaction hash it was created, up to 5 at a time
- ```ps-gas``` Returns the current Safe, Proposed and Fast gas prices
- ```ps-abi``` Returns the contract Application Binary Interface ( ABI ) of a verified smart contract.
- ```ps-help``` 
- ```ps-getTrxHash <transaction hash>``` Return a link to for specific transaction hash. 
- ```ps-getTrx <wallet address> <offset>``` Return a list of normal transaction for specific address.
- ```ps-getTokenHolder <token_smart_contract>``` Return 1000 holders of specific ERC20 token.
- ```ps-getBalance <wallet address>``` Get amount in MATIC for single address. 
- ```ps-getErc20 <wallet address> <contract address> <offset>``` Return list of ERC-20 transactions, can be filtered by specific smart contract address. 
- ```ps-getErc721 <wallet address> <contract address> <offset>``` Return list of ERC-721 (NFT) transactions, can be filtered by specific smart contract address. 
- ```ps-getErc1115 <wallet address> <contract address> <offset>``` Return list of ERC-721 (NFT) transactions, can be filtered by specific smart contract address
