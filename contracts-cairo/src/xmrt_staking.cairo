#[starknet::contract]
mod XMRTStaking {
use starknet::{ContractAddress, get_caller_address, get_block_timestamp, get_contract_address};
use openzeppelin::access::ownable::OwnableComponent;
use openzeppelin::upgrades::UpgradeableComponent;
use openzeppelin::upgrades::interface::IUpgradeable;
use openzeppelin::token::erc20::interface::{IERC20Dispatcher, IERC20DispatcherTrait};
use openzeppelin::security::reentrancyguard::ReentrancyGuardComponent;
use core::num::traits::Zero;

    component!(path: OwnableComponent, storage: ownable, event: OwnableEvent);
    component!(path: UpgradeableComponent, storage: upgradeable, event: UpgradeableEvent);
    component!(path: ReentrancyGuardComponent, storage: reentrancy_guard, event: ReentrancyGuardEvent);

    // Ownable
    #[abi(embed_v0)]
    impl OwnableMixinImpl = OwnableComponent::OwnableMixinImpl<ContractState>;
    impl OwnableInternalImpl = OwnableComponent::InternalImpl<ContractState>;

    // Upgradeable
    impl UpgradeableInternalImpl = UpgradeableComponent::InternalImpl<ContractState>;

    // ReentrancyGuard
    impl ReentrancyGuardInternalImpl = ReentrancyGuardComponent::InternalImpl<ContractState>;

    #[storage]
    struct Storage {
        #[substorage(v0)]
        ownable: OwnableComponent::Storage,
        #[substorage(v0)]
        upgradeable: UpgradeableComponent::Storage,
        #[substorage(v0)]
        reentrancy_guard: ReentrancyGuardComponent::Storage,
        // Staking specific storage
        xmrt_token: ContractAddress,
        reward_rate: u256, // Rewards per second per token staked
        last_update_time: u64,
        reward_per_token_stored: u256,
        total_staked: u256,
        paused: bool,
        minimum_stake: u256,
        lock_period: u64, // Lock period in seconds
        // User specific data
        user_reward_per_token_paid: Map<ContractAddress, u256>,
        rewards: Map<ContractAddress, u256>,
        balances: Map<ContractAddress, u256>,
        stake_timestamps: Map<ContractAddress, u64>,
        // Pool configuration
        reward_duration: u64,
        period_finish: u64,
        reward_pool: u256,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        #[flat]
        OwnableEvent: OwnableComponent::Event,
        #[flat]
        UpgradeableEvent: UpgradeableComponent::Event,
        #[flat]
        ReentrancyGuardEvent: ReentrancyGuardComponent::Event,
        // Custom events
        Staked: Staked,
        Withdrawn: Withdrawn,
        RewardPaid: RewardPaid,
        RewardAdded: RewardAdded,
        Paused: Paused,
        Unpaused: Unpaused,
        RewardRateUpdated: RewardRateUpdated,
        MinimumStakeUpdated: MinimumStakeUpdated,
        LockPeriodUpdated: LockPeriodUpdated,
    }

    #[derive(Drop, starknet::Event)]
    struct Staked {
        #[key]
        user: ContractAddress,
        amount: u256,
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
    }

    #[derive(Drop, starknet::Event)]
    struct Paused {}

    #[derive(Drop, starknet::Event)]
    struct Unpaused {}

    #[derive(Drop, starknet::Event)]
    struct RewardRateUpdated {
        new_rate: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct MinimumStakeUpdated {
        new_minimum: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct LockPeriodUpdated {
        new_period: u64,
    }

    pub mod Errors {
        pub const PAUSED: felt252 = 'Contract is paused';
        pub const ZERO_ADDRESS: felt252 = 'Zero address not allowed';
        pub const ZERO_AMOUNT: felt252 = 'Zero amount not allowed';
        pub const INSUFFICIENT_BALANCE: felt252 = 'Insufficient balance';
        pub const BELOW_MINIMUM_STAKE: felt252 = 'Below minimum stake';
        pub const TOKENS_LOCKED: felt252 = 'Tokens still locked';
        pub const TRANSFER_FAILED: felt252 = 'Transfer failed';
        pub const INSUFFICIENT_REWARD_POOL: felt252 = 'Insufficient reward pool';
        pub const INVALID_DURATION: felt252 = 'Invalid duration';
    }

    #[constructor]
    fn constructor(
        ref self: ContractState,
        owner: ContractAddress,
        xmrt_token: ContractAddress,
        reward_rate: u256,
        minimum_stake: u256,
        lock_period: u64,
        reward_duration: u64
    ) {
        self.ownable.initializer(owner);
        self.xmrt_token.write(xmrt_token);
        self.reward_rate.write(reward_rate);
        self.minimum_stake.write(minimum_stake);
        self.lock_period.write(lock_period);
        self.reward_duration.write(reward_duration);
        self.last_update_time.write(get_block_timestamp());
        self.paused.write(false);
    }

    #[abi(embed_v0)]
    impl UpgradeableImpl of IUpgradeable<ContractState> {
        fn upgrade(ref self: ContractState, new_class_hash: starknet::ClassHash) {
            self.ownable.assert_only_owner();
            self.upgradeable._upgrade(new_class_hash);
        }
    }

    #[abi(embed_v0)]
    impl XMRTStakingImpl of super::IXMRTStaking<ContractState> {
        fn stake(ref self: ContractState, amount: u256) {
            self.reentrancy_guard.start();
            self._assert_not_paused();
            assert(amount > 0, Errors::ZERO_AMOUNT);
            assert(amount >= self.minimum_stake.read(), Errors::BELOW_MINIMUM_STAKE);
            
            let caller = get_caller_address();
            self._update_reward(caller);
            
            // Transfer tokens from user to contract
            let token = IERC20Dispatcher { contract_address: self.xmrt_token.read() };
            let success = token.transfer_from(caller, get_contract_address(), amount);
            assert(success, Errors::TRANSFER_FAILED);
            
            // Update user balance and total staked
            let current_balance = self.balances.read(caller);
            self.balances.write(caller, current_balance + amount);
            
            let current_total = self.total_staked.read();
            self.total_staked.write(current_total + amount);
            
            // Record stake timestamp
            self.stake_timestamps.write(caller, get_block_timestamp());
            
            self.emit(Staked { user: caller, amount });
            self.reentrancy_guard.end();
        }

        fn withdraw(ref self: ContractState, amount: u256) {
            self.reentrancy_guard.start();
            self._assert_not_paused();
            assert(amount > 0, Errors::ZERO_AMOUNT);
            
            let caller = get_caller_address();
            let user_balance = self.balances.read(caller);
            assert(user_balance >= amount, Errors::INSUFFICIENT_BALANCE);
            
            // Check if lock period has passed
            let stake_time = self.stake_timestamps.read(caller);
            let current_time = get_block_timestamp();
            let lock_period = self.lock_period.read();
            assert(current_time >= stake_time + lock_period, Errors::TOKENS_LOCKED);
            
            self._update_reward(caller);
            
            // Update balances
            self.balances.write(caller, user_balance - amount);
            let current_total = self.total_staked.read();
            self.total_staked.write(current_total - amount);
            
            // Transfer tokens back to user
            let token = IERC20Dispatcher { contract_address: self.xmrt_token.read() };
            let success = token.transfer(caller, amount);
            assert(success, Errors::TRANSFER_FAILED);
            
            self.emit(Withdrawn { user: caller, amount });
            self.reentrancy_guard.end();
        }

        fn claim_reward(ref self: ContractState) {
            self.reentrancy_guard.start();
            self._assert_not_paused();
            
            let caller = get_caller_address();
            self._update_reward(caller);
            
            let reward = self.rewards.read(caller);
            if reward > 0 {
                self.rewards.write(caller, 0);
                
                // Check if reward pool has sufficient balance
                let reward_pool = self.reward_pool.read();
                assert(reward_pool >= reward, Errors::INSUFFICIENT_REWARD_POOL);
                self.reward_pool.write(reward_pool - reward);
                
                // Transfer reward to user
                let token = IERC20Dispatcher { contract_address: self.xmrt_token.read() };
                let success = token.transfer(caller, reward);
                assert(success, Errors::TRANSFER_FAILED);
                
                self.emit(RewardPaid { user: caller, reward });
            }
            self.reentrancy_guard.end();
        }

        fn add_reward(ref self: ContractState, reward: u256) {
            self.ownable.assert_only_owner();
            assert(reward > 0, Errors::ZERO_AMOUNT);
            
            self._update_reward(Zero::zero());
            
            let current_time = get_block_timestamp();
            let duration = self.reward_duration.read();
            
            if current_time >= self.period_finish.read() {
                self.reward_rate.write(reward / duration.into());
            } else {
                let remaining = self.period_finish.read() - current_time;
                let leftover = remaining.into() * self.reward_rate.read();
                self.reward_rate.write((reward + leftover) / duration.into());
            }
            
            self.last_update_time.write(current_time);
            self.period_finish.write(current_time + duration);
            
            // Add to reward pool
            let current_pool = self.reward_pool.read();
            self.reward_pool.write(current_pool + reward);
            
            self.emit(RewardAdded { reward });
        }

        fn pause(ref self: ContractState) {
            self.ownable.assert_only_owner();
            self.paused.write(true);
            self.emit(Paused {});
        }

        fn unpause(ref self: ContractState) {
            self.ownable.assert_only_owner();
            self.paused.write(false);
            self.emit(Unpaused {});
        }

        fn set_reward_rate(ref self: ContractState, new_rate: u256) {
            self.ownable.assert_only_owner();
            self.reward_rate.write(new_rate);
            self.emit(RewardRateUpdated { new_rate });
        }

        fn set_minimum_stake(ref self: ContractState, new_minimum: u256) {
            self.ownable.assert_only_owner();
            self.minimum_stake.write(new_minimum);
            self.emit(MinimumStakeUpdated { new_minimum });
        }

        fn set_lock_period(ref self: ContractState, new_period: u64) {
            self.ownable.assert_only_owner();
            self.lock_period.write(new_period);
            self.emit(LockPeriodUpdated { new_period });
        }

        // View functions
        fn balance_of(self: @ContractState, account: ContractAddress) -> u256 {
            self.balances.read(account)
        }

        fn earned(self: @ContractState, account: ContractAddress) -> u256 {
            let balance = self.balances.read(account);
            let reward_per_token = self._reward_per_token();
            let user_reward_per_token_paid = self.user_reward_per_token_paid.read(account);
            let rewards = self.rewards.read(account);
            
            balance * (reward_per_token - user_reward_per_token_paid) / 1000000000000000000 + rewards
        }

        fn total_staked(self: @ContractState) -> u256 {
            self.total_staked.read()
        }

        fn reward_rate(self: @ContractState) -> u256 {
            self.reward_rate.read()
        }

        fn minimum_stake(self: @ContractState) -> u256 {
            self.minimum_stake.read()
        }

        fn lock_period(self: @ContractState) -> u64 {
            self.lock_period.read()
        }

        fn is_paused(self: @ContractState) -> bool {
            self.paused.read()
        }

        fn reward_pool(self: @ContractState) -> u256 {
            self.reward_pool.read()
        }

        fn stake_timestamp(self: @ContractState, account: ContractAddress) -> u64 {
            self.stake_timestamps.read(account)
        }

        fn can_withdraw(self: @ContractState, account: ContractAddress) -> bool {
            let stake_time = self.stake_timestamps.read(account);
            let current_time = get_block_timestamp();
            let lock_period = self.lock_period.read();
            current_time >= stake_time + lock_period
        }
    }

    #[generate_trait]
    impl InternalImpl of InternalTrait {
        fn _assert_not_paused(self: @ContractState) {
            assert(!self.paused.read(), Errors::PAUSED);
        }

        fn _reward_per_token(self: @ContractState) -> u256 {
            let total_staked = self.total_staked.read();
            if total_staked == 0 {
                return self.reward_per_token_stored.read();
            }
            
            let current_time = get_block_timestamp();
            let last_update = self.last_update_time.read();
            let period_finish = self.period_finish.read();
            let applicable_time = if current_time < period_finish { current_time } else { period_finish };
            
            if applicable_time <= last_update {
                return self.reward_per_token_stored.read();
            }
            
            let time_diff = applicable_time - last_update;
            let reward_rate = self.reward_rate.read();
            
            self.reward_per_token_stored.read() + 
                (time_diff.into() * reward_rate * 1000000000000000000) / total_staked
        }

        fn _update_reward(ref self: ContractState, account: ContractAddress) {
            let reward_per_token = self._reward_per_token();
            self.reward_per_token_stored.write(reward_per_token);
            self.last_update_time.write(get_block_timestamp());
            
            if !account.is_zero() {
                let earned = self.earned(account);
                self.rewards.write(account, earned);
                self.user_reward_per_token_paid.write(account, reward_per_token);
            }
        }
    }
}

#[starknet::interface]
trait IXMRTStaking<TContractState> {
    fn stake(ref self: TContractState, amount: u256);
    fn withdraw(ref self: TContractState, amount: u256);
    fn claim_reward(ref self: TContractState);
    fn add_reward(ref self: TContractState, reward: u256);
    fn pause(ref self: TContractState);
    fn unpause(ref self: TContractState);
    fn set_reward_rate(ref self: TContractState, new_rate: u256);
    fn set_minimum_stake(ref self: TContractState, new_minimum: u256);
    fn set_lock_period(ref self: TContractState, new_period: u64);
    
    // View functions
    fn balance_of(self: @TContractState, account: ContractAddress) -> u256;
    fn earned(self: @TContractState, account: ContractAddress) -> u256;
    fn total_staked(self: @TContractState) -> u256;
    fn reward_rate(self: @TContractState) -> u256;
    fn minimum_stake(self: @TContractState) -> u256;
    fn lock_period(self: @TContractState) -> u64;
    fn is_paused(self: @TContractState) -> bool;
    fn reward_pool(self: @TContractState) -> u256;
    fn stake_timestamp(self: @TContractState, account: ContractAddress) -> u64;
    fn can_withdraw(self: @TContractState, account: ContractAddress) -> bool;
}

