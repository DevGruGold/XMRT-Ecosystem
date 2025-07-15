/// @title Governance
/// @notice This contract implements comprehensive governance functionality for the XMRT DAO

#[starknet::contract]
mod Governance {
    use starknet::{ContractAddress, get_caller_address, get_block_timestamp};
    use core::array::ArrayTrait;
    use core::traits::Into;

    #[storage]
    struct Storage {
        // Governance parameters
        voting_delay: u64,
        voting_period: u64,
        proposal_threshold: u256,
        quorum_threshold: u256,
        
        // Proposal tracking
        proposal_count: u256,
        proposals: LegacyMap<u256, Proposal>,
        votes: LegacyMap<(u256, ContractAddress), Vote>,
        proposal_votes: LegacyMap<u256, ProposalVotes>,
        
        // Access control
        admin: ContractAddress,
        token_contract: ContractAddress,
    }

    #[derive(Drop, Serde, starknet::Store)]
    struct Proposal {
        id: u256,
        proposer: ContractAddress,
        title: felt252,
        description: felt252,
        start_time: u64,
        end_time: u64,
        executed: bool,
        cancelled: bool,
        target: ContractAddress,
        value: u256,
        calldata: felt252,
    }

    #[derive(Drop, Serde, starknet::Store)]
    struct Vote {
        support: bool,
        weight: u256,
        timestamp: u64,
    }

    #[derive(Drop, Serde, starknet::Store)]
    struct ProposalVotes {
        for_votes: u256,
        against_votes: u256,
        abstain_votes: u256,
        total_votes: u256,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        ProposalCreated: ProposalCreated,
        VoteCast: VoteCast,
        ProposalExecuted: ProposalExecuted,
        ProposalCancelled: ProposalCancelled,
    }

    #[derive(Drop, starknet::Event)]
    struct ProposalCreated {
        #[key]
        proposal_id: u256,
        proposer: ContractAddress,
        title: felt252,
        start_time: u64,
        end_time: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct VoteCast {
        #[key]
        voter: ContractAddress,
        #[key]
        proposal_id: u256,
        support: bool,
        weight: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct ProposalExecuted {
        #[key]
        proposal_id: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct ProposalCancelled {
        #[key]
        proposal_id: u256,
    }

    #[constructor]
    fn constructor(
        ref self: ContractState,
        admin: ContractAddress,
        token_contract: ContractAddress,
        voting_delay: u64,
        voting_period: u64,
        proposal_threshold: u256,
        quorum_threshold: u256,
    ) {
        self.admin.write(admin);
        self.token_contract.write(token_contract);
        self.voting_delay.write(voting_delay);
        self.voting_period.write(voting_period);
        self.proposal_threshold.write(proposal_threshold);
        self.quorum_threshold.write(quorum_threshold);
        self.proposal_count.write(0);
    }

    #[abi(embed_v0)]
    impl GovernanceImpl of IGovernance<ContractState> {
        fn create_proposal(
            ref self: ContractState,
            title: felt252,
            description: felt252,
            target: ContractAddress,
            value: u256,
            calldata: felt252,
        ) -> u256 {
            let caller = get_caller_address();
            let current_time = get_block_timestamp();
            
            // Check if proposer has enough tokens
            let proposer_balance = self._get_voting_power(caller);
            assert(proposer_balance >= self.proposal_threshold.read(), 'Insufficient tokens to propose');
            
            let proposal_id = self.proposal_count.read() + 1;
            self.proposal_count.write(proposal_id);
            
            let start_time = current_time + self.voting_delay.read();
            let end_time = start_time + self.voting_period.read();
            
            let proposal = Proposal {
                id: proposal_id,
                proposer: caller,
                title,
                description,
                start_time,
                end_time,
                executed: false,
                cancelled: false,
                target,
                value,
                calldata,
            };
            
            self.proposals.write(proposal_id, proposal);
            
            // Initialize proposal votes
            let initial_votes = ProposalVotes {
                for_votes: 0,
                against_votes: 0,
                abstain_votes: 0,
                total_votes: 0,
            };
            self.proposal_votes.write(proposal_id, initial_votes);
            
            self.emit(ProposalCreated {
                proposal_id,
                proposer: caller,
                title,
                start_time,
                end_time,
            });
            
            proposal_id
        }

        fn cast_vote(
            ref self: ContractState,
            proposal_id: u256,
            support: bool,
        ) {
            let caller = get_caller_address();
            let current_time = get_block_timestamp();
            
            let proposal = self.proposals.read(proposal_id);
            assert(proposal.id != 0, 'Proposal does not exist');
            assert(current_time >= proposal.start_time, 'Voting not started');
            assert(current_time <= proposal.end_time, 'Voting period ended');
            assert(!proposal.executed, 'Proposal already executed');
            assert(!proposal.cancelled, 'Proposal cancelled');
            
            // Check if user already voted
            let existing_vote = self.votes.read((proposal_id, caller));
            assert(existing_vote.weight == 0, 'Already voted');
            
            let voting_power = self._get_voting_power(caller);
            assert(voting_power > 0, 'No voting power');
            
            let vote = Vote {
                support,
                weight: voting_power,
                timestamp: current_time,
            };
            
            self.votes.write((proposal_id, caller), vote);
            
            // Update proposal vote counts
            let mut proposal_votes = self.proposal_votes.read(proposal_id);
            if support {
                proposal_votes.for_votes += voting_power;
            } else {
                proposal_votes.against_votes += voting_power;
            }
            proposal_votes.total_votes += voting_power;
            self.proposal_votes.write(proposal_id, proposal_votes);
            
            self.emit(VoteCast {
                voter: caller,
                proposal_id,
                support,
                weight: voting_power,
            });
        }

        fn execute_proposal(ref self: ContractState, proposal_id: u256) {
            let caller = get_caller_address();
            let current_time = get_block_timestamp();
            
            let mut proposal = self.proposals.read(proposal_id);
            assert(proposal.id != 0, 'Proposal does not exist');
            assert(current_time > proposal.end_time, 'Voting period not ended');
            assert(!proposal.executed, 'Proposal already executed');
            assert(!proposal.cancelled, 'Proposal cancelled');
            
            let proposal_votes = self.proposal_votes.read(proposal_id);
            
            // Check quorum
            assert(proposal_votes.total_votes >= self.quorum_threshold.read(), 'Quorum not reached');
            
            // Check if proposal passed
            assert(proposal_votes.for_votes > proposal_votes.against_votes, 'Proposal failed');
            
            proposal.executed = true;
            self.proposals.write(proposal_id, proposal);
            
            // Execute the proposal (simplified - in practice would call target contract)
            // This would involve calling the target contract with the specified calldata
            
            self.emit(ProposalExecuted { proposal_id });
        }

        fn cancel_proposal(ref self: ContractState, proposal_id: u256) {
            let caller = get_caller_address();
            
            let mut proposal = self.proposals.read(proposal_id);
            assert(proposal.id != 0, 'Proposal does not exist');
            assert(!proposal.executed, 'Proposal already executed');
            assert(!proposal.cancelled, 'Proposal already cancelled');
            
            // Only proposer or admin can cancel
            assert(
                caller == proposal.proposer || caller == self.admin.read(),
                'Not authorized to cancel'
            );
            
            proposal.cancelled = true;
            self.proposals.write(proposal_id, proposal);
            
            self.emit(ProposalCancelled { proposal_id });
        }

        fn get_proposal(self: @ContractState, proposal_id: u256) -> Proposal {
            self.proposals.read(proposal_id)
        }

        fn get_proposal_votes(self: @ContractState, proposal_id: u256) -> ProposalVotes {
            self.proposal_votes.read(proposal_id)
        }

        fn get_vote(self: @ContractState, proposal_id: u256, voter: ContractAddress) -> Vote {
            self.votes.read((proposal_id, voter))
        }

        fn get_voting_power(self: @ContractState, account: ContractAddress) -> u256 {
            self._get_voting_power(account)
        }

        fn get_proposal_count(self: @ContractState) -> u256 {
            self.proposal_count.read()
        }

        fn get_voting_delay(self: @ContractState) -> u64 {
            self.voting_delay.read()
        }

        fn get_voting_period(self: @ContractState) -> u64 {
            self.voting_period.read()
        }

        fn get_proposal_threshold(self: @ContractState) -> u256 {
            self.proposal_threshold.read()
        }

        fn get_quorum_threshold(self: @ContractState) -> u256 {
            self.quorum_threshold.read()
        }
    }

    #[generate_trait]
    impl InternalImpl of InternalTrait {
        fn _get_voting_power(self: @ContractState, account: ContractAddress) -> u256 {
            // This would interface with the XMRT token contract to get voting power
            // For now, returning a placeholder value
            // In practice, this would call the token contract's balance_of function
            1000 // Placeholder
        }

        fn _only_admin(self: @ContractState) {
            assert(get_caller_address() == self.admin.read(), 'Only admin');
        }
    }
}

#[starknet::interface]
trait IGovernance<TContractState> {
    fn create_proposal(
        ref self: TContractState,
        title: felt252,
        description: felt252,
        target: ContractAddress,
        value: u256,
        calldata: felt252,
    ) -> u256;
    
    fn cast_vote(ref self: TContractState, proposal_id: u256, support: bool);
    fn execute_proposal(ref self: TContractState, proposal_id: u256);
    fn cancel_proposal(ref self: TContractState, proposal_id: u256);
    
    fn get_proposal(self: @TContractState, proposal_id: u256) -> Governance::Proposal;
    fn get_proposal_votes(self: @TContractState, proposal_id: u256) -> Governance::ProposalVotes;
    fn get_vote(self: @TContractState, proposal_id: u256, voter: ContractAddress) -> Governance::Vote;
    fn get_voting_power(self: @TContractState, account: ContractAddress) -> u256;
    fn get_proposal_count(self: @TContractState) -> u256;
    fn get_voting_delay(self: @TContractState) -> u64;
    fn get_voting_period(self: @TContractState) -> u64;
    fn get_proposal_threshold(self: @TContractState) -> u256;
    fn get_quorum_threshold(self: @TContractState) -> u256;
}

