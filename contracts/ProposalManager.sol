// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ProposalManager {
    struct Proposal {
        string description;
        uint256 yes;
        uint256 no;
        uint256 deadline;
        bool executed;
    }

    Proposal[] public proposals;
    mapping(address => mapping(uint => bool)) public voted;

    function submitProposal(string memory desc) public {
        proposals.push(Proposal(desc, 0, 0, block.timestamp + 3 days, false));
    }

    function vote(uint id, bool support) public {
        require(block.timestamp < proposals[id].deadline, "Expired");
        require(!voted[msg.sender][id], "Already voted");
        voted[msg.sender][id] = true;
        if (support) proposals[id].yes++;
        else proposals[id].no++;
    }

    function execute(uint id) public {
        Proposal storage p = proposals[id];
        require(block.timestamp >= p.deadline && !p.executed, "Can't execute");
        require(p.yes > p.no, "Rejected");
        p.executed = true;
    }
}
