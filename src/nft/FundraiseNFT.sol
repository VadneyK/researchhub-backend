// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ResearchHubNFT is ERC721, Ownable {
    uint256 private _nextTokenId;

    constructor() ERC721("ResearchHub NFT", "RHNFT") Ownable(msg.sender) {}

    function mint() public returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _safeMint(msg.sender, tokenId);
        return tokenId;
    }
}