// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract TreasuryManager {
    address public owner;
    mapping(address => uint256) public grants;

    constructor() {
        owner = msg.sender;
    }

    receive() external payable {}

    function approveGrant(address recipient, uint256 amount) public {
        require(msg.sender == owner, "Not authorized");
        grants[recipient] += amount;
    }

    function withdrawGrant() public {
        uint256 amount = grants[msg.sender];
        require(amount > 0, "No grant approved");
        grants[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }

    function balance() public view returns (uint256) {
        return address(this).balance;
    }
}
