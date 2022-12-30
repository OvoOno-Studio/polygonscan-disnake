# PolygonScan Web Scraper Discord bot
A Discord bot that uses the [Polygonscan API](https://polygonscan.com/apis) to provide access to various blockchain data and functionality, such as querying the state of a contract, retrieving transaction history, or submitting transactions.

This bot uses the [Polygonscan API](https://polygonscan.com/apis) and [Disnake](https://docs.disnake.dev/en/stable/)

## Commands

```
Prefix command: ps-
ps-ping - Return bot latency
ps-getTrxHash <transaction hash> - Return a link to for specific transaction hash.
ps-getTrx <wallet address> <offset> - Return a list of normal transaction for specific address
ps-getBalance <wallet address> -Get amount in MATIC for single address. 
ps-getErc20 <wallet address> <contract address> <offset> - Return list of ERC-20 transactions, can be filtered by specific smart contract address.
ps-getErc721 <wallet address> <contract address> <offset> - Return list of ERC-721 (NFT) transactions, can be filtered by specific smart contract address.
```
