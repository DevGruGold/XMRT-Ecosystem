/// @title Treasury
/// @notice This contract manages the DAO treasury and fund allocation

#[starknet::contract]
mod Treasury {
    use starknet::{ContractAddress, get_caller_address, get_block_timestamp};
    use core::array::ArrayTrait;
    use core::traits::Into;

    #[storage]
    struct Storage {
        // Access control
        admin: ContractAddress,
        governance_contract: ContractAddress,
        
        // Treasury balances
        eth_balance: u256,
        token_balances: LegacyMap<ContractAddress, u256>,
        
        // Allocation tracking
        allocation_count: u256,
        allocations: LegacyMap<u256, Allocation>,
        
        // Emergency controls
        emergency_pause: bool,
        emergency_admin: ContractAddress,
    }

    #[derive(Drop, Serde, starknet::Store)]
    struct Allocation {
        id: u256,
        recipient: ContractAddress,
        token: ContractAddress, // Zero address for ETH
        amount: u256,
        purpose: felt252,
        allocated_at: u64,
        executed: bool,
        approved_by: ContractAddress,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        FundsDeposited: FundsDeposited,
        FundsAllocated: FundsAllocated,
        AllocationExecuted: AllocationExecuted,
        EmergencyPause: EmergencyPause,
        EmergencyUnpause: EmergencyUnpause,
    }

    #[derive(Drop, starknet::Event)]
    struct FundsDeposited {
        #[key]
        depositor: ContractAddress,
        token: ContractAddress,
        amount: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct FundsAllocated {
        #[key]
        allocation_id: u256,
        recipient: ContractAddress,
        token: ContractAddress,
        amount: u256,
        purpose: felt252,
    }

    #[derive(Drop, starknet::Event)]
    struct AllocationExecuted {
        #[key]
        allocation_id: u256,
        recipient: ContractAddress,
        amount: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct EmergencyPause {
        admin: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct EmergencyUnpause {
        admin: ContractAddress,
    }

    #[constructor]
    fn constructor(
        ref self: ContractState,
        admin: ContractAddress,
        governance_contract: ContractAddress,
        emergency_admin: ContractAddress,
    ) {
        self.admin.write(admin);
        self.governance_contract.write(governance_contract);
        self.emergency_admin.write(emergency_admin);
        self.allocation_count.write(0);
        self.emergency_pause.write(false);
    }

    #[abi(embed_v0)]
    impl TreasuryImpl of ITreasury<ContractState> {
        fn deposit_eth(ref self: ContractState) {
            self._require_not_paused();
            let caller = get_caller_address();
            
            // In a real implementation, this would handle ETH deposits
            // For now, we'll simulate with a placeholder amount
            let amount = 1000; // Placeholder
            
            let current_balance = self.eth_balance.read();
            self.eth_balance.write(current_balance + amount);
            
            self.emit(FundsDeposited {
                depositor: caller,
                token: starknet::contract_address_const::<0>(), // Zero address for ETH
                amount,
            });
        }

        fn deposit_token(ref self: ContractState, token: ContractAddress, amount: u256) {
            self._require_not_paused();
            let caller = get_caller_address();
            
            // In a real implementation, this would transfer tokens from caller
            // For now, we'll just update the balance
            let current_balance = self.token_balances.read(token);
            self.token_balances.write(token, current_balance + amount);
            
            self.emit(FundsDeposited {
                depositor: caller,
                token,
                amount,
            });
        }

        fn allocate_funds(
            ref self: ContractState,
            recipient: ContractAddress,
            token: ContractAddress,
            amount: u256,
            purpose: felt252,
        ) -> u256 {
            self._require_not_paused();
            self._only_governance();
            
            // Check if treasury has sufficient funds
            if token == starknet::contract_address_const::<0>() {
                assert(self.eth_balance.read() >= amount, 'Insufficient ETH balance');
            } else {
                assert(self.token_balances.read(token) >= amount, 'Insufficient token balance');
            }
            
            let allocation_id = self.allocation_count.read() + 1;
            self.allocation_count.write(allocation_id);
            
            let allocation = Allocation {
                id: allocation_id,
                recipient,
                token,
                amount,
                purpose,
                allocated_at: get_block_timestamp(),
                executed: false,
                approved_by: get_caller_address(),
            };
            
            self.allocations.write(allocation_id, allocation);
            
            self.emit(FundsAllocated {
                allocation_id,
                recipient,
                token,
                amount,
                purpose,
            });
            
            allocation_id
        }

        fn execute_allocation(ref self: ContractState, allocation_id: u256) {
            self._require_not_paused();
            
            let mut allocation = self.allocations.read(allocation_id);
            assert(allocation.id != 0, 'Allocation does not exist');
            assert(!allocation.executed, 'Allocation already executed');
            
            // Only governance or admin can execute
            let caller = get_caller_address();
            assert(
                caller == self.governance_contract.read() || caller == self.admin.read(),
                'Not authorized to execute'
            );
            
            // Update balances
            if allocation.token == starknet::contract_address_const::<0>() {
                let current_balance = self.eth_balance.read();
                self.eth_balance.write(current_balance - allocation.amount);
            } else {
                let current_balance = self.token_balances.read(allocation.token);
                self.token_balances.write(allocation.token, current_balance - allocation.amount);
            }
            
            allocation.executed = true;
            self.allocations.write(allocation_id, allocation);
            
            // In a real implementation, this would transfer funds to recipient
            
            self.emit(AllocationExecuted {
                allocation_id,
                recipient: allocation.recipient,
                amount: allocation.amount,
            });
        }

        fn emergency_pause(ref self: ContractState) {
            let caller = get_caller_address();
            assert(
                caller == self.emergency_admin.read() || caller == self.admin.read(),
                'Not authorized for emergency pause'
            );
            
            self.emergency_pause.write(true);
            self.emit(EmergencyPause { admin: caller });
        }

        fn emergency_unpause(ref self: ContractState) {
            let caller = get_caller_address();
            assert(
                caller == self.emergency_admin.read() || caller == self.admin.read(),
                'Not authorized for emergency unpause'
            );
            
            self.emergency_pause.write(false);
            self.emit(EmergencyUnpause { admin: caller });
        }

        fn get_eth_balance(self: @ContractState) -> u256 {
            self.eth_balance.read()
        }

        fn get_token_balance(self: @ContractState, token: ContractAddress) -> u256 {
            self.token_balances.read(token)
        }

        fn get_allocation(self: @ContractState, allocation_id: u256) -> Allocation {
            self.allocations.read(allocation_id)
        }

        fn get_allocation_count(self: @ContractState) -> u256 {
            self.allocation_count.read()
        }

        fn is_paused(self: @ContractState) -> bool {
            self.emergency_pause.read()
        }

        fn set_governance_contract(ref self: ContractState, new_governance: ContractAddress) {
            self._only_admin();
            self.governance_contract.write(new_governance);
        }

        fn set_emergency_admin(ref self: ContractState, new_emergency_admin: ContractAddress) {
            self._only_admin();
            self.emergency_admin.write(new_emergency_admin);
        }
    }

    #[generate_trait]
    impl InternalImpl of InternalTrait {
        fn _only_admin(self: @ContractState) {
            assert(get_caller_address() == self.admin.read(), 'Only admin');
        }

        fn _only_governance(self: @ContractState) {
            assert(get_caller_address() == self.governance_contract.read(), 'Only governance');
        }

        fn _require_not_paused(self: @ContractState) {
            assert(!self.emergency_pause.read(), 'Contract is paused');
        }
    }
}

#[starknet::interface]
trait ITreasury<TContractState> {
    fn deposit_eth(ref self: TContractState);
    fn deposit_token(ref self: TContractState, token: ContractAddress, amount: u256);
    fn allocate_funds(
        ref self: TContractState,
        recipient: ContractAddress,
        token: ContractAddress,
        amount: u256,
        purpose: felt252,
    ) -> u256;
    fn execute_allocation(ref self: TContractState, allocation_id: u256);
    fn emergency_pause(ref self: TContractState);
    fn emergency_unpause(ref self: TContractState);
    
    fn get_eth_balance(self: @TContractState) -> u256;
    fn get_token_balance(self: @TContractState, token: ContractAddress) -> u256;
    fn get_allocation(self: @TContractState, allocation_id: u256) -> Treasury::Allocation;
    fn get_allocation_count(self: @TContractState) -> u256;
    fn is_paused(self: @TContractState) -> bool;
    
    fn set_governance_contract(ref self: TContractState, new_governance: ContractAddress);
    fn set_emergency_admin(ref self: TContractState, new_emergency_admin: ContractAddress);
}

