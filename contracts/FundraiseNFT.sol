// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

contract FundraiseNFT is ERC721, Ownable {
    using Strings for uint256;
    
    uint256 private _tokenIds;
    string public baseURI;
    mapping(uint256 => uint256) public fundraiseToTokenCount;
    uint256 public constant MIN_RSC_AMOUNT = 1000; // Minimum RSC required for NFT
    
    struct NFTMetadata {
        string image;
        string name;
        string description;
    }
    
    mapping(uint256 => NFTMetadata) public fundraiseMetadata;

    constructor() ERC721("ResearchHub Fundraise", "RHF") Ownable(msg.sender) {
        baseURI = "https://api.researchhub.com/api/nft/";
    }

    function setBaseURI(string memory _newBaseURI) public onlyOwner {
        baseURI = _newBaseURI;
    }

    function _baseURI() internal view override returns (string memory) {
        return baseURI;
    }

    function setFundraiseMetadata(
        uint256 fundraiseId,
        string memory image,
        string memory name,
        string memory description
    ) public onlyOwner {
        fundraiseMetadata[fundraiseId] = NFTMetadata(image, name, description);
    }

    function mint(address to, uint256 fundraiseId) public onlyOwner returns (uint256) {
        _tokenIds++;
        uint256 newTokenId = _tokenIds;
        _safeMint(to, newTokenId);
        fundraiseToTokenCount[fundraiseId]++;
        return newTokenId;
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        _requireOwned(tokenId);
        return string(abi.encodePacked(baseURI, tokenId.toString()));
    }
} 