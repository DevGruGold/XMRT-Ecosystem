// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IXMRT {
    function transfer(address,uint256) external returns (bool);
}

contract RewardsManager {
    IXMRT public xmrt;
    mapping(string => uint256) public userContrib;
    mapping(string => bool) public claimed;

    constructor(address _xmrt) {
        xmrt = IXMRT(_xmrt);
    }

    function record(string memory uid, uint256 amount) external {
        userContrib[uid] += amount;
    }

    function claim(string memory uid) external {
        require(!claimed[uid], "Already claimed");
        uint256 amt = userContrib[uid];
        claimed[uid] = true;
        xmrt.transfer(msg.sender, amt);
    }
}
