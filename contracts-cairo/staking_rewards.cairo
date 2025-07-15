/// @title StakingRewards
/// @notice This contract manages staking rewards and incentives for XMRT token holders

#[starknet::contract]
mod StakingRewards {
    use starknet::{ContractAddress, get_caller_address, get_block_timestamp};
    use core::array::ArrayTrait;
    use core::traits::Into;

    #[storage]
    struct Storage {
        // Contract configuration
        admin: ContractAddress,
        xmrt_token: ContractAddress,
        rewards_token: ContractAddress,
        
        // Staking parameters
        reward_rate: u256,
        reward_duration: u64,
        finish_at: u64,
        updated_at: u64,
        reward_per_token_stored: u256,
        
        // User data
        user_reward_per_token_paid: LegacyMap<ContractAddress, u256>,
        rewards: LegacyMap<ContractAddress, u256>,
        balances: LegacyMap<ContractAddress, u256>,
        
        // Global state
        total_supply: u256,
        
        // Staking tiers and multipliers
        tier_thresholds: LegacyMap<u8, u256>,
        tier_multipliers: LegacyMap<u8, u256>,
        user_tiers: LegacyMap<ContractAddress, u8>,
        
        // Lock periods
        lock_periods: LegacyMap<u8, u64>,
        user_lock_end: LegacyMap<ContractAddress, u64>,
        
        // Emergency controls
        paused: bool,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        Staked: Staked,
        Withdrawn: Withdrawn,
        RewardPaid: RewardPaid,
        RewardAdded: RewardAdded,
        TierUpdated: TierUpdated,
        Paused: Paused,
        Unpaused: Unpaused,
    }

    #[derive(Drop, starknet::Event)]
    struct Staked {
        #[key]
        user: ContractAddress,
        amount: u256,
        tier: u8,
        lock_end: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct Withdrawn {
        #[key]
        user: ContractAddress,
        amount: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct RewardPaid {
        #[key]
        user: ContractAddress,
        reward: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct RewardAdded {
        reward: u256,
        duration: u64,
    }

    #[derive(Drop, starknet::Event)]
    struct TierUpdated {
        #[key]
        user: ContractAddress,
        old_tier: u8,
        new_tier: u8,
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
        rewards_token: ContractAddress,
    ) {
        self.admin.write(admin);
        self.xmrt_token.write(xmrt_token);
        self.rewards_token.write(rewards_token);
        self.paused.write(false);
        
        // Initialize tier thresholds (in XMRT tokens)
        self.tier_thresholds.write(1, 1000 * 1000000000000000000); // 1,000 XMRT
        self.tier_thresholds.write(2, 5000 * 1000000000000000000); // 5,000 XMRT
        self.tier_thresholds.write(3, 10000 * 1000000000000000000); // 10,000 XMRT
        self.tier_thresholds.write(4, 50000 * 1000000000000000000); // 50,000 XMRT
        
        // Initialize tier multipliers (basis points, 10000 = 100%)
        self.tier_multipliers.write(0, 10000); // 100% (base tier)
        self.tier_multipliers.write(1, 12000); // 120%
        self.tier_multipliers.write(2, 15000); // 150%
        self.tier_multipliers.write(3, 20000); // 200%
        self.tier_multipliers.write(4, 30000); // 300%
        
        // Initialize lock periods (in seconds)
        self.lock_periods.write(0, 0); // No lock
        self.lock_periods.write(1, 30 * 24 * 60 * 60); // 30 days
        self.lock_periods.write(2, 90 * 24 * 60 * 60); // 90 days
        self.lock_periods.write(3, 180 * 24 * 60 * 60); // 180 days
        self.lock_periods.write(4, 365 * 24 * 60 * 60); // 365 days
    }

    #[abi(embed_v0)]
    impl StakingRewardsImpl of IStakingRewards<ContractState> {
        fn stake(ref self: ContractState, amount: u256, lock_tier: u8) {
            self._require_not_paused();
            assert(amount > 0, 'Cannot stake 0');
            assert(lock_tier <= 4, 'Invalid lock tier');
            
            let caller = get_caller_address();
            self._update_reward(caller);
            
            // Transfer tokens from user to contract
            // In a real implementation, this would call the XMRT token contract
            
            let current_balance = self.balances.read(caller);
            self.balances.write(caller, current_balance + amount);
            
            let current_total = self.total_supply.read();
            self.total_supply.write(current_total + amount);
            
            // Set lock period
            let lock_duration = self.lock_periods.read(lock_tier);
            let lock_end = get_block_timestamp() + lock_duration;
            self.user_lock_end.write(caller, lock_end);
            
            // Update user tier based on total staked amount
            let new_balance = current_balance + amount;
            let old_tier = self.user_tiers.read(caller);
            let new_tier = self._calculate_tier(new_balance);
            
            if new_tier != old_tier {
                self.user_tiers.write(caller, new_tier);
                self.emit(TierUpdated {
                    user: caller,
                    old_tier,
                    new_tier,
                });
            }
            
            self.emit(Staked {
                user: caller,
                amount,
                tier: new_tier,
                lock_end,
            });
        }

        fn withdraw(ref self: ContractState, amount: u256) {
            self._require_not_paused();
            assert(amount > 0, 'Cannot withdraw 0');
            
            let caller = get_caller_address();
            let current_balance = self.balances.read(caller);
            assert(current_balance >= amount, 'Insufficient balance');
            
            // Check if lock period has ended
            let lock_end = self.user_lock_end.read(caller);
            assert(get_block_timestamp() >= lock_end, 'Tokens still locked');
            
            self._update_reward(caller);
            
            self.balances.write(caller, current_balance - amount);
            
            let current_total = self.total_supply.read();
            self.total_supply.write(current_total - amount);
            
            // Update user tier
            let new_balance = current_balance - amount;
            let old_tier = self.user_tiers.read(caller);
            let new_tier = self._calculate_tier(new_balance);
            
            if new_tier != old_tier {
                self.user_tiers.write(caller, new_tier);
                self.emit(TierUpdated {
                    user: caller,
                    old_tier,
                    new_tier,
                });
            }
            
            // Transfer tokens back to user
            // In a real implementation, this would call the XMRT token contract
            
            self.emit(Withdrawn {
                user: caller,
                amount,
            });
        }

        fn claim_reward(ref self: ContractState) {
            self._require_not_paused();
            let caller = get_caller_address();
            
            self._update_reward(caller);
            
            let reward = self.rewards.read(caller);
            if reward > 0 {
                self.rewards.write(caller, 0);
                
                // Transfer reward tokens to user
                // In a real implementation, this would call the rewards token contract
                
                self.emit(RewardPaid {
                    user: caller,
                    reward,
                });
            }
        }

        fn add_reward(ref self: ContractState, reward: u256, duration: u64) {
            self._only_admin();
            self._update_reward(starknet::contract_address_const::<0>());
            
            let current_time = get_block_timestamp();
            
            if current_time >= self.finish_at.read() {
                self.reward_rate.write(reward / duration.into());
            } else {
                let remaining_time = self.finish_at.read() - current_time;
                let leftover = remaining_time.into() * self.reward_rate.read();
                self.reward_rate.write((reward + leftover) / duration.into());
            }
            
            self.reward_duration.write(duration);
            self.finish_at.write(current_time + duration);
            self.updated_at.write(current_time);
            
            self.emit(RewardAdded { reward, duration });
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

        fn balance_of(self: @ContractState, account: ContractAddress) -> u256 {
            self.balances.read(account)
        }

        fn earned(self: @ContractState, account: ContractAddress) -> u256 {
            let balance = self.balances.read(account);
            let user_tier = self.user_tiers.read(account);
            let multiplier = self.tier_multipliers.read(user_tier);
            
            let base_earned = balance * (self._reward_per_token() - self.user_reward_per_token_paid.read(account)) / 1000000000000000000;
            let tier_bonus = base_earned * multiplier / 10000;
            
            self.rewards.read(account) + tier_bonus
        }

        fn reward_per_token(self: @ContractState) -> u256 {
            self._reward_per_token()
        }

        fn get_user_tier(self: @ContractState, account: ContractAddress) -> u8 {
            self.user_tiers.read(account)
        }

        fn get_lock_end(self: @ContractState, account: ContractAddress) -> u64 {
            self.user_lock_end.read(account)
        }

        fn get_tier_threshold(self: @ContractState, tier: u8) -> u256 {
            self.tier_thresholds.read(tier)
        }

        fn get_tier_multiplier(self: @ContractState, tier: u8) -> u256 {
            self.tier_multipliers.read(tier)
        }

        fn total_supply(self: @ContractState) -> u256 {
            self.total_supply.read()
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

        fn _require_not_paused(self: @ContractState) {
            assert(!self.paused.read(), 'Contract is paused');
        }

        fn _reward_per_token(self: @ContractState) -> u256 {
            let total_supply = self.total_supply.read();
            if total_supply == 0 {
                return self.reward_per_token_stored.read();
            }
            
            let current_time = get_block_timestamp();
            let last_time_applicable = if current_time < self.finish_at.read() {
                current_time
            } else {
                self.finish_at.read()
            };
            
            let time_diff = last_time_applicable - self.updated_at.read();
            let reward_per_token_increase = time_diff.into() * self.reward_rate.read() * 1000000000000000000 / total_supply;
            
            self.reward_per_token_stored.read() + reward_per_token_increase
        }

        fn _update_reward(ref self: ContractState, account: ContractAddress) {
            let new_reward_per_token = self._reward_per_token();
            self.reward_per_token_stored.write(new_reward_per_token);
            self.updated_at.write(get_block_timestamp());
            
            if account != starknet::contract_address_const::<0>() {
                let earned_amount = self.earned(account);
                self.rewards.write(account, earned_amount);
                self.user_reward_per_token_paid.write(account, new_reward_per_token);
            }
        }

        fn _calculate_tier(self: @ContractState, balance: u256) -> u8 {
            if balance >= self.tier_thresholds.read(4) {
                4
            } else if balance >= self.tier_thresholds.read(3) {
                3
            } else if balance >= self.tier_thresholds.read(2) {
                2
            } else if balance >= self.tier_thresholds.read(1) {
                1
            } else {
                0
            }
        }
    }
}

#[starknet::interface]
trait IStakingRewards<TContractState> {
    fn stake(ref self: TContractState, amount: u256, lock_tier: u8);
    fn withdraw(ref self: TContractState, amount: u256);
    fn claim_reward(ref self: TContractState);
    fn add_reward(ref self: TContractState, reward: u256, duration: u64);
    fn pause(ref self: TContractState);
    fn unpause(ref self: TContractState);
    
    fn balance_of(self: @TContractState, account: ContractAddress) -> u256;
    fn earned(self: @TContractState, account: ContractAddress) -> u256;
    fn reward_per_token(self: @TContractState) -> u256;
    fn get_user_tier(self: @TContractState, account: ContractAddress) -> u8;
    fn get_lock_end(self: @TContractState, account: ContractAddress) -> u64;
    fn get_tier_threshold(self: @TContractState, tier: u8) -> u256;
    fn get_tier_multiplier(self: @TContractState, tier: u8) -> u256;
    fn total_supply(self: @TContractState) -> u256;
    fn is_paused(self: @TContractState) -> bool;
}

