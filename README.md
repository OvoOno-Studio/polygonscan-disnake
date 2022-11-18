# PolygonScan Web Scraper Discord bot
= disnake and polygonscan api

## Comands

```
Prefix command: ps-
ps-ping - Return bot latency
ps-getTrxHash <transaction hash> - Return a link to for specific transaction hash.
ps-getTrx <wallet address> <offset> - Return a list of normal transaction for specific address
ps-getBalance <wallet address> -Get amount in MATIC for single address. 
ps-getErc20 <wallet address> <contract address> <offset> - Return list of ERC-20 transactions, can be filtered by specific smart contract address.
ps-getErc721 <wallet address> <contract address> <offset> - Return list of ERC-721 (NFT) transactions, can be filtered by specific smart contract address.
```