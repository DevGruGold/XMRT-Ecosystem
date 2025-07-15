/// @title CrossChainBridge
/// @notice This contract handles cross-chain token transfers and bridge operations

#[starknet::contract]
mod CrossChainBridge {
    use starknet::{ContractAddress, get_caller_address, get_block_timestamp};
    use core::array::ArrayTrait;
    use core::traits::Into;

    #[storage]
    struct Storage {
        // Access control
        admin: ContractAddress,
        bridge_operators: LegacyMap<ContractAddress, bool>,
        
        // Bridge configuration
        xmrt_token: ContractAddress,
        bridge_fee: u256,
        min_bridge_amount: u256,
        max_bridge_amount: u256,
        
        // Supported chains
        supported_chains: LegacyMap<u32, bool>,
        chain_configs: LegacyMap<u32, ChainConfig>,
        
        // Bridge transactions
        transaction_count: u256,
        bridge_transactions: LegacyMap<u256, BridgeTransaction>,
        user_transactions: LegacyMap<(ContractAddress, u256), u256>,
        
        // Liquidity management
        chain_liquidity: LegacyMap<u32, u256>,
        total_locked: u256,
        
        // Security features
        paused: bool,
        daily_limits: LegacyMap<u32, u256>,
        daily_volumes: LegacyMap<(u32, u64), u256>, // (chain_id, day) -> volume
        
        // Validator consensus
        required_confirmations: u32,
        transaction_confirmations: LegacyMap<(u256, ContractAddress), bool>,
        confirmation_counts: LegacyMap<u256, u32>,
    }

    #[derive(Drop, Serde, starknet::Store)]
    struct ChainConfig {
        chain_id: u32,
        name: felt252,
        bridge_address: felt252,
        is_active: bool,
        fee_multiplier: u256, // Basis points (10000 = 100%)
    }

    #[derive(Drop, Serde, starknet::Store)]
    struct BridgeTransaction {
        id: u256,
        user: ContractAddress,
        source_chain: u32,
        destination_chain: u32,
        amount: u256,
        fee: u256,
        status: u8, // 0: pending, 1: confirmed, 2: completed, 3: failed
        created_at: u64,
        completed_at: u64,
        tx_hash: felt252,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        BridgeInitiated: BridgeInitiated,
        BridgeConfirmed: BridgeConfirmed,
        BridgeCompleted: BridgeCompleted,
        BridgeFailed: BridgeFailed,
        ChainAdded: ChainAdded,
        ChainUpdated: ChainUpdated,
        OperatorAdded: OperatorAdded,
        OperatorRemoved: OperatorRemoved,
        LiquidityAdded: LiquidityAdded,
        LiquidityRemoved: LiquidityRemoved,
        Paused: Paused,
        Unpaused: Unpaused,
    }

    #[derive(Drop, starknet::Event)]
    struct BridgeInitiated {
        #[key]
        transaction_id: u256,
        #[key]
        user: ContractAddress,
        source_chain: u32,
        destination_chain: u32,
        amount: u256,
        fee: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct BridgeConfirmed {
        #[key]
        transaction_id: u256,
        #[key]
        operator: ContractAddress,
        confirmations: u32,
    }

    #[derive(Drop, starknet::Event)]
    struct BridgeCompleted {
        #[key]
        transaction_id: u256,
        #[key]
        user: ContractAddress,
        amount: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct BridgeFailed {
        #[key]
        transaction_id: u256,
        reason: felt252,
    }

    #[derive(Drop, starknet::Event)]
    struct ChainAdded {
        chain_id: u32,
        name: felt252,
    }

    #[derive(Drop, starknet::Event)]
    struct ChainUpdated {
        chain_id: u32,
        is_active: bool,
    }

    #[derive(Drop, starknet::Event)]
    struct OperatorAdded {
        #[key]
        operator: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct OperatorRemoved {
        #[key]
        operator: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct LiquidityAdded {
        chain_id: u32,
        amount: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct LiquidityRemoved {
        chain_id: u32,
        amount: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct Paused {
        admin: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct Unpaused {
        admin: ContractAddress,
    }

    #[constructor]
    fn constructor(
        ref self: ContractState,
        admin: ContractAddress,
        xmrt_token: ContractAddress,
        bridge_fee: u256,
        min_bridge_amount: u256,
        max_bridge_amount: u256,
        required_confirmations: u32,
    ) {
        self.admin.write(admin);
        self.xmrt_token.write(xmrt_token);
        self.bridge_fee.write(bridge_fee);
        self.min_bridge_amount.write(min_bridge_amount);
        self.max_bridge_amount.write(max_bridge_amount);
        self.required_confirmations.write(required_confirmations);
        self.transaction_count.write(0);
        self.paused.write(false);
        
        // Add admin as initial bridge operator
        self.bridge_operators.write(admin, true);
    }

    #[abi(embed_v0)]
    impl CrossChainBridgeImpl of ICrossChainBridge<ContractState> {
        fn initiate_bridge(
            ref self: ContractState,
            destination_chain: u32,
            amount: u256,
            recipient: felt252,
        ) -> u256 {
            self._require_not_paused();
            assert(amount >= self.min_bridge_amount.read(), 'Amount below minimum');
            assert(amount <= self.max_bridge_amount.read(), 'Amount above maximum');
            assert(self.supported_chains.read(destination_chain), 'Unsupported destination chain');
            
            let caller = get_caller_address();
            let current_time = get_block_timestamp();
            
            // Check daily limits
            let today = current_time / 86400; // Convert to days
            let daily_volume = self.daily_volumes.read((destination_chain, today));
            let daily_limit = self.daily_limits.read(destination_chain);
            assert(daily_volume + amount <= daily_limit, 'Daily limit exceeded');
            
            // Calculate fee
            let chain_config = self.chain_configs.read(destination_chain);
            let base_fee = self.bridge_fee.read();
            let fee = base_fee * chain_config.fee_multiplier / 10000;
            let total_amount = amount + fee;
            
            // Check user balance and transfer tokens
            // In a real implementation, this would call the XMRT token contract
            
            let transaction_id = self.transaction_count.read() + 1;
            self.transaction_count.write(transaction_id);
            
            let bridge_tx = BridgeTransaction {
                id: transaction_id,
                user: caller,
                source_chain: 1, // Assuming Starknet is chain ID 1
                destination_chain,
                amount,
                fee,
                status: 0, // pending
                created_at: current_time,
                completed_at: 0,
                tx_hash: 0,
            };
            
            self.bridge_transactions.write(transaction_id, bridge_tx);
            
            // Update daily volume
            self.daily_volumes.write((destination_chain, today), daily_volume + amount);
            
            // Lock tokens
            let current_locked = self.total_locked.read();
            self.total_locked.write(current_locked + total_amount);
            
            self.emit(BridgeInitiated {
                transaction_id,
                user: caller,
                source_chain: 1,
                destination_chain,
                amount,
                fee,
            });
            
            transaction_id
        }

        fn confirm_bridge(ref self: ContractState, transaction_id: u256, tx_hash: felt252) {
            self._only_operator();
            
            let caller = get_caller_address();
            assert(!self.transaction_confirmations.read((transaction_id, caller)), 'Already confirmed');
            
            let bridge_tx = self.bridge_transactions.read(transaction_id);
            assert(bridge_tx.id != 0, 'Transaction does not exist');
            assert(bridge_tx.status == 0, 'Transaction not pending');
            
            self.transaction_confirmations.write((transaction_id, caller), true);
            
            let current_confirmations = self.confirmation_counts.read(transaction_id) + 1;
            self.confirmation_counts.write(transaction_id, current_confirmations);
            
            self.emit(BridgeConfirmed {
                transaction_id,
                operator: caller,
                confirmations: current_confirmations,
            });
            
            // If enough confirmations, mark as confirmed
            if current_confirmations >= self.required_confirmations.read() {
                let mut updated_tx = bridge_tx;
                updated_tx.status = 1; // confirmed
                updated_tx.tx_hash = tx_hash;
                self.bridge_transactions.write(transaction_id, updated_tx);
            }
        }

        fn complete_bridge(ref self: ContractState, transaction_id: u256) {
            self._only_operator();
            
            let mut bridge_tx = self.bridge_transactions.read(transaction_id);
            assert(bridge_tx.id != 0, 'Transaction does not exist');
            assert(bridge_tx.status == 1, 'Transaction not confirmed');
            
            bridge_tx.status = 2; // completed
            bridge_tx.completed_at = get_block_timestamp();
            self.bridge_transactions.write(transaction_id, bridge_tx);
            
            // Release locked tokens (they were sent to destination chain)
            let current_locked = self.total_locked.read();
            self.total_locked.write(current_locked - (bridge_tx.amount + bridge_tx.fee));
            
            self.emit(BridgeCompleted {
                transaction_id,
                user: bridge_tx.user,
                amount: bridge_tx.amount,
            });
        }

        fn fail_bridge(ref self: ContractState, transaction_id: u256, reason: felt252) {
            self._only_operator();
            
            let mut bridge_tx = self.bridge_transactions.read(transaction_id);
            assert(bridge_tx.id != 0, 'Transaction does not exist');
            assert(bridge_tx.status <= 1, 'Transaction already processed');
            
            bridge_tx.status = 3; // failed
            self.bridge_transactions.write(transaction_id, bridge_tx);
            
            // Refund tokens to user
            // In a real implementation, this would call the XMRT token contract
            
            // Release locked tokens
            let current_locked = self.total_locked.read();
            self.total_locked.write(current_locked - (bridge_tx.amount + bridge_tx.fee));
            
            self.emit(BridgeFailed {
                transaction_id,
                reason,
            });
        }

        fn add_supported_chain(
            ref self: ContractState,
            chain_id: u32,
            name: felt252,
            bridge_address: felt252,
            fee_multiplier: u256,
            daily_limit: u256,
        ) {
            self._only_admin();
            
            let chain_config = ChainConfig {
                chain_id,
                name,
                bridge_address,
                is_active: true,
                fee_multiplier,
            };
            
            self.supported_chains.write(chain_id, true);
            self.chain_configs.write(chain_id, chain_config);
            self.daily_limits.write(chain_id, daily_limit);
            
            self.emit(ChainAdded { chain_id, name });
        }

        fn update_chain_status(ref self: ContractState, chain_id: u32, is_active: bool) {
            self._only_admin();
            
            let mut chain_config = self.chain_configs.read(chain_id);
            assert(chain_config.chain_id != 0, 'Chain does not exist');
            
            chain_config.is_active = is_active;
            self.chain_configs.write(chain_id, chain_config);
            self.supported_chains.write(chain_id, is_active);
            
            self.emit(ChainUpdated { chain_id, is_active });
        }

        fn add_bridge_operator(ref self: ContractState, operator: ContractAddress) {
            self._only_admin();
            self.bridge_operators.write(operator, true);
            self.emit(OperatorAdded { operator });
        }

        fn remove_bridge_operator(ref self: ContractState, operator: ContractAddress) {
            self._only_admin();
            self.bridge_operators.write(operator, false);
            self.emit(OperatorRemoved { operator });
        }

        fn pause(ref self: ContractState) {
            self._only_admin();
            self.paused.write(true);
            self.emit(Paused { admin: get_caller_address() });
        }

        fn unpause(ref self: ContractState) {
            self._only_admin();
            self.paused.write(false);
            self.emit(Unpaused { admin: get_caller_address() });
        }

        fn get_bridge_transaction(self: @ContractState, transaction_id: u256) -> BridgeTransaction {
            self.bridge_transactions.read(transaction_id)
        }

        fn get_chain_config(self: @ContractState, chain_id: u32) -> ChainConfig {
            self.chain_configs.read(chain_id)
        }

        fn get_transaction_confirmations(self: @ContractState, transaction_id: u256) -> u32 {
            self.confirmation_counts.read(transaction_id)
        }

        fn is_chain_supported(self: @ContractState, chain_id: u32) -> bool {
            self.supported_chains.read(chain_id)
        }

        fn is_bridge_operator(self: @ContractState, operator: ContractAddress) -> bool {
            self.bridge_operators.read(operator)
        }

        fn get_daily_volume(self: @ContractState, chain_id: u32, day: u64) -> u256 {
            self.daily_volumes.read((chain_id, day))
        }

        fn get_daily_limit(self: @ContractState, chain_id: u32) -> u256 {
            self.daily_limits.read(chain_id)
        }

        fn get_total_locked(self: @ContractState) -> u256 {
            self.total_locked.read()
        }

        fn is_paused(self: @ContractState) -> bool {
            self.paused.read()
        }
    }

    #[generate_trait]
    impl InternalImpl of InternalTrait {
        fn _only_admin(self: @ContractState) {
            assert(get_caller_address() == self.admin.read(), 'Only admin');
        }

        fn _only_operator(self: @ContractState) {
            assert(self.bridge_operators.read(get_caller_address()), 'Only bridge operator');
        }

        fn _require_not_paused(self: @ContractState) {
            assert(!self.paused.read(), 'Contract is paused');
        }
    }
}

#[starknet::interface]
trait ICrossChainBridge<TContractState> {
    fn initiate_bridge(
        ref self: TContractState,
        destination_chain: u32,
        amount: u256,
        recipient: felt252,
    ) -> u256;
    fn confirm_bridge(ref self: TContractState, transaction_id: u256, tx_hash: felt252);
    fn complete_bridge(ref self: TContractState, transaction_id: u256);
    fn fail_bridge(ref self: TContractState, transaction_id: u256, reason: felt252);
    
    fn add_supported_chain(
        ref self: TContractState,
        chain_id: u32,
        name: felt252,
        bridge_address: felt252,
        fee_multiplier: u256,
        daily_limit: u256,
    );
    fn update_chain_status(ref self: TContractState, chain_id: u32, is_active: bool);
    fn add_bridge_operator(ref self: TContractState, operator: ContractAddress);
    fn remove_bridge_operator(ref self: TContractState, operator: ContractAddress);
    fn pause(ref self: TContractState);
    fn unpause(ref self: TContractState);
    
    fn get_bridge_transaction(self: @TContractState, transaction_id: u256) -> CrossChainBridge::BridgeTransaction;
    fn get_chain_config(self: @TContractState, chain_id: u32) -> CrossChainBridge::ChainConfig;
    fn get_transaction_confirmations(self: @TContractState, transaction_id: u256) -> u32;
    fn is_chain_supported(self: @TContractState, chain_id: u32) -> bool;
    fn is_bridge_operator(self: @TContractState, operator: ContractAddress) -> bool;
    fn get_daily_volume(self: @TContractState, chain_id: u32, day: u64) -> u256;
    fn get_daily_limit(self: @TContractState, chain_id: u32) -> u256;
    fn get_total_locked(self: @TContractState) -> u256;
    fn is_paused(self: @TContractState) -> bool;
}

