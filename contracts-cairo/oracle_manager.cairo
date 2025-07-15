/// @title OracleManager
/// @notice This contract manages price feeds and oracle data for the XMRT ecosystem

#[starknet::contract]
mod OracleManager {
    use starknet::{ContractAddress, get_caller_address, get_block_timestamp};
    use core::array::ArrayTrait;
    use core::traits::Into;

    #[storage]
    struct Storage {
        // Access control
        admin: ContractAddress,
        oracle_operators: LegacyMap<ContractAddress, bool>,
        
        // Price feeds
        price_feeds: LegacyMap<felt252, PriceFeed>,
        supported_assets: LegacyMap<felt252, bool>,
        
        // Oracle data
        oracle_count: u32,
        oracles: LegacyMap<u32, Oracle>,
        oracle_data: LegacyMap<(u32, felt252), OracleData>,
        
        // Aggregation settings
        min_oracles_required: u32,
        max_price_deviation: u256, // Basis points (10000 = 100%)
        price_staleness_threshold: u64, // Seconds
        
        // Emergency controls
        paused: bool,
        emergency_prices: LegacyMap<felt252, u256>,
        
        // Historical data
        price_history: LegacyMap<(felt252, u64), u256>, // (asset, timestamp) -> price
        price_update_count: LegacyMap<felt252, u256>,
    }

    #[derive(Drop, Serde, starknet::Store)]
    struct PriceFeed {
        asset: felt252,
        price: u256,
        last_updated: u64,
        decimals: u8,
        is_active: bool,
        confidence: u256, // Basis points (10000 = 100%)
        source_count: u32,
    }

    #[derive(Drop, Serde, starknet::Store)]
    struct Oracle {
        id: u32,
        operator: ContractAddress,
        name: felt252,
        is_active: bool,
        reputation_score: u256,
        total_updates: u256,
        successful_updates: u256,
        last_update: u64,
    }

    #[derive(Drop, Serde, starknet::Store)]
    struct OracleData {
        oracle_id: u32,
        asset: felt252,
        price: u256,
        timestamp: u64,
        confidence: u256,
        signature: felt252, // Simplified signature representation
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        PriceUpdated: PriceUpdated,
        OracleAdded: OracleAdded,
        OracleUpdated: OracleUpdated,
        OracleRemoved: OracleRemoved,
        AssetAdded: AssetAdded,
        AssetUpdated: AssetUpdated,
        EmergencyPriceSet: EmergencyPriceSet,
        Paused: Paused,
        Unpaused: Unpaused,
    }

    #[derive(Drop, starknet::Event)]
    struct PriceUpdated {
        #[key]
        asset: felt252,
        price: u256,
        confidence: u256,
        timestamp: u64,
        source_count: u32,
    }

    #[derive(Drop, starknet::Event)]
    struct OracleAdded {
        #[key]
        oracle_id: u32,
        operator: ContractAddress,
        name: felt252,
    }

    #[derive(Drop, starknet::Event)]
    struct OracleUpdated {
        #[key]
        oracle_id: u32,
        is_active: bool,
        reputation_score: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct OracleRemoved {
        #[key]
        oracle_id: u32,
    }

    #[derive(Drop, starknet::Event)]
    struct AssetAdded {
        #[key]
        asset: felt252,
        decimals: u8,
    }

    #[derive(Drop, starknet::Event)]
    struct AssetUpdated {
        #[key]
        asset: felt252,
        is_active: bool,
    }

    #[derive(Drop, starknet::Event)]
    struct EmergencyPriceSet {
        #[key]
        asset: felt252,
        price: u256,
        admin: ContractAddress,
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
        min_oracles_required: u32,
        max_price_deviation: u256,
        price_staleness_threshold: u64,
    ) {
        self.admin.write(admin);
        self.min_oracles_required.write(min_oracles_required);
        self.max_price_deviation.write(max_price_deviation);
        self.price_staleness_threshold.write(price_staleness_threshold);
        self.oracle_count.write(0);
        self.paused.write(false);
        
        // Add admin as initial oracle operator
        self.oracle_operators.write(admin, true);
    }

    #[abi(embed_v0)]
    impl OracleManagerImpl of IOracleManager<ContractState> {
        fn submit_price_data(
            ref self: ContractState,
            oracle_id: u32,
            asset: felt252,
            price: u256,
            confidence: u256,
            signature: felt252,
        ) {
            self._require_not_paused();
            self._only_oracle_operator();
            
            let oracle = self.oracles.read(oracle_id);
            assert(oracle.id != 0, 'Oracle does not exist');
            assert(oracle.is_active, 'Oracle is not active');
            assert(oracle.operator == get_caller_address(), 'Not oracle operator');
            assert(self.supported_assets.read(asset), 'Asset not supported');
            assert(confidence <= 10000, 'Invalid confidence value');
            
            let current_time = get_block_timestamp();
            
            // Store oracle data
            let oracle_data = OracleData {
                oracle_id,
                asset,
                price,
                timestamp: current_time,
                confidence,
                signature,
            };
            
            self.oracle_data.write((oracle_id, asset), oracle_data);
            
            // Update oracle statistics
            let mut updated_oracle = oracle;
            updated_oracle.total_updates += 1;
            updated_oracle.last_update = current_time;
            self.oracles.write(oracle_id, updated_oracle);
            
            // Aggregate price data
            self._aggregate_price_data(asset);
        }

        fn add_oracle(
            ref self: ContractState,
            operator: ContractAddress,
            name: felt252,
        ) -> u32 {
            self._only_admin();
            
            let oracle_id = self.oracle_count.read() + 1;
            self.oracle_count.write(oracle_id);
            
            let oracle = Oracle {
                id: oracle_id,
                operator,
                name,
                is_active: true,
                reputation_score: 10000, // Start with 100% reputation
                total_updates: 0,
                successful_updates: 0,
                last_update: 0,
            };
            
            self.oracles.write(oracle_id, oracle);
            self.oracle_operators.write(operator, true);
            
            self.emit(OracleAdded {
                oracle_id,
                operator,
                name,
            });
            
            oracle_id
        }

        fn update_oracle_status(ref self: ContractState, oracle_id: u32, is_active: bool) {
            self._only_admin();
            
            let mut oracle = self.oracles.read(oracle_id);
            assert(oracle.id != 0, 'Oracle does not exist');
            
            oracle.is_active = is_active;
            self.oracles.write(oracle_id, oracle);
            
            self.emit(OracleUpdated {
                oracle_id,
                is_active,
                reputation_score: oracle.reputation_score,
            });
        }

        fn add_supported_asset(ref self: ContractState, asset: felt252, decimals: u8) {
            self._only_admin();
            
            self.supported_assets.write(asset, true);
            
            // Initialize price feed
            let price_feed = PriceFeed {
                asset,
                price: 0,
                last_updated: 0,
                decimals,
                is_active: true,
                confidence: 0,
                source_count: 0,
            };
            
            self.price_feeds.write(asset, price_feed);
            
            self.emit(AssetAdded { asset, decimals });
        }

        fn update_asset_status(ref self: ContractState, asset: felt252, is_active: bool) {
            self._only_admin();
            
            assert(self.supported_assets.read(asset), 'Asset not supported');
            
            let mut price_feed = self.price_feeds.read(asset);
            price_feed.is_active = is_active;
            self.price_feeds.write(asset, price_feed);
            
            self.emit(AssetUpdated { asset, is_active });
        }

        fn set_emergency_price(ref self: ContractState, asset: felt252, price: u256) {
            self._only_admin();
            assert(self.supported_assets.read(asset), 'Asset not supported');
            
            self.emergency_prices.write(asset, price);
            
            self.emit(EmergencyPriceSet {
                asset,
                price,
                admin: get_caller_address(),
            });
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

        fn get_price(self: @ContractState, asset: felt252) -> (u256, u64, u256) {
            let price_feed = self.price_feeds.read(asset);
            assert(price_feed.is_active, 'Asset not active');
            
            let current_time = get_block_timestamp();
            let staleness_threshold = self.price_staleness_threshold.read();
            
            // Check if price is stale
            if current_time - price_feed.last_updated > staleness_threshold {
                // Return emergency price if available
                let emergency_price = self.emergency_prices.read(asset);
                if emergency_price > 0 {
                    return (emergency_price, current_time, 5000); // 50% confidence for emergency price
                }
                assert(false, 'Price data is stale');
            }
            
            (price_feed.price, price_feed.last_updated, price_feed.confidence)
        }

        fn get_price_feed(self: @ContractState, asset: felt252) -> PriceFeed {
            self.price_feeds.read(asset)
        }

        fn get_oracle(self: @ContractState, oracle_id: u32) -> Oracle {
            self.oracles.read(oracle_id)
        }

        fn get_oracle_data(self: @ContractState, oracle_id: u32, asset: felt252) -> OracleData {
            self.oracle_data.read((oracle_id, asset))
        }

        fn get_historical_price(self: @ContractState, asset: felt252, timestamp: u64) -> u256 {
            self.price_history.read((asset, timestamp))
        }

        fn is_asset_supported(self: @ContractState, asset: felt252) -> bool {
            self.supported_assets.read(asset)
        }

        fn is_oracle_operator(self: @ContractState, operator: ContractAddress) -> bool {
            self.oracle_operators.read(operator)
        }

        fn get_oracle_count(self: @ContractState) -> u32 {
            self.oracle_count.read()
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

        fn _only_oracle_operator(self: @ContractState) {
            assert(self.oracle_operators.read(get_caller_address()), 'Only oracle operator');
        }

        fn _require_not_paused(self: @ContractState) {
            assert(!self.paused.read(), 'Contract is paused');
        }

        fn _aggregate_price_data(ref self: ContractState, asset: felt252) {
            let current_time = get_block_timestamp();
            let oracle_count = self.oracle_count.read();
            let min_oracles = self.min_oracles_required.read();
            
            let mut valid_prices: Array<u256> = ArrayTrait::new();
            let mut total_confidence = 0_u256;
            let mut active_oracles = 0_u32;
            
            // Collect valid price data from all oracles
            let mut i = 1_u32;
            loop {
                if i > oracle_count {
                    break;
                }
                
                let oracle = self.oracles.read(i);
                if oracle.is_active {
                    let oracle_data = self.oracle_data.read((i, asset));
                    
                    // Check if data is recent enough
                    if current_time - oracle_data.timestamp <= 300 { // 5 minutes
                        valid_prices.append(oracle_data.price);
                        total_confidence += oracle_data.confidence;
                        active_oracles += 1;
                    }
                }
                
                i += 1;
            };
            
            // Require minimum number of oracles
            assert(active_oracles >= min_oracles, 'Insufficient oracle data');
            
            // Calculate median price (simplified implementation)
            let aggregated_price = self._calculate_median_price(valid_prices);
            let average_confidence = total_confidence / active_oracles.into();
            
            // Update price feed
            let mut price_feed = self.price_feeds.read(asset);
            price_feed.price = aggregated_price;
            price_feed.last_updated = current_time;
            price_feed.confidence = average_confidence;
            price_feed.source_count = active_oracles;
            self.price_feeds.write(asset, price_feed);
            
            // Store historical price
            self.price_history.write((asset, current_time), aggregated_price);
            
            // Update price update count
            let update_count = self.price_update_count.read(asset);
            self.price_update_count.write(asset, update_count + 1);
            
            self.emit(PriceUpdated {
                asset,
                price: aggregated_price,
                confidence: average_confidence,
                timestamp: current_time,
                source_count: active_oracles,
            });
        }

        fn _calculate_median_price(self: @ContractState, mut prices: Array<u256>) -> u256 {
            let len = prices.len();
            if len == 0 {
                return 0;
            }
            
            // Simple median calculation (in practice, would need proper sorting)
            // For now, return the first price as a placeholder
            *prices.at(0)
        }
    }
}

#[starknet::interface]
trait IOracleManager<TContractState> {
    fn submit_price_data(
        ref self: TContractState,
        oracle_id: u32,
        asset: felt252,
        price: u256,
        confidence: u256,
        signature: felt252,
    );
    fn add_oracle(ref self: TContractState, operator: ContractAddress, name: felt252) -> u32;
    fn update_oracle_status(ref self: TContractState, oracle_id: u32, is_active: bool);
    fn add_supported_asset(ref self: TContractState, asset: felt252, decimals: u8);
    fn update_asset_status(ref self: TContractState, asset: felt252, is_active: bool);
    fn set_emergency_price(ref self: TContractState, asset: felt252, price: u256);
    fn pause(ref self: TContractState);
    fn unpause(ref self: TContractState);
    
    fn get_price(self: @TContractState, asset: felt252) -> (u256, u64, u256);
    fn get_price_feed(self: @TContractState, asset: felt252) -> OracleManager::PriceFeed;
    fn get_oracle(self: @TContractState, oracle_id: u32) -> OracleManager::Oracle;
    fn get_oracle_data(self: @TContractState, oracle_id: u32, asset: felt252) -> OracleManager::OracleData;
    fn get_historical_price(self: @TContractState, asset: felt252, timestamp: u64) -> u256;
    fn is_asset_supported(self: @TContractState, asset: felt252) -> bool;
    fn is_oracle_operator(self: @TContractState, operator: ContractAddress) -> bool;
    fn get_oracle_count(self: @TContractState) -> u32;
    fn is_paused(self: @TContractState) -> bool;
}

